"""Reliability statistics (protocol v1.0.4 Sec. 3; decision V3; R4-19 item 13).

Three statistics, never called inter-annotator reliability: owner intra-rater consistency (re-label >= 14 days later),
owner-AI agreement, and AI repeat-run consistency.

Intra-rater sample, per phase: population N = every issued candidate of the phase with a final label (B0 and B1+;
annotator-added sites excluded); n = max(50, ceil(0.10 N)); allocated to repositories in proportion to N_r with at
least 3 each (largest remainder); within a repository half owner-final eligible and half ineligible (or all
available); seeded with "20261113:intra:<phase>"; presented in a new seeded order. The re-label may start only 14
days after the latest primary label among the sampled candidates. AI repeat-run sample: n = max(30, ceil(0.10 N_AI)),
seed "20261113:airepeat:<phase>".

Per field: n, raw agreement, Cohen's kappa with a bootstrap 95% CI (items resampled within repositories, 2,000
resamples), the confusion table, per-class specific agreement 2 n_ii / (row_i + col_i) for classes with >= 5 items
in either rating, and class prevalence. Rule: kappa(gt_role) point estimate < 0.60 -> Phase DV: revise the guide and
re-label before F1; Phase T: test results labelled exploratory.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
from collections import Counter, defaultdict
from typing import Sequence

import numpy as np

from .stats import cohen_kappa

FIELDS = ("eligible", "gt_role", "assessability", "possible_roles", "hybrid_component", "obvious_from_name",
          "evidence_needed", "key_provenance")
KAPPA_RULE = 0.60
GAP_DAYS = 14


def _u(seed: str, cid: str) -> str:
    return hashlib.sha256(f"{seed}|{cid}".encode("utf-8")).hexdigest()


def intra_sample(candidates: Sequence[dict], phase: str) -> dict:
    """candidates: dicts with candidate_id, repo, eligible (owner-final bool), annotator_added (optional).
    Returns {"n", "allocation", "sample" (presentation order)}."""
    seed = f"20261113:intra:{phase}"
    pop = [c for c in candidates if not c.get("annotator_added")]
    N = len(pop)
    n = max(50, math.ceil(0.10 * N))
    if N <= n:
        chosen = sorted(pop, key=lambda c: _u(seed + ":order", c["candidate_id"]))
        return {"N": N, "n": len(chosen), "allocation": dict(Counter(c["repo"] for c in chosen)), "sample": chosen}
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for c in pop:
        by_repo[c["repo"]].append(c)
    raw = {r: n * len(v) / N for r, v in by_repo.items()}
    alloc = {r: max(3, math.floor(x)) for r, x in raw.items()}
    remainder = sorted(by_repo, key=lambda r: (-(raw[r] - math.floor(raw[r])), r))
    i = 0
    while sum(alloc.values()) < n:
        alloc[remainder[i % len(remainder)]] += 1
        i += 1
    chosen = []
    for r, items in sorted(by_repo.items()):
        k = min(alloc[r], len(items))
        alloc[r] = k
        elig = sorted((c for c in items if c["eligible"] is True), key=lambda c: _u(seed, c["candidate_id"]))
        inel = sorted((c for c in items if c["eligible"] is not True), key=lambda c: _u(seed, c["candidate_id"]))
        half = k // 2
        take_e = min(len(elig), k - min(len(inel), k - half))
        take_i = min(len(inel), k - take_e)
        chosen += elig[:take_e] + inel[:take_i]
    chosen.sort(key=lambda c: _u(seed + ":order", c["candidate_id"]))
    return {"N": N, "n": len(chosen), "allocation": alloc, "sample": chosen}


def check_gap(primary_utc: Sequence[str], now_utc: str) -> None:
    """Refuse a re-label earlier than 14 days after the latest primary label of the sample."""
    parse = lambda s: _dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ" if s.count(":") == 2 else "%Y-%m-%dT%H:%MZ")
    latest = max(parse(s) for s in primary_utc)
    if parse(now_utc) - latest < _dt.timedelta(days=GAP_DAYS):
        raise ValueError(f"re-label refused: the latest sampled primary label is from {latest:%Y-%m-%d}; "
                         f"wait until {(latest + _dt.timedelta(days=GAP_DAYS)):%Y-%m-%d}")


def ai_repeat_sample(candidate_ids: Sequence[str], phase: str) -> list[str]:
    seed = f"20261113:airepeat:{phase}"
    n = max(30, math.ceil(0.10 * len(candidate_ids)))
    return sorted(candidate_ids, key=lambda c: _u(seed, c))[:n]


def _norm(v):
    return json.dumps(sorted(v) if isinstance(v, list) else v)


def field_agreement(a: Sequence, b: Sequence, repos: Sequence[str], *, B: int = 2_000, seed: int = 20261113) -> dict:
    """Agreement between two ratings of the same items for one field."""
    x, y = [_norm(v) for v in a], [_norm(v) for v in b]
    n = len(x)
    if n == 0:
        return {"n": 0}
    po = sum(i == j for i, j in zip(x, y)) / n
    kappa = cohen_kappa(x, y)
    cats = sorted(set(x) | set(y))
    conf = {ci: {cj: sum(1 for i, j in zip(x, y) if i == ci and j == cj) for cj in cats} for ci in cats}
    specific = {}
    for c in cats:
        row, col = sum(conf[c].values()), sum(conf[r][c] for r in cats)
        if row >= 5 or col >= 5:
            specific[c] = 2 * conf[c][c] / (row + col)
    prevalence = {c: (x.count(c) + y.count(c)) / (2 * n) for c in cats}
    rng = np.random.default_rng(seed)
    groups = defaultdict(list)
    for i, r in enumerate(repos):
        groups[r].append(i)
    ks = []
    for _ in range(B):
        idx = [g[k] for g in groups.values() for k in rng.integers(0, len(g), len(g))]
        xs, ys = [x[i] for i in idx], [y[i] for i in idx]
        ks.append(cohen_kappa(xs, ys) if len(set(xs) | set(ys)) > 1 else 1.0)
    return {"n": n, "raw_agreement": po, "kappa": kappa, "kappa_ci95": (float(np.quantile(ks, 0.025)), float(np.quantile(ks, 0.975))),
            "confusion": conf, "specific_agreement": specific, "prevalence": prevalence}


def agreement_report(first: Sequence[dict], second: Sequence[dict], *, phase: str, kind: str, B: int = 2_000) -> dict:
    """first/second: label envelopes of the same candidates (matched by candidate_id). kind: 'intra-rater',
    'owner-AI' or 'AI repeat-run'. AI 'insufficient_context' records are excluded and counted."""
    if kind not in ("intra-rater", "owner-AI", "AI repeat-run"):
        raise ValueError(kind)
    sec = {r["meta"]["candidate_id"]: r for r in second}
    pairs, excluded = [], 0
    for r in first:
        s = sec.get(r["meta"]["candidate_id"])
        if s is None:
            continue
        if any((z["meta"].get("ai") or {}).get("status") == "insufficient_context" for z in (r, s)):
            excluded += 1
            continue
        pairs.append((r, s))
    out = {"kind": kind, "phase": phase, "pairs": len(pairs), "excluded_insufficient_context": excluded, "fields": {}}
    for f in FIELDS:
        ab = [(p["site"][f], q["site"][f], p["site"].get("repo", "?")) for p, q in pairs if f in p["site"] and f in q["site"]]
        out["fields"][f] = field_agreement([u for u, _, _ in ab], [v for _, v, _ in ab], [r for _, _, r in ab], B=B)
    k = out["fields"]["gt_role"].get("kappa")
    if kind == "intra-rater" and k is not None and k < KAPPA_RULE:
        out["rule"] = ("kappa(gt_role) < 0.60: Phase DV -> revise the guide and re-label before F1" if phase == "DV"
                       else "kappa(gt_role) < 0.60: Phase T -> all test results labelled exploratory")
    else:
        out["rule"] = None
    return out
