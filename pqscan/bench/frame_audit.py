"""Descriptive frame audit (protocol v1.0.4 Sec. 2; decision V7; R4-19 item 15).

On the 6 development/validation repositories: crypto-importing .py files (pyca or PyCryptodome) are put in a seeded
order per repository and taken round-robin across repositories until >= 60 eligible sites have been audited and every
repository has contributed >= 1 file. The owner reads each whole file blind to the pool and records every eligible
site; the script then checks pool membership at statement level.

Can estimate: the share of eligible sites in such files that the pool misses (development/validation only), with a
file-level cluster bootstrap interval (files resampled within repositories). Cannot estimate: recall in files
importing no supported library, recall in the test split, recall in Python projects generally, or errors the owner
and the pool share.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Sequence

import numpy as np

from .candidates import PYCA, PYCRYPTODOME, python_files, statement_starts

SEED = "20261113:frame"
MIN_ELIGIBLE, MIN_FILES_PER_REPO = 60, 1


def frame_files(repo_root: Path) -> list[str]:
    out = []
    for p in python_files(Path(repo_root)):
        t = p.read_text(encoding="utf-8", errors="replace")
        if PYCA.search(t) or PYCRYPTODOME.search(t):
            out.append(p.relative_to(repo_root).as_posix())
    return out


def frame_hash(frames: dict[str, list[str]]) -> str:
    return hashlib.sha256(json.dumps({r: sorted(v) for r, v in frames.items()}, sort_keys=True).encode()).hexdigest()


def worklist(frames: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Round-robin over repositories (ascending name), each repository's files in a seeded order."""
    orders = {r: sorted(v, key=lambda f: hashlib.sha256(f"{SEED}|{r}|{f}".encode()).hexdigest()) for r, v in frames.items()}
    out, i = [], 0
    while any(i < len(v) for v in orders.values()):
        for r in sorted(orders):
            if i < len(orders[r]):
                out.append((r, orders[r][i]))
        i += 1
    return out


def stop_reached(audited: Sequence[dict], repos: Sequence[str]) -> bool:
    """audited: [{"repo", "file", "eligible_lines": [...]}] in worklist order; repos: EVERY repository of the audit
    frame. Stop only when >= MIN_ELIGIBLE eligible sites have been audited AND every repository of the frame (not only
    those already visited) has contributed >= MIN_FILES_PER_REPO files (protocol v1.0.5 Sec. 2; fixed 2026-11-18:
    the earlier version checked only the repositories already audited)."""
    if not repos:
        raise ValueError("the audit frame's repositories must be given")
    return sum(len(a["eligible_lines"]) for a in audited) >= MIN_ELIGIBLE and all(
        sum(a["repo"] == r for a in audited) >= MIN_FILES_PER_REPO for r in repos)


def membership(audited: Sequence[dict], pools: dict[str, set[tuple[str, int]]], sources: dict[str, str]) -> list[dict]:
    """Per audited file: eligible sites found by the owner and whether each is in the candidate pool (statement level).
    `sources` maps (repo) -> repository root, used to map lines to statement starts."""
    out = []
    for a in audited:
        text = (Path(sources[a["repo"]]) / a["file"]).read_text(encoding="utf-8", errors="replace")
        starts = statement_starts(text)
        found = []
        for ln in a["eligible_lines"]:
            st = starts.get(int(ln), int(ln))
            found.append({"line": int(ln), "statement": st, "in_pool": (a["file"], st) in pools[a["repo"]]})
        out.append({"repo": a["repo"], "file": a["file"], "sites": found})
    return out


def missed_share(per_file: Sequence[dict], *, B: int = 2_000, seed: int = 20261113) -> dict:
    """Share of audited eligible sites missing from the pool, with a file-level cluster bootstrap 95% interval."""
    files = [(f["repo"], len(f["sites"]), sum(not s["in_pool"] for s in f["sites"])) for f in per_file]
    tot = sum(n for _, n, _ in files)
    miss = sum(m for _, _, m in files)
    if tot == 0:
        return {"eligible": 0, "missed": 0, "share": None, "ci95": (None, None)}
    by_repo = defaultdict(list)
    for r, n, m in files:
        by_repo[r].append((n, m))
    rng = np.random.default_rng(seed)
    shares = []
    for _ in range(B):
        nn = mm = 0
        for v in by_repo.values():
            for k in rng.integers(0, len(v), len(v)):
                nn += v[k][0]
                mm += v[k][1]
        shares.append(mm / nn if nn else 0.0)
    return {"eligible": tot, "missed": miss, "share": miss / tot, "files": len(files),
            "ci95": (float(np.quantile(shares, 0.025)), float(np.quantile(shares, 0.975))),
            "can_estimate": "share of eligible sites in crypto-importing files of the 6 development/validation repositories missed by the pool",
            "cannot_estimate": "recall outside such files, in the test split, or in Python projects generally; errors shared by the owner and the pool"}
