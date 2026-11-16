"""Reference implementation of equal-coverage matching (V12'') -- PROPOSED, NOT ADOPTED. Not production code.

Specification: ../R4_03a_matching_implementation_spec.md. This module exists so that the specification, the worked
example, the pilot demonstration and the unit tests can be checked against running code before the owner approves
the design. The production version (checklist item B4/B5, pqscan/bench) is written only after approval.

Two independent implementations are kept on purpose:
  * match_repository / matched_comparison: per-site, dictionary-based, hash tie-break (used for the observed data);
  * matched_delta_batch: vectorised numpy core used by the bootstrap and the calibration simulation.
The unit tests check that both give identical withdrawals and outcomes.

Scoring always goes through the frozen judge (pqscan.bench.judge.judge, scoring_policy.md v1.0), imported read-only.
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pqscan.bench.judge import judge  # noqa: E402  frozen scoring v1.0 (read-only use)

TIER_RANK = {"T0": 0, "T1": 1, "T2": 2, "T3": 3}
ACTIONS = ("RECOMMEND", "FLAG_NO_TARGET", "ABSTAIN", "NO_FINDING", "EXECUTION_FAILURE")
REC_CLASSES = ("SIG", "KEM", "DUAL", "PQC_ALREADY", "NONE")
PRIMARY_SEED = "20261113"
SENSITIVITY_SEEDS = tuple(f"20261113-S{i:03d}" for i in range(1, 101))
BOOTSTRAP_SEED = 20261113


@dataclass(frozen=True)
class ArmOutput:
    action: str
    rec_class: str = "NONE"
    tier: str | None = None


@dataclass
class RepoMatch:
    repo: str
    comparison: str
    seed: str
    n: int
    R_f: int
    R_m: int
    k: int
    withdrawn_f: list = field(default_factory=list)   # site ids, in withdrawal order
    withdrawn_m: list = field(default_factory=list)
    boundary_tier: str | None = None                  # tier in which the last withdrawal happened
    tied_at_boundary: int = 0                         # recommendations of the withdrawing arm in that tier
    withdrawn_at_boundary: int = 0


def tiebreak_key(seed: str, comparison: str, repo: str, site_id: str) -> str:
    """Library-independent seeded order: SHA-256 of 'seed|comparison|repo|site_id' (lower hex sorts first)."""
    return hashlib.sha256(f"{seed}|{comparison}|{repo}|{site_id}".encode("utf-8")).hexdigest()


def _validate(site_ids: Sequence[str], arm: Sequence[ArmOutput], name: str) -> None:
    if len(set(site_ids)) != len(site_ids):
        raise ValueError("duplicate site ids")
    if len(arm) != len(site_ids):
        raise ValueError(f"arm {name}: {len(arm)} outputs for {len(site_ids)} sites")
    for sid, a in zip(site_ids, arm):
        if a.action not in ACTIONS:
            raise ValueError(f"{name}/{sid}: unknown action {a.action!r}")
        if a.action == "EXECUTION_FAILURE":
            raise ValueError(f"{name}/{sid}: EXECUTION_FAILURE must be removed from the paired set before matching")
        if a.action == "RECOMMEND":
            if a.tier not in TIER_RANK:
                raise ValueError(f"{name}/{sid}: RECOMMEND without a valid evidence tier ({a.tier!r})")
            if a.rec_class not in REC_CLASSES or a.rec_class == "NONE":
                raise ValueError(f"{name}/{sid}: RECOMMEND with rec_class {a.rec_class!r}")


def match_repository(site_ids: Sequence[str], arm_f: Sequence[ArmOutput], arm_m: Sequence[ArmOutput], *,
                     comparison: str, repo: str, seed: str = PRIMARY_SEED, order: str = "tier") -> RepoMatch:
    """Label-free matching inside one repository. Only site ids and the two arms' outputs are inputs.
    order="tier": lowest tier first, SHA-256 within a tier (primary). order="hash": SHA-256 order only, tiers ignored
    (ranking-free sensitivity)."""
    if order not in ("tier", "hash"):
        raise ValueError(order)
    _validate(site_ids, arm_f, "F")
    _validate(site_ids, arm_m, "M")
    rec_f = [(sid, a) for sid, a in zip(site_ids, arm_f) if a.action == "RECOMMEND"]
    rec_m = [(sid, a) for sid, a in zip(site_ids, arm_m) if a.action == "RECOMMEND"]
    k = min(len(rec_f), len(rec_m))
    res = RepoMatch(repo, comparison, seed, len(site_ids), len(rec_f), len(rec_m), k)
    for recs, out in ((rec_f, res.withdrawn_f), (rec_m, res.withdrawn_m)):
        excess = len(recs) - k
        if excess <= 0:
            continue
        rank = (lambda a: TIER_RANK[a.tier]) if order == "tier" else (lambda a: 0)
        srt = sorted(recs, key=lambda x: (rank(x[1]), tiebreak_key(seed, comparison, repo, x[0])))
        out.extend(sid for sid, _ in srt[:excess])
        if order == "tier":
            res.boundary_tier = srt[excess - 1][1].tier
            res.tied_at_boundary = sum(1 for _, a in recs if a.tier == res.boundary_tier)
            res.withdrawn_at_boundary = sum(1 for _, a in srt[:excess] if a.tier == res.boundary_tier)
        else:
            res.boundary_tier, res.tied_at_boundary, res.withdrawn_at_boundary = "ANY", len(recs), excess
    return res


def apply_withdrawal(site_ids: Sequence[str], arm: Sequence[ArmOutput], withdrawn: Sequence[str]) -> list[ArmOutput]:
    w = set(withdrawn)
    return [ArmOutput("ABSTAIN", "NONE", a.tier) if sid in w else a for sid, a in zip(site_ids, arm)]


def is_correct(label: Mapping[str, str], out: ArmOutput) -> int:
    return int(judge(label, out.action, out.rec_class).judgment == "CORRECT")


def _category(out: ArmOutput, withdrawn: bool) -> str:
    if withdrawn:
        return "WITHDRAWN"
    return {"RECOMMEND": "REC", "FLAG_NO_TARGET": "FLAG", "ABSTAIN": "ABSTAIN", "NO_FINDING": "NO_FINDING"}[out.action]


def matched_comparison(sites: Sequence[Mapping[str, str]], arm_f: Sequence[ArmOutput], arm_m: Sequence[ArmOutput], *,
                       comparison: str, repo: str, seed: str = PRIMARY_SEED, order: str = "tier") -> dict:
    """Match, score with the frozen judge, and decompose. `sites` carry site_id plus the label fields the judge needs
    (eligible, gt_role, assessability, hybrid_component). Labels are used for scoring only, after matching."""
    ids = [s["site_id"] for s in sites]
    for s in sites:
        if str(s["eligible"]).lower() not in ("yes", "true"):
            raise ValueError(f"{s['site_id']}: only primary-set eligible sites enter the matched comparison")
    m = match_repository(ids, arm_f, arm_m, comparison=comparison, repo=repo, seed=seed, order=order)
    f2 = apply_withdrawal(ids, arm_f, m.withdrawn_f)
    m2 = apply_withdrawal(ids, arm_m, m.withdrawn_m)
    rows = []
    for s, a0, a1, b0, b1 in zip(sites, arm_f, f2, arm_m, m2):
        wf, wm = s["site_id"] in m.withdrawn_f, s["site_id"] in m.withdrawn_m
        rows.append({
            "site_id": s["site_id"],
            "F_natural": a0, "F_matched": a1, "F_withdrawn": wf,
            "M_natural": b0, "M_matched": b1, "M_withdrawn": wm,
            "F_judgment_natural": judge(s, a0.action, a0.rec_class).judgment,
            "F_judgment_matched": judge(s, a1.action, a1.rec_class).judgment,
            "M_judgment_natural": judge(s, b0.action, b0.rec_class).judgment,
            "M_judgment_matched": judge(s, b1.action, b1.rec_class).judgment,
            "X_nat": is_correct(s, a0), "X": is_correct(s, a1),
            "Y_nat": is_correct(s, b0), "Y": is_correct(s, b1),
            "F_cat": _category(a0, wf), "M_cat": _category(b0, wm),
        })
    n = len(rows)
    X = sum(r["X"] for r in rows); Y = sum(r["Y"] for r in rows)
    rec_f_after = sum(r["F_matched"].action == "RECOMMEND" for r in rows)
    rec_m_after = sum(r["M_matched"].action == "RECOMMEND" for r in rows)
    assert rec_f_after == rec_m_after == m.k, "equal recommendation counts after matching"
    decomp = {}
    for cat in ("REC", "WITHDRAWN", "FLAG", "ABSTAIN", "NO_FINDING"):
        decomp[cat] = (sum(r["X"] for r in rows if r["F_cat"] == cat), sum(r["Y"] for r in rows if r["M_cat"] == cat))
    both = {r["site_id"] for r in rows if r["F_matched"].action == "RECOMMEND" and r["M_matched"].action == "RECOMMEND"}
    f_only = {r["site_id"] for r in rows if r["F_matched"].action == "RECOMMEND" and r["M_matched"].action != "RECOMMEND"}
    m_only = {r["site_id"] for r in rows if r["M_matched"].action == "RECOMMEND" and r["F_matched"].action != "RECOMMEND"}
    return {
        "match": m, "rows": rows, "n": n, "X": X, "Y": Y, "delta": (X - Y) / n,
        "X_nat": sum(r["X_nat"] for r in rows), "Y_nat": sum(r["Y_nat"] for r in rows),
        "b": sum(1 for r in rows if r["X"] == 1 and r["Y"] == 0),
        "c": sum(1 for r in rows if r["X"] == 0 and r["Y"] == 1),
        "decomposition": decomp, "both_rec": both, "f_only_rec": f_only, "m_only_rec": m_only,
        "rec_correct_f": sum(r["X"] for r in rows if r["F_matched"].action == "RECOMMEND"),
        "rec_correct_m": sum(r["Y"] for r in rows if r["M_matched"].action == "RECOMMEND"),
    }


def tie_average_delta(sites, arm_f, arm_m, *, comparison: str, repo: str, order: str = "tier") -> float:
    """Exact expectation of the matched difference over all uniformly random tie-breaks (no seed). In the boundary
    tier, each tied recommendation of the withdrawing arm is withdrawn with probability j/m. Exact because the
    difference is linear in the withdrawal indicators and a uniformly random j-subset of m tied sites contains each
    of them with probability j/m. With order="hash" every recommendation is tied (probability e/R)."""
    ids = [s["site_id"] for s in sites]
    m = match_repository(ids, arm_f, arm_m, comparison=comparison, repo=repo, order=order)
    tot = 0.0
    for arm, withdrawn, sign in ((arm_f, m.withdrawn_f, 1), (arm_m, m.withdrawn_m, -1)):
        wset = set(withdrawn)
        p_tie = (m.withdrawn_at_boundary / m.tied_at_boundary) if (wset and m.tied_at_boundary) else 0.0
        bt = TIER_RANK[m.boundary_tier] if (wset and order == "tier") else None
        for s, a in zip(sites, arm):
            c_keep = is_correct(s, a)
            if a.action != "RECOMMEND" or not wset:
                tot += sign * c_keep
                continue
            c_wd = is_correct(s, ArmOutput("ABSTAIN", "NONE", a.tier))
            if order == "hash":
                pw = p_tie
            else:
                r = TIER_RANK[a.tier]
                pw = 1.0 if r < bt else (p_tie if r == bt else 0.0)
            tot += sign * ((1 - pw) * c_keep + pw * c_wd)
    return tot / len(sites)


# ---------------------------------------------------------------------------------------------- vectorised core
def site_arrays(sites, arm):
    """Per-site arrays for the vectorised core: rec (bool), tier (int, -1 if not REC), c_rec (correct if the
    output is kept), c_wd (correct if a REC is withdrawn, i.e. judged as ABSTAIN)."""
    rec = np.array([a.action == "RECOMMEND" for a in arm])
    tier = np.array([TIER_RANK[a.tier] if a.action == "RECOMMEND" else -1 for a in arm])
    c_keep = np.array([is_correct(s, a) for s, a in zip(sites, arm)], dtype=np.int8)
    c_wd = np.array([is_correct(s, ArmOutput("ABSTAIN", "NONE", a.tier)) for s, a in zip(sites, arm)], dtype=np.int8)
    return rec, tier, c_keep, c_wd


def _withdraw_mask(rec, tier, u, excess):
    """rec, tier, u: (B, n); excess: (B,). True where a REC is withdrawn: the `excess` smallest (tier + u) keys."""
    key = np.where(rec, tier + u, np.inf)
    order = np.argsort(key, axis=1, kind="stable")
    rank = np.empty_like(order)
    np.put_along_axis(rank, order, np.arange(rec.shape[1])[None, :].repeat(rec.shape[0], 0), axis=1)
    return rec & (rank < excess[:, None])


def matched_delta_batch(F, M, idx, uF, uM):
    """Matched difference for B resamples of one repository. F, M: tuples from site_arrays; idx: (B, n) resample
    indices; uF, uM: (B, n) tie-break keys in [0, 1). Returns (delta (B,), k (B,))."""
    recF, tierF, ckF, cwF = (a[idx] for a in F)
    recM, tierM, ckM, cwM = (a[idx] for a in M)
    RF, RM = recF.sum(1), recM.sum(1)
    k = np.minimum(RF, RM)
    wF = _withdraw_mask(recF, tierF, uF, RF - k)
    wM = _withdraw_mask(recM, tierM, uM, RM - k)
    X = np.where(wF, cwF, ckF)
    Y = np.where(wM, cwM, ckM)
    return (X.sum(1) - Y.sum(1)) / idx.shape[1], k


def tie_average_arrays(F, M):
    """Vectorised exact tie-average (expectation over uniform tie-breaks) of the matched difference for one
    repository; equals tie_average_delta on the same data (unit-tested)."""
    recF, recM = F[0], M[0]
    k = min(int(recF.sum()), int(recM.sum()))
    tot = []
    for rec, tier, ck, cw in (F, M):
        e = int(rec.sum()) - k
        w = np.zeros(rec.size)
        if e > 0:
            tiers = np.sort(tier[rec])
            tb = tiers[e - 1]                                  # boundary tier
            below = int((tiers < tb).sum()); at = int((tiers == tb).sum())
            w = np.where(rec & (tier < tb), 1.0, np.where(rec & (tier == tb), (e - below) / at, 0.0))
        tot.append(float(np.sum((1 - w) * ck + w * cw)))
    return (tot[0] - tot[1]) / recF.size


def bootstrap_pvalue(repos, d0=0.0, B=10_000, seed=BOOTSTRAP_SEED, chunk=2_000, return_dist=False):
    """Stratified re-matching bootstrap. repos: list of (F_arrays, M_arrays). Sites are resampled with replacement
    within each repository; repositories are fixed. Each resample re-counts R_F, R_M, recomputes k_r, withdraws by
    tier with fresh uniform tie keys, re-scores and recomputes the repository-balanced delta*.
    One-sided p for H0: delta <= d0 is (1 + #{delta* <= d0}) / (B + 1)."""
    rng = np.random.default_rng(seed)
    dist = np.empty(B)
    done = 0
    while done < B:
        b = min(chunk, B - done)
        acc = np.zeros(b)
        for F, M in repos:
            n = F[0].size
            idx = rng.integers(0, n, size=(b, n))
            uF = rng.random((b, n)); uM = rng.random((b, n))
            d, _ = matched_delta_batch(F, M, idx, uF, uM)
            acc += d
        dist[done:done + b] = acc / len(repos)
        done += b
    p = (1 + np.count_nonzero(dist <= d0 + 1e-12)) / (B + 1)
    return (p, dist) if return_dist else p


# ================================================================================ V12'' additions (R4-11 .. R4-16)
from fractions import Fraction  # noqa: E402


def _ta_arm(rec, tier, ck, cw, e, ranking=True):
    """Expected correct count of one arm over uniform tie-breaks, batched. rec/tier/ck/cw: (B, n); e: (B,)."""
    t = np.where(rec, tier if ranking else 0, 99)
    s = np.sort(t, axis=1)
    pos = np.clip(e - 1, 0, rec.shape[1] - 1)
    tb = np.take_along_axis(s, pos[:, None], 1)[:, 0]
    tb = np.where(e > 0, tb, -1)[:, None]
    below = (rec & (t < tb)).sum(1)
    at = (rec & (t == tb)).sum(1)
    frac = np.where(e > 0, (e - below) / np.maximum(at, 1), 0.0)[:, None]
    w = np.where(rec & (t < tb), 1.0, np.where(rec & (t == tb), frac, 0.0))
    return ((1 - w) * ck + w * cw).sum(1)


def tie_average_batch(F, M, idx, ranking=True):
    """Exact tie-averaged matched difference for B resamples of one repository (no tie randomness at all).
    Returns (delta_ta (B,), k (B,), R_F (B,), R_M (B,))."""
    recF, tierF, ckF, cwF = (a[idx] for a in F)
    recM, tierM, ckM, cwM = (a[idx] for a in M)
    RF, RM = recF.sum(1), recM.sum(1)
    k = np.minimum(RF, RM)
    xf = _ta_arm(recF, tierF, ckF, cwF, RF - k, ranking)
    ym = _ta_arm(recM, tierM, ckM, cwM, RM - k, ranking)
    return (xf - ym) / idx.shape[1], k, RF, RM


def pooled(values, ns, weighting="repository"):
    """Pooled estimate over repositories. 'repository' = (1/K) sum_r delta_r (primary, R4-02 Sec. 2);
    'site' = sum_r n_r delta_r / sum_r n_r (secondary). They are identical only when every n_r is equal.
    values: (K,) or (B, K)."""
    values, ns = np.asarray(values, float), np.asarray(ns, float)
    if weighting == "repository":
        out = values.mean(axis=-1)
    elif weighting == "site":
        out = (values * ns).sum(-1) / ns.sum()
    else:
        raise ValueError(weighting)
    return float(out) if np.ndim(out) == 0 else out


def bootstrap_ta(repos, d0=0.0, B=10_000, seed=BOOTSTRAP_SEED, chunk=2_000, weighting="repository", ranking=True,
                 return_dist=False):
    """V12'' primary test: stratified re-matching bootstrap of the exact tie-averaged estimate. Sites are resampled
    with replacement within each repository (repositories fixed, in the given order); every resample recounts,
    re-matches and re-scores with exact tie-averaging, so no tie key is drawn anywhere.
    p = (1 + #{delta* <= d0}) / (B + 1)."""
    rng = np.random.default_rng(seed)
    ns = np.array([F[0].size for F, _ in repos])
    dist = np.empty(B)
    done = 0
    while done < B:
        b = min(chunk, B - done)
        vals = np.empty((b, len(repos)))
        for j, (F, M) in enumerate(repos):
            idx = rng.integers(0, ns[j], size=(b, ns[j]))
            vals[:, j] = tie_average_batch(F, M, idx, ranking)[0]
        dist[done:done + b] = pooled(vals, ns, weighting)
        done += b
    p = (1 + np.count_nonzero(dist <= d0 + 1e-12)) / (B + 1)
    return (p, dist) if return_dist else p


def point_estimate_ta(repos, weighting="repository", ranking=True):
    vals = [float(tie_average_batch(F, M, np.arange(F[0].size)[None, :], ranking)[0][0]) for F, M in repos]
    return pooled(vals, [F[0].size for F, _ in repos], weighting), vals


def coverage_gap(R_f: Sequence[int], R_m: Sequence[int], n: Sequence[int]) -> Fraction:
    """Signed natural-coverage gap g = C_full - C_comparator, repository-balanced like the estimand:
    g = (1/K) sum_r (R_F,r - R_M,r) / n_r, as an exact fraction (no floating point at the boundary)."""
    if not (len(R_f) == len(R_m) == len(n)) or not n:
        raise ValueError("one entry per repository")
    if any(int(c) <= 0 for c in n):
        raise ValueError("every repository needs at least one common evaluable site")
    return sum((Fraction(int(a) - int(b), int(c)) for a, b, c in zip(R_f, R_m, n)), Fraction(0)) / len(n)


GUARD_G = Fraction(1, 10)


def guard_active(g: Fraction) -> bool:
    """Coverage-gap guard: active iff g < 1/10 exactly. Negative gaps, zero and 0 < g < 0.10 activate it;
    g = 0.10 exactly and above do not."""
    return g < GUARD_G


def guarded_p(p: float, g: Fraction) -> float:
    return min(1.0, 2.0 * p) if guard_active(g) else p


K_MIN, C_MIN, FEASIBLE_MIN = 5, Fraction(1, 5), 5


def feasibility(k: Sequence[int], n: Sequence[int], feasible_min: int = FEASIBLE_MIN) -> dict:
    """Feasibility gate (label-free). A repository is matching-feasible iff k_r >= 5. The gate passes iff the pooled
    matched coverage sum(k) / sum(n) >= 0.20 (site-weighted: it measures how many recommendations exist overall)
    AND at least `feasible_min` repositories (5 of the 7 test repositories) are feasible."""
    flags = [int(x) >= K_MIN for x in k]
    pooled_cov = Fraction(int(sum(k)), int(sum(n)))
    return {"feasible": flags, "n_feasible": sum(flags), "pooled_matched_coverage": pooled_cov,
            "passes": pooled_cov >= C_MIN and sum(flags) >= feasible_min}


def holm(pvals: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values, in input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj, run = [0.0] * m, 0.0
    for step, i in enumerate(order):
        run = max(run, min(1.0, (m - step) * pvals[i]))
        adj[i] = run
    return adj


def execution_partition(site_ids: Sequence[str], arm_f: Sequence[ArmOutput], arm_m: Sequence[ArmOutput]) -> dict:
    """Split the eligible sites of one repository by execution status (R4-12)."""
    out = {"both": [], "f_only": [], "m_only": [], "neither": []}
    for sid, a, b in zip(site_ids, arm_f, arm_m):
        fa, ma = a.action != "EXECUTION_FAILURE", b.action != "EXECUTION_FAILURE"
        out["both" if fa and ma else "f_only" if fa else "m_only" if ma else "neither"].append(sid)
    return out


def _prec(rows, arm, matched):
    key_a = f"{arm}_matched" if matched else f"{arm}_natural"
    key_x = ("X" if arm == "F" else "Y") if matched else ("X_nat" if arm == "F" else "Y_nat")
    recs = [r for r in rows if r[key_a].action == "RECOMMEND"]
    return (sum(r[key_x] for r in recs), len(recs))


def evaluate_repository(sites, arm_f, arm_m, *, comparison: str, repo: str) -> dict:
    """Complete V12'' per-repository report: execution partition; matching on the common evaluable set; exact
    tie-averaged estimate; primary-seed per-site table; ranking-free and failure sensitivities; every reporting field
    of R4-14. `sites` are the repository's primary-set eligible sites (labels used for scoring only)."""
    ids = [s["site_id"] for s in sites]
    part = execution_partition(ids, arm_f, arm_m)
    keep = set(part["both"])
    cs = [s for s in sites if s["site_id"] in keep]
    cf = [a for s, a in zip(sites, arm_f) if s["site_id"] in keep]
    cm = [a for s, a in zip(sites, arm_m) if s["site_id"] in keep]
    n_all, n = len(sites), len(cs)
    rep = {"comparison": comparison, "repo": repo, "n_eligible": n_all, "n_common": n,
           "exec_fail_f": sum(a.action == "EXECUTION_FAILURE" for a in arm_f),
           "exec_fail_m": sum(a.action == "EXECUTION_FAILURE" for a in arm_m),
           "partition": {k: len(v) for k, v in part.items()},
           "n_indeterminate_common": sum(1 for s in cs if judge(s, "ABSTAIN", "NONE").judgment == "CORRECT"),
           "n_indeterminate_eligible": sum(1 for s in sites if judge(s, "ABSTAIN", "NONE").judgment == "CORRECT")}
    if n == 0:
        rep.update(delta_ta=None, k=0, R_f=0, R_m=0, note="no common evaluable site")
        return rep
    r = matched_comparison(cs, cf, cm, comparison=comparison, repo=repo)
    m = r["match"]
    rep.update(
        R_f=m.R_f, R_m=m.R_m, k=m.k, cov_f=m.R_f / n, cov_m=m.R_m / n, matched_cov=m.k / n,
        withdrawn_f=len(m.withdrawn_f), withdrawn_m=len(m.withdrawn_m), boundary_tier=m.boundary_tier,
        tied=m.tied_at_boundary, withdrawn_at_boundary=m.withdrawn_at_boundary,
        both_rec=len(r["both_rec"]), f_only_rec=len(r["f_only_rec"]), m_only_rec=len(r["m_only_rec"]),
        correct_f=r["X"], correct_m=r["Y"], correct_f_nat=r["X_nat"], correct_m_nat=r["Y_nat"],
        incorrect_f=sum(1 for x in r["rows"] if x["F_judgment_matched"] == "INCORRECT"),
        incorrect_m=sum(1 for x in r["rows"] if x["M_judgment_matched"] == "INCORRECT"),
        delta_seed=r["delta"], b=r["b"], c=r["c"],
        delta_ta=tie_average_delta(cs, cf, cm, comparison=comparison, repo=repo),
        delta_ta_rankfree=tie_average_delta(cs, cf, cm, comparison=comparison, repo=repo, order="hash"),
        delta_nat=(r["X_nat"] - r["Y_nat"]) / n,
        prec_f_nat=_prec(r["rows"], "F", False), prec_m_nat=_prec(r["rows"], "M", False),
        prec_f_matched=_prec(r["rows"], "F", True), prec_m_matched=_prec(r["rows"], "M", True),
        decomposition=r["decomposition"], rows=r["rows"],
        delta_seeds=[matched_comparison(cs, cf, cm, comparison=comparison, repo=repo, seed=sd)["delta"]
                     for sd in SENSITIVITY_SEEDS],
        arrays=(site_arrays(cs, cf), site_arrays(cs, cm)))
    rep["prec_matched_ta"] = matched_precision_ta(*rep["arrays"])
    # failure sensitivity on the full eligible denominator (R4-12 Sec. 4)
    only_f = [i for i, (a, b) in enumerate(zip(arm_f, arm_m)) if a.action != "EXECUTION_FAILURE" and b.action == "EXECUTION_FAILURE"]
    only_m = [i for i, (a, b) in enumerate(zip(arm_f, arm_m)) if b.action != "EXECUTION_FAILURE" and a.action == "EXECUTION_FAILURE"]
    xf_extra = sum(is_correct(sites[i], arm_f[i]) for i in only_f)
    ym_extra = sum(is_correct(sites[i], arm_m[i]) for i in only_m)
    base = rep["delta_ta"] * n
    nfail_f, nfail_m = rep["exec_fail_f"], rep["exec_fail_m"]
    # S-F1: every failed (site, arm) scored "not correct"; single-arm sites scored for the arm that ran (unmatched)
    rep["delta_failures_not_correct"] = (base + xf_extra - ym_extra) / n_all
    # S-F2: extreme bounds: failures all correct for the other arm only (worst for F) / for F only (best for F)
    rep["delta_failure_bounds"] = ((base + xf_extra - ym_extra - nfail_f) / n_all,
                                   (base + xf_extra - ym_extra + nfail_m) / n_all)
    return rep


def matched_precision_ta(F, M, ranking=True):
    """Tie-averaged matched recommendation precision per arm: (expected correct kept RECOMMENDs, k) for F and M.
    F, M: site_arrays tuples of one repository (common evaluable set)."""
    k = min(int(F[0].sum()), int(M[0].sum()))
    out = []
    for rec, tier, ck, cw in (F, M):
        e = int(rec.sum()) - k
        w = np.zeros(rec.size)
        if e > 0:
            t = np.where(rec, tier if ranking else 0, 99)
            tb = np.sort(t)[e - 1]
            below = int((rec & (t < tb)).sum()); at = int((rec & (t == tb)).sum())
            w = np.where(rec & (t < tb), 1.0, np.where(rec & (t == tb), (e - below) / at, 0.0))
        out.append((float(np.sum((1 - w) * ck * rec)), k))
    return tuple(out)
