"""Experiment E driver (protocol Sec. 6; run specification; owner decisions TA17 and TA22, revision v1.0.5-r6).

Pre-F1 infrastructure: written and tested on development, synthetic-dev and fixture data only. It REFUSES the test
split unless both freeze records (F1 `docs/freeze/pretest_freeze.json`, F2 `docs/freeze/label_freeze.json`) and both
tags exist, and it refuses the synthetic holdout for H4 until the F1 freeze record exists. It never fetches a
repository and never writes a label.

What it computes from judged rows (pqscan.bench.run format) and owner-final label records:
* F-B (confirmatory): H2-1, H2-3, H2-4 (+ H2-S outside the family) via matching.repository_result and
  h2.run_family. TA17: on the test split, exactly the seven manifest test repositories must be present, so K = 7
  (h2.py, part of the E30 calibration closure, is not changed).
* F-A (confirmatory): fa.run_fa against the registered baselines (run specification families.F-A.baselines).
* H1 (h1.py), H3 (h3.py), and H4 (h4_analysis.py, from Dataset A, separately).
* TA22: the unresolved bounding (protocol Sec. 5.6) for H2 and H3, and as reported sensitivities for F-A and H1:
  every analysis is recomputed with the label variants of reporting.label_variants; primary results use 'final'.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Mapping, Sequence

from ..baselines.simple import H2_COMPARISONS
from . import fa, h1, h2, h3, h4_analysis
from .judge import judge, strict_judgment
from .matching import Output, repository_result
from .reporting import label_variants

ROOT = Path(__file__).resolve().parents[2]
F1_RECORD, F2_RECORD = "docs/freeze/pretest_freeze.json", "docs/freeze/label_freeze.json"
F1_TAG, F2_TAG = "phase3-pretest-freeze", "phase3-label-freeze"
K_TEST = 7
ALLOWED_SPLITS = ("development", "validation", "synthetic-dev", "fixture", "test")
SENSITIVITY_VARIANTS = ("unresolved_ai", "unresolved_indeterminate", "consensus")


class GateError(RuntimeError):
    """Raised when a freeze gate required for the requested data has not been passed."""


def _tag_exists(root: Path, tag: str) -> bool:
    r = subprocess.run(["git", "tag", "-l", tag], cwd=root, capture_output=True, text=True)
    return r.stdout.strip() == tag


def check_gate(split: str, root: Path = ROOT) -> None:
    if split not in ALLOWED_SPLITS:
        raise GateError(f"unknown split {split!r}")
    if split == "test":
        missing = [p for p in (F1_RECORD, F2_RECORD) if not (root / p).exists()]
        missing += [t for t in (F1_TAG, F2_TAG) if not _tag_exists(root, t)]
        if missing:
            raise GateError(f"test split refused: F1/F2 not passed (missing {missing})")


def test_repositories(root: Path = ROOT) -> list[str]:
    m = json.loads((root / "benchmark/real/manifest.json").read_text(encoding="utf-8"))
    return [e["repo"] for e in m["splits"]["test"]]


def assert_seven(repos: Sequence[str], root: Path = ROOT) -> None:
    """TA17: exactly the seven manifest test repositories, so K = 7 in every H2 comparison."""
    expected = test_repositories(root)
    if len(expected) != K_TEST or sorted(set(repos)) != sorted(expected):
        raise GateError(f"TA17: expected exactly the {K_TEST} test repositories {expected}, got {sorted(set(repos))}")


def fa_baselines(root: Path = ROOT) -> list[str]:
    spec = json.loads((root / "docs/specification/run_specification_pre_f1.json").read_text(encoding="utf-8"))
    return list(spec["families"]["F-A"]["baselines"])


def rejudge(rows: Sequence[Mapping], labels: Mapping[str, Mapping]) -> list[dict]:
    """Re-score rows under a label variant (the tool outputs never change; only the labels do)."""
    out = []
    for r in rows:
        lab = labels.get(r["site_id"])
        if lab is None:
            continue
        j = judge(lab, r["tool_action"], r["rec_class"])
        js = strict_judgment(j, bool(r.get("dropin_wording")))
        out.append(dict(r, eligible=lab["eligible"], gt_role=lab["gt_role"], assessability=lab["assessability"],
                        hybrid_component=lab["hybrid_component"], judgment=j.judgment, harm_category=j.harm,
                        judgment_strict=js.judgment, harm_category_strict=js.harm))
    return out


def _output(r: Mapping) -> Output:
    return Output(r["tool_action"], r["rec_class"] or "NONE", r.get("tier") or None)


def run_fb(rows: Sequence[Mapping], labels: Sequence[Mapping], repos: Sequence[str], *, B: int, seed: int,
           mc_rule: bool = True) -> dict:
    """Every repository in `repos` enters every comparison, even with no labelled site under a label variant, so K
    never shrinks (TA17); such a repository is non-estimable and the comparison is not assessable as registered."""
    if not repos:
        return {"status": "NOT ASSESSABLE", "reason": "no repositories"}
    out = {(r["method"], r["site_id"]): _output(r) for r in rows}
    by_repo: dict[str, list[Mapping]] = {r: [] for r in repos}
    for lab in labels:
        if str(lab["eligible"]).lower() in ("true", "yes"):
            by_repo[lab["repo"]].append(lab)
    results = {}
    for comp, (fa_arm, m_arm) in H2_COMPARISONS.items():
        res = []
        for repo in sorted(by_repo):
            L = [l for l in by_repo[repo] if (f"pqscan:{fa_arm}", l["site_id"]) in out
                 and (f"pqscan:{m_arm}", l["site_id"]) in out]
            res.append(repository_result(L, [out[f"pqscan:{fa_arm}", l["site_id"]] for l in L],
                                         [out[f"pqscan:{m_arm}", l["site_id"]] for l in L], comparison=comp, repo=repo))
        results[comp] = res
    return h2.run_family(results, B=B, seed=seed, mc_rule=mc_rule)


def _variants(finals: Sequence[Mapping], ai_records: Sequence[Mapping]) -> dict[str, list[dict]]:
    full = {r["site"]["site_id"]: r["site"] for r in finals}
    return {name: [dict(full[v["site_id"]], **v) for v in vs]
            for name, vs in label_variants(finals, ai_records).items()}


def _all_repos(sites_by_repo: Mapping[str, list], repos: Sequence[str]) -> dict[str, list]:
    """C1: a repository with n_r = 0 stays in H3 (it makes every point NOT ESTIMABLE); it is never dropped."""
    return {r: list(sites_by_repo.get(r, [])) for r in repos}


def _one(rows, labels, repos, *, B, seed, h3_B, mc_rule, baselines, with_fb=True) -> dict:
    lab = {l["site_id"]: l for l in labels}
    jr = rejudge(rows, lab)
    res = {"F-A": fa.run_fa(jr, baselines, B=2_000) if any(r["method"] == fa.SYSTEM for r in jr) else
           {"status": "NOT ASSESSABLE", "reason": "no rows for the proposed system"},
           "H1a": h1.h1a(labels), "H1b": h1.h1b(jr), "H3": h3.analyse(_all_repos(h3.sites_from_rows(jr), repos), B=h3_B, seed=seed)}
    if with_fb:
        res["F-B"] = run_fb(jr, labels, repos, B=B, seed=seed, mc_rule=mc_rule)
    return res


def analyse(*, split: str, rows: Sequence[Mapping], finals: Sequence[Mapping], ai_records: Sequence[Mapping] = (),
            B: int = h2.B_PRIMARY, seed: int = h2.SEED, h3_B: int = h3.B_BOOT, mc_rule: bool = True,
            bounding: bool = True, root: Path = ROOT) -> dict:
    """`finals`: owner-final records {"site": {...label fields incl. repo...}, "meta": {"unresolved": [...]}}.
    `mc_rule=False` and small B are for development smoke tests only; the real analysis uses the defaults."""
    check_gate(split, root)
    repos = sorted({r["site"]["repo"] for r in finals})
    if split == "test":
        assert_seven(repos, root)
    variants = _variants(finals, ai_records)
    kw = dict(B=B, seed=seed, h3_B=h3_B, mc_rule=mc_rule, baselines=fa_baselines(root))
    out = {"split": split, "repositories": repos, "K": len(repos),
           "primary": _one(rows, variants["final"], repos, **kw),
           "note": "unresolved_owner equals 'final' (final labels already hold the owner's value) and is not repeated"}
    if bounding:
        out["sensitivities_TA22"] = {v: _one(rows, variants[v], repos, **kw) for v in SENSITIVITY_VARIANTS}
    return out


def analyse_h4(*, sites: Sequence[Mapping], outcomes_by_tool: Mapping, root: Path = ROOT,
               use_holdout: bool = False) -> dict:
    """H4 from Dataset A. Before F1 only synthetic-dev base cases may be used (use_holdout=False)."""
    manifest = json.loads((root / "benchmark/synthetic/manifest.json").read_text(encoding="utf-8"))
    split = manifest["split"]
    if use_holdout and not (root / F1_RECORD).exists():
        raise GateError("synthetic holdout refused before the F1 freeze record exists")
    keep = [s for s in sites if use_holdout or split.get(s["base_case"]) == "synthetic-dev"]
    return h4_analysis.analyse(keep, outcomes_by_tool, split)
