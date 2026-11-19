"""Experiment A, confirmatory family F-A (protocol v1.0.4 Sec. 5.4; phase3_analysis_plan.md Sec. 9; R4-21 C6;
owner rule D; R4-19 Batch 4).

For each baseline j that ran: one-sided exact McNemar ("proposed system better") on the pooled discordant pairs over
the sites where both the proposed system and j ran, at natural coverage; Holm across j at alpha = 0.025.
Required with every result: per-repository and pooled both-ran denominators, site-weighted and repository-balanced
differences (descriptive) with a within-repository bootstrap CI, execution failures by reason, and the S-F1 / S-F2
failure sensitivities. ASSUMPTIONS is printed with the results.

Input rows: one per (site, method) with keys site_id, repo, method, judgment (the frozen judge's output, as produced
by `pqscan.bench.run.judge_ours` / `judge_external`), and, for failures, judgment == "EXECUTION_FAILURE" with a
reason in `note` when available. Only primary-set eligible sites are passed in.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Sequence

import numpy as np

from .stats import holm, mcnemar_exact_one_sided

ALPHA = 0.025
SYSTEM = "pqscan:B4-full-T2"
NOT_SCORED = {"cbomkit": "not run (owner decision D4 = A)", "mehl": "repository-level labels, no per-site migration recommendation (owner decision D14)"}
# Wording of analysis plan v1.0.1 Sec. 9 (protocol v1.0.5 Sec. 5.4, F05); third-review finding TA02 replaced the v1.0.4
# text, which still asserted independent pairs. Pinned by tests/test_g08_confirmation_and_fa_assumptions.py.
ASSUMPTIONS = (
    "F-A assumptions (protocol v1.0.5 Sec. 5.4; analysis plan Sec. 9): (1) the 7 test repositories are fixed; "
    "inference concerns them only; (2) sites are stratified simple random samples with eligibility-only stopping; "
    "(3) sites are drawn without replacement within strata, so the sampled pairs are not independent. Whether the "
    "pooled exact test keeps its level under this design is not asserted from theory: it was checked by the pre-F1 "
    "simulation (plan Sec. 11.6; PASS), which covers the simulated configurations only; (4) the estimand of each "
    "comparison is the site-weighted difference over its own both-ran sites. Limitation: 7 purposively chosen "
    "repositories; no claim beyond them.")


def _correct(j: str) -> int:
    return int(j == "CORRECT")


def compare_one(rows_sys: dict, rows_base: dict, *, B: int = 2_000, seed: int = 20261113) -> dict:
    """rows_*: site_id -> (repo, judgment). Returns the per-baseline F-A record (without Holm)."""
    sites = sorted(set(rows_sys) & set(rows_base))
    if set(rows_sys) != set(rows_base):
        raise ValueError("the system and the baseline must be judged on the same eligible sites")
    by_repo: dict[str, list[tuple[int, int]]] = defaultdict(list)
    fail = {"system": 0, "baseline": 0, "both": 0}
    all_pairs = []
    for s in sites:
        repo, js = rows_sys[s]
        _, jb = rows_base[s]
        fs, fb = js == "EXECUTION_FAILURE", jb == "EXECUTION_FAILURE"
        if fs and fb:
            fail["both"] += 1
        elif fs:
            fail["system"] += 1
        elif fb:
            fail["baseline"] += 1
        all_pairs.append((repo, 0 if fs else _correct(js), 0 if fb else _correct(jb), fs, fb))
        if not (fs or fb):
            by_repo[repo].append((_correct(js), _correct(jb)))
    b = sum(x == 1 and y == 0 for v in by_repo.values() for x, y in v)
    c = sum(x == 0 and y == 1 for v in by_repo.values() for x, y in v)
    n = sum(len(v) for v in by_repo.values())
    repos = sorted(by_repo)
    rb = [np.mean([x - y for x, y in by_repo[r]]) for r in repos]
    # within-repository bootstrap (sites resampled inside each repository) for the site-weighted difference
    rng = np.random.default_rng(seed)
    if n:
        dist = np.zeros(B)
        for r in repos:
            d = np.array([x - y for x, y in by_repo[r]], dtype=float)
            dist += d[rng.integers(0, d.size, size=(B, d.size))].sum(axis=1)
        dist /= n
        ci = (float(np.quantile(dist, 0.025)), float(np.quantile(dist, 0.975)))
    else:
        ci = (None, None)
    N_all = len(all_pairs)
    # S-F1: every failed (site, method) scored not correct, on all eligible sites (x, y are already 0 for failures)
    base = sum(x - y for _, x, y, _, _ in all_pairs)
    sf1 = base / N_all if N_all else None
    # S-F2: extreme bounds: every site where the system failed counted as a baseline win (lower), every site where
    # the baseline failed counted as a system win (upper)
    sys_failed, base_failed = fail["system"] + fail["both"], fail["baseline"] + fail["both"]
    sf2 = ((base - sys_failed) / N_all, (base + base_failed) / N_all) if N_all else (None, None)
    return {"n_eligible": N_all, "n_both_ran": n, "both_ran_per_repo": {r: len(by_repo[r]) for r in repos},
            "b": b, "c": c, "p_one_sided": mcnemar_exact_one_sided(b, c),
            "delta_site": (b - c) / n if n else None, "delta_repo_balanced": float(np.mean(rb)) if rb else None,
            "ci95_site": ci, "failures": fail, "delta_sf1": sf1, "delta_sf2": sf2}


def run_fa(rows: Sequence[dict], baselines: Sequence[str], *, system: str = SYSTEM, B: int = 2_000) -> dict:
    """Holm across the baselines that ran. Baselines in NOT_SCORED are listed but never tested."""
    table: dict[str, dict] = defaultdict(dict)
    for r in rows:
        table[r["method"]][r["site_id"]] = (r["repo"], r["judgment"])
    if system not in table:
        raise ValueError(f"no rows for the proposed system {system}")
    out = {"assumptions": ASSUMPTIONS, "system": system, "not_scored": {}, "comparisons": {}}
    tested = []
    for j in baselines:
        key = next((k for k in NOT_SCORED if k in j.lower()), None)
        if key:
            out["not_scored"][j] = NOT_SCORED[key]
            continue
        if j not in table:
            out["not_scored"][j] = "no results"
            continue
        out["comparisons"][j] = compare_one(table[system], table[j], B=B)
        tested.append(j)
    adj = holm([out["comparisons"][j]["p_one_sided"] for j in tested]) if tested else []
    for j, a in zip(tested, adj):
        out["comparisons"][j]["p_holm"] = a
        out["comparisons"][j]["rejected"] = a <= ALPHA
    return out
