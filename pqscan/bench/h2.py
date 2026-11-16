"""H2 inference (phase3_analysis_plan.md Sec. 2, 5, 7, 8; decisions V10a, V10b, V13, V20, V21; R4-19 items 10-12).

Input: per comparison, the per-repository results of `pqscan.bench.matching.repository_result` for the seven test
repositories. Output: the estimates, bootstrap p-values, guard, gate, K/K_e assessability, Holm (m = 3) and the
outcome statements. Nothing here reads labels directly: correctness enters only through the matched arrays.

Bootstrap (Sec. 7.1): for b = 1..B, within each estimable repository (ascending name), draw n_r indices with
replacement and n_r uniform tie keys per arm; recount, re-match lowest tier first (ties by the keys), re-score and
pool with the point estimate's weighting. p(d0) = (1 + #{delta* <= d0}) / (B + 1). The repository-by-stratum
variant (Sec. 2 fallback) resamples within (repository x stratum) cells instead; it is used only if the pre-F1
two-stratum calibration requires it (BOOTSTRAP_VARIANT below records which variant is in force).
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

import numpy as np
from scipy import stats as sps

from .stats import holm

ALPHA = 0.025
MARGIN = 0.10
GUARD = Fraction(1, 10)
K_MIN, C_MIN, FEASIBLE_MIN, K_REPOS = 5, Fraction(1, 5), 5, 7
B_PRIMARY, B_RERUN, SEED = 10_000, 100_000, 20261113
CONFIRMATORY = ("H2-1", "H2-3", "H2-4")
BOOTSTRAP_VARIANT = "unstratified"          # "stratified" only if the pre-F1 two-stratum calibration fails (Sec. 11)


# --------------------------------------------------------------------------------------------- bootstrap
def _withdraw_mask(rec: np.ndarray, tier: np.ndarray, keys: np.ndarray, excess: np.ndarray) -> np.ndarray:
    """rec, tier, keys: (b, n); excess: (b,). True for the `excess` recommendations with the smallest tier + key."""
    score = np.where(rec, tier.astype(float) + keys, np.inf)
    ranks = np.argsort(np.argsort(score, axis=1, kind="stable"), axis=1, kind="stable")
    return rec & (ranks < excess[:, None])


def resampled_delta(F: tuple, M: tuple, idx: np.ndarray, keys_f: np.ndarray, keys_m: np.ndarray) -> np.ndarray:
    """Matched difference per resample of one repository (random tie keys inside the resample)."""
    rf, tf, kf, wf = (a[idx] for a in F)
    rm, tm, km, wm = (a[idx] for a in M)
    nf, nm = rf.sum(axis=1), rm.sum(axis=1)
    k = np.minimum(nf, nm)
    xf = np.where(_withdraw_mask(rf, tf, keys_f, nf - k), wf, kf).sum(axis=1)
    ym = np.where(_withdraw_mask(rm, tm, keys_m, nm - k), wm, km).sum(axis=1)
    return (xf - ym) / idx.shape[1]


def _indices(rng, n: int, b: int, strata: Sequence | None):
    if strata is None:
        return rng.integers(0, n, size=(b, n))
    strata = np.asarray(strata, dtype=object)
    idx = np.empty((b, n), dtype=np.int64)
    for s in sorted(set(strata.tolist()), key=str):
        pos = np.flatnonzero(strata == s)
        idx[:, pos] = pos[rng.integers(0, len(pos), size=(b, len(pos)))]
    return idx


def bootstrap(repos: Sequence[tuple[tuple, tuple]], *, B: int = B_PRIMARY, seed: int = SEED, chunk: int = 2_000,
              weighting: str = "repository", strata: Sequence[Sequence] | None = None) -> np.ndarray:
    """Distribution of delta* (length B). `repos` are (F arrays, M arrays) of the estimable repositories in ascending
    repository-name order. `strata` (per repository, per site) selects the repository-by-stratum variant."""
    rng = np.random.default_rng(seed)
    ns = np.array([F[0].size for F, _ in repos], dtype=float)
    out = np.empty(B)
    done = 0
    while done < B:
        b = min(chunk, B - done)
        vals = np.empty((b, len(repos)))
        for j, (F, M) in enumerate(repos):
            n = F[0].size
            idx = _indices(rng, n, b, None if strata is None else strata[j])
            vals[:, j] = resampled_delta(F, M, idx, rng.random((b, n)), rng.random((b, n)))
        out[done:done + b] = vals.mean(axis=1) if weighting == "repository" else (vals * ns).sum(axis=1) / ns.sum()
        done += b
    return out


def p_value(dist: np.ndarray, d0: float) -> float:
    return (1 + int(np.count_nonzero(dist <= d0 + 1e-12))) / (dist.size + 1)


def mc_rerun_needed(p: float, threshold: float, B: int) -> bool:
    return abs(p - threshold) < 3 * math.sqrt(max(p * (1 - p), 1e-300) / B)


# --------------------------------------------------------------------------------------------- guard, gate, K_e
def coverage_gap(results: Sequence[dict]) -> Fraction | None:
    """g = (1/K_e) sum over estimable repositories of (R_F - R_M)/n_r, exact. None when K_e = 0 (undefined)."""
    est = [r for r in results if r.get("n_common", 0) >= 1]
    if not est:
        return None
    return sum((Fraction(r["R_f"] - r["R_m"], r["n_common"]) for r in est), Fraction(0)) / len(est)


def guard_active(g: Fraction | None) -> bool:
    if g is None:
        raise ValueError("the coverage gap is undefined (K_e = 0)")
    return g < GUARD


def guarded(p: float, g: Fraction) -> float:
    return min(1.0, 2.0 * p) if guard_active(g) else p


def gate(results: Sequence[dict]) -> dict:
    est = [r for r in results if r.get("n_common", 0) >= 1]
    k = [r["k"] for r in est]
    n = [r["n_common"] for r in est]
    feasible = [r["repo"] for r in results if r.get("n_common", 0) >= 1 and r["k"] >= K_MIN]
    c_pool = Fraction(sum(k), sum(n)) if sum(n) else None
    c_bar = (sum(Fraction(a, b) for a, b in zip(k, n)) / len(n)) if n else None
    return {"c_pool": c_pool, "c_bar": c_bar, "feasible": feasible, "n_feasible": len(feasible),
            "passes": bool(c_pool is not None and c_pool >= C_MIN and len(feasible) >= FEASIBLE_MIN)}


def assessability(K: int, K_e: int) -> str:
    """Plan Sec. 7.4 (owner rules A and B)."""
    if K_e == K:
        return "assessable"
    if K_e == 0:
        return "not assessable (no estimable repository)"
    return "not assessable as pre-registered"


# --------------------------------------------------------------------------------------------- one comparison
def analyse_comparison(name: str, results: Sequence[dict], *, B: int = B_PRIMARY, seed: int = SEED,
                       variant: str = BOOTSTRAP_VARIANT) -> dict:
    results = sorted(results, key=lambda r: r["repo"])
    K = len(results)
    est = [r for r in results if r.get("n_common", 0) >= 1]
    K_e = len(est)
    out = {"comparison": name, "K": K, "K_e": K_e, "assessability": assessability(K, K_e),
           "non_estimable": [{"repo": r["repo"], "n_eligible": r["n_eligible"], "partition": r["partition"]}
                             for r in results if r.get("n_common", 0) < 1],
           "gate": gate(results), "B": B, "seed": seed, "variant": variant}
    if K_e == 0:
        out.update(g=None, guard=None, delta=None, delta_site=None, p=None, p_guarded=None, lower_975=None)
        return out
    g = coverage_gap(results)
    deltas = [r["delta_ta"] for r in est]
    ns = [r["n_common"] for r in est]
    repos = [r["arrays"] for r in est]
    strata = [r["site_strata"] for r in est] if variant == "stratified" else None
    dist = bootstrap(repos, B=B, seed=seed, strata=strata)
    p0 = p_value(dist, 0.0)
    out.update(g=g, guard=guard_active(g), delta=float(np.mean(deltas)),
               delta_site=float(np.dot(deltas, ns) / np.sum(ns)), p=p0, p_guarded=guarded(p0, g),
               lower_975=float(np.quantile(dist, 0.025)), lower_9875=float(np.quantile(dist, 0.0125)),
               dist_mean=float(dist.mean()), dist_sd=float(dist.std(ddof=1)),
               per_repo=[{"repo": r["repo"], "delta_ta": r["delta_ta"], "k": r["k"], "n_common": r["n_common"]} for r in est])
    if name == "H2-1":
        pm = p_value(dist, MARGIN)
        out.update(p_margin=pm, p_margin_guarded=guarded(pm, g))
    return out


# --------------------------------------------------------------------------------------------- family F-B
def holm_thresholds(pvals: dict[str, float]) -> dict[str, float]:
    order = sorted(pvals, key=lambda c: pvals[c])
    return {c: ALPHA / (len(order) - i) for i, c in enumerate(order)}


def run_family(results_by_comparison: dict[str, Sequence[dict]], *, B: int = B_PRIMARY, seed: int = SEED,
               variant: str = BOOTSTRAP_VARIANT) -> dict:
    """Steps 3-10 of plan Sec. 7.5 for H2-1, H2-3, H2-4 (H2-S analysed alongside, outside the family)."""
    res = {c: analyse_comparison(c, results_by_comparison[c], B=B, seed=seed, variant=variant)
           for c in results_by_comparison}
    # Monte Carlo rule: re-run a comparison with B = 100,000 if its guarded p is within 3 MC-SE of its threshold
    def guarded_or_one(c):
        r = res[c]
        return r["p_guarded"] if r["assessability"] == "assessable" else 1.0
    fam = [c for c in CONFIRMATORY if c in res]
    for _ in range(2):
        thr = holm_thresholds({c: guarded_or_one(c) for c in fam})
        rerun = [c for c in fam if res[c]["assessability"] == "assessable" and res[c]["B"] < B_RERUN
                 and mc_rerun_needed(res[c]["p"], thr[c] / (2 if res[c]["guard"] else 1), res[c]["B"])]
        if not rerun:
            break
        for c in rerun:
            res[c] = analyse_comparison(c, results_by_comparison[c], B=B_RERUN, seed=seed, variant=variant)
            res[c]["mc_rerun"] = True
    pstar = {c: guarded_or_one(c) for c in fam}
    adj = dict(zip(fam, holm([pstar[c] for c in fam]))) if fam else {}
    for c in fam:
        r = res[c]
        r["p_holm"] = adj[c]
        r["holm_rejected"] = adj[c] <= ALPHA
        r["claimable"] = r["assessability"] == "assessable" and r["holm_rejected"] and r["gate"]["passes"]
        r["statement"] = statement(c, r)
    if "H2-1" in res:
        r = res["H2-1"]
        r["h2b"] = h2b_statement(r)
    if "H2-S" in res:
        res["H2-S"]["statement"] = "secondary (outside the family)"
    return res


def statement(c: str, r: dict) -> str:
    """Plan Sec. 8. Never 'H2 supported'."""
    label = {"H2-1": "H2a (confirmatory)", "H2-3": "H2-3 (confirmatory)", "H2-4": "H2-4 (confirmatory)"}[c]
    if r["assessability"] != "assessable":
        return f"{label}: {r['assessability']}"
    if not r["gate"]["passes"]:
        return f"{label}: not assessable at equal coverage (matched coverage too low)"
    return f"{label}: {'supported' if r['claimable'] else 'not supported'}"


def h2b_statement(r: dict) -> str:
    if r["assessability"] != "assessable":
        return "H2b (exploratory, pre-specified; not under family-wise error control): not assessable"
    met = r["p_margin_guarded"] <= ALPHA
    return ("H2b (exploratory, pre-specified; not under family-wise error control): 10-point criterion "
            + ("met" if met else "not met"))


# --------------------------------------------------------------------------------------------- exploratory (S15)
def repository_level(deltas: Sequence[float]) -> dict:
    """Exploratory generalisation analyses on the per-repository estimates (labelled exploratory; R4-04)."""
    d = np.asarray(deltas, dtype=float)
    K = d.size
    out = {"K_e": K, "deltas": d.tolist(), "leave_one_out": [float(np.delete(d, i).mean()) for i in range(K)] if K > 1 else []}
    if K >= 2 and d.std(ddof=1) > 0:
        out["t_one_sided_p"] = float(sps.ttest_1samp(d, 0.0, alternative="greater").pvalue)
    if K >= 1:
        signs = np.array(np.meshgrid(*[[-1, 1]] * K)).reshape(K, -1).T
        stat = (signs * np.abs(d)).sum(axis=1)
        out["sign_flip_p"] = float(np.mean(stat >= d.sum() - 1e-12))
        if np.any(d != 0):
            out["wilcoxon_one_sided_p"] = float(sps.wilcoxon(d, alternative="greater").pvalue)
    return out
