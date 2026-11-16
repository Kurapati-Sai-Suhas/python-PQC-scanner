"""Calibration of the stratified re-matching bootstrap for H2 (R4-03 audit). PROPOSED, NOT ADOPTED. Not results.

    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/calib_matching_v4.py            # full run (~25 min, 8 processes)
    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/calib_matching_v4.py --quick    # smoke run

Writes ../results/calib_matching.csv, ../results/calib_power.csv, ../results/calib_ties.csv and ../results/calib_matching.md.

Generative model (assumed; every number below is a planning assumption, not an estimate). Each repository r has
n = 30 eligible sites. A site's truth is one of
  T: determinate with a migration target (expected SIG or KEM),
  N: expected NONE (KEY_MATERIAL_ONLY / PROTOCOL_CONFIG / approved hybrid),
  I: expected ABSTAIN (INDETERMINATE),
shared by both arms. Each arm A, given the category, RECOMMENDs with probability r_A[cat]; a recommendation gets
tier t with probability pi_A[cat][t] and, on a T site, is CORRECT with probability q_A[t] (always not correct on N
or I: OVER_RECOMMENDATION / UNJUSTIFIED). A non-recommendation is FLAG_NO_TARGET with probability g_A (N sites;
CORRECT) or h_A (I sites; DETECTED_ONLY), otherwise ABSTAIN (CORRECT on I, UNASSESSABLE elsewhere). This is
exactly the frozen scoring table restricted to the actions the Module C arms emit (no DUAL, no PQC_ALREADY).
Dependence between the arms: with probability rho a site's action, tier and correctness uniforms are shared.

Population estimand (fixed repositories): delta_r = E_F(c*) - E_M(c*), c* = min(p_F, p_M), where E_A(c) is the
expected correct-per-eligible-site of arm A after withdrawing its lowest-tier recommendation mass down to coverage c
(uniform within the boundary tier). Computed analytically. Null scenarios are calibrated (bisection on one arm
parameter) so that delta_r equals a stated target exactly.

Test (as specified in R4-02 Sec. 5 / R4-03a): repository-balanced matched delta; B bootstrap resamples of sites
within each repository; each resample re-counts, re-matches with fresh uniform tie keys, re-scores;
p = (1 + #{delta* <= d0}) / (B + 1). Rejection at alpha/3, alpha/2, alpha (Holm steps for m = 3), alpha = 0.025.
"""
from __future__ import annotations

import copy
import csv
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matching_ref_v4 as MR  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
ALPHA = 0.025
LEVELS = (ALPHA / 3, ALPHA / 2, ALPHA)
CATS = ("T", "N", "I")
K_MIN, C_MIN, REPOS_MIN = 5, 0.20, 5          # proposed feasibility gate (R4-03 audit Sec. 4)


# --------------------------------------------------------------------------------------------- model
def arm(rT, piT, q, rN=0.0, piN=(0, 1, 0, 0), g=0.0, rI=0.0, piI=(0, 1, 0, 0), h=0.0):
    return dict(r=dict(T=rT, N=rN, I=rI), pi=dict(T=np.array(piT, float), N=np.array(piN, float), I=np.array(piI, float)),
                q=np.array(q, float), g=g, h=h)


def repo(F, M, pT=0.75, pN=0.10, pI=0.15, rho=0.5, n=30):
    return dict(F=F, M=M, p=dict(T=pT, N=pN, I=pI), rho=rho, n=n)


def coverage(R, A):
    return sum(R["p"][c] * A["r"][c] for c in CATS)


def expected_correct(R, A, c):
    """E[correct-per-eligible] of arm A after withdrawing lowest-tier REC mass down to coverage c."""
    mass = {cat: R["p"][cat] * A["r"][cat] * A["pi"][cat] for cat in CATS}
    W = max(0.0, coverage(R, A) - c)
    frac = np.zeros(4)
    for t in range(4):
        tm = sum(mass[cat][t] for cat in CATS)
        if tm <= 0 or W <= 0:
            continue
        w = min(W, tm)
        frac[t] = w / tm
        W -= w
    e = float(np.sum(mass["T"] * (1 - frac) * A["q"]) + np.sum(mass["I"] * frac))
    e += R["p"]["N"] * A["g"] + R["p"]["I"] * (1 - A["r"]["I"] - A["h"])
    return e


def pop_delta(R):
    c = min(coverage(R, R["F"]), coverage(R, R["M"]))
    return expected_correct(R, R["F"], c) - expected_correct(R, R["M"], c)


def _with(R, tune, th):
    R2 = copy.deepcopy(R)
    if tune == "qF":
        R2["F"]["q"] = np.clip(R["F"]["q"] + th, 0, 1)
    elif tune == "gF":
        R2["F"]["g"] = float(np.clip(R["F"]["g"] + th, 0, 1 - R["F"]["r"]["N"]))
    else:
        raise ValueError(tune)
    return R2


def calibrate(R, target, tune="qF"):
    lo, hi = -1.0, 1.0
    flo, fhi = pop_delta(_with(R, tune, lo)) - target, pop_delta(_with(R, tune, hi)) - target
    if flo > 0 or fhi < 0:
        raise ValueError(f"target {target} unreachable by tuning {tune}: range [{flo + target:.3f}, {fhi + target:.3f}]")
    for _ in range(80):
        mid = (lo + hi) / 2
        if pop_delta(_with(R, tune, mid)) - target > 0:
            hi = mid
        else:
            lo = mid
    R2 = _with(R, tune, (lo + hi) / 2)
    assert abs(pop_delta(R2) - target) < 1e-9, (pop_delta(R2), target)
    return R2


def _draw_arm(A, cat, ua, ut, uc):
    r = np.array([A["r"][c] for c in CATS])[cat]
    flag_p = np.where(cat == 1, A["g"], np.where(cat == 2, A["h"], 0.0))
    rec = ua < r
    flag = (~rec) & (ua < r + flag_p)
    cdf = np.stack([np.cumsum(A["pi"][c]) for c in CATS])[cat]          # (n, 4)
    tier = np.minimum((ut[:, None] > cdf).sum(1), 3)
    c_keep = np.where(rec, (cat == 0) & (uc < A["q"][tier]), np.where(flag, cat == 1, cat == 2)).astype(np.int8)
    c_wd = (cat == 2).astype(np.int8)
    return rec, np.where(rec, tier, -1), c_keep, c_wd


def draw_repo(R, rng):
    n = R["n"]
    p = np.array([R["p"][c] for c in CATS])
    cat = np.minimum((rng.random(n)[:, None] > np.cumsum(p)[None, :]).sum(1), 2)
    shared = rng.random(n) < R["rho"]
    uF = rng.random((3, n))
    uM = np.where(shared[None, :], uF, rng.random((3, n)))
    return _draw_arm(R["F"], cat, *uF), _draw_arm(R["M"], cat, *uM)


# --------------------------------------------------------------------------------------------- one data set
def analyse(repos_data, B, rng, d0):
    """Observed matched delta (random tie keys), bootstrap p, and diagnostics for one simulated data set."""
    deltas, ks, ns, disc = [], [], [], 0
    for F, M in repos_data:
        n = F[0].size
        idx = np.arange(n)[None, :]
        d, k = MR.matched_delta_batch(F, M, idx, rng.random((1, n)), rng.random((1, n)))
        deltas.append(d[0]); ks.append(int(k[0])); ns.append(n)
    est = float(np.mean(deltas))
    est_ta = float(np.mean([MR.tie_average_arrays(F, M) for F, M in repos_data]))   # seed-free point estimate
    p, dist = MR.bootstrap_pvalue(repos_data, d0=d0, B=B, seed=int(rng.integers(2**63)), chunk=B, return_dist=True)
    # basic (reverse-percentile) bootstrap on the tie-averaged estimate: reject H0 delta <= d0 when
    # 2*est_ta - q_(1-a)(delta*) > d0, i.e. p_basic = (1 + #{delta* >= 2*est_ta - d0}) / (B + 1)
    p_basic = (1 + np.count_nonzero(dist >= 2 * est_ta - d0 - 1e-12)) / (B + 1)
    ks, ns = np.array(ks), np.array(ns)
    gate = (ks.sum() / ns.sum() >= C_MIN) and ((ks >= K_MIN).sum() >= REPOS_MIN)
    return est, p, float(dist.std(ddof=1)), ks, ns, gate, est_ta, p_basic, float(dist.mean())


# --------------------------------------------------------------------------------------------- scenarios
def base_F(**kw):
    a = dict(rT=0.85, piT=(0.05, 0.10, 0.55, 0.30), q=(0.70, 0.80, 0.90, 0.95), rN=0.10, piN=(0.1, 0.3, 0.5, 0.1), g=0.70,
             rI=0.30, piI=(0.30, 0.40, 0.30, 0.0), h=0.05)
    a.update(kw)
    return arm(**a)


def base_M(**kw):
    a = dict(rT=0.50, piT=(0.10, 0.90, 0, 0), q=(0.75, 0.85, 0, 0), rN=0.05, piN=(0.2, 0.8, 0, 0), g=0.30,
             rI=0.15, piI=(0.2, 0.8, 0, 0), h=0.0)
    a.update(kw)
    return arm(**a)


HET = np.array([-3, -2, -1, 0, 1, 2, 3]) / 2.0     # population SD 1 across the 7 repositories


def scenarios():
    S = []

    def add(sid, desc, repos, targets=None, tunes=None, d0=0.0, mode="fixed", tau=0.0):
        S.append(dict(id=sid, desc=desc, repos=repos, targets=targets if targets is not None else [0.0] * 7,
                      tunes=tunes or ["qF"] * 7, d0=d0, mode=mode, tau=tau))

    b = repo(base_F(), base_M())
    # S00: the rev4 model of sim_matching_v4.py, re-implemented here (no calibration; tests H0: delta <= delta_true)
    r4 = repo(arm(0.85, (0, 0, 0.55, 0.45), (0, 0, 0.80, 0.93), rI=0.25, piI=(0, 0, 0.55, 0.45)),
              arm(0.50, (0.1, 0.9, 0, 0), (0.82, 0.82, 0, 0), rI=0.10, piI=(0.1, 0.9, 0, 0)), pT=0.85, pN=0.0, pI=0.15, rho=0.0)
    S.append(dict(id="S00", desc="rev4 model (sim_matching_v4.py) reproduced; H0: delta <= delta_true", repos=[r4] * 7,
                  targets=None, tunes=None, d0=pop_delta(r4), mode="uncalibrated", tau=0.0))
    add("S01", "base: F cov 0.69, M cov 0.40, rho 0.5, 15% indeterminate", [b] * 7)
    add("S02", "low natural coverage (F 0.34, M 0.17)", [repo(base_F(rT=0.40), base_M(rT=0.20, rI=0.05))] * 7)
    add("S03", "high natural coverage (F 0.80, M 0.70)", [repo(base_F(rT=0.95, rI=0.20), base_M(rT=0.85))] * 7)
    add("S04", "equal natural coverage (kink of min)", [repo(base_F(), base_M(rT=0.85, rN=0.10, rI=0.30))] * 7)
    add("S05", "comparator has the higher coverage (M withdraws; coarse T0/T1 tiers)",
        [repo(base_F(rT=0.50, rI=0.10), base_M(rT=0.90, rI=0.30))] * 7)
    add("S06", "very low matched coverage (M cov about 0.05; k_r often 0-2)",
        [repo(base_F(), base_M(rT=0.06, rN=0.0, rI=0.02))] * 7, tunes=["gF"] * 7)
    zero = repo(base_F(), base_M(rT=0.0, rN=0.0, rI=0.0))
    add("S07", "two repositories with zero comparator coverage (k_r = 0), five base",
        [zero, zero] + [b] * 5, tunes=["gF", "gF"] + ["qF"] * 5)
    add("S08", "flat tiers: all F recommendations T2 (withdrawal is pure tie-break)",
        [repo(base_F(piT=(0, 0, 1, 0), piN=(0, 0, 1, 0), piI=(0, 0, 1, 0)), base_M())] * 7)
    add("S09", "steep tiers: F T0-T3 equally likely, strong tier gradient, F's indeterminate recs at T0",
        [repo(base_F(piT=(0.25, 0.25, 0.25, 0.25), q=(0.40, 0.65, 0.85, 0.97), piI=(1, 0, 0, 0)), base_M())] * 7)
    add("S10", "high indeterminate share (35%)", [repo(base_F(), base_M(), pT=0.55, pN=0.10, pI=0.35)] * 7)
    add("S11", "low discordance (rho 0.9)", [repo(base_F(), base_M(), rho=0.9)] * 7)
    add("S12", "high discordance (rho 0, arms independent given truth)", [repo(base_F(), base_M(), rho=0.0)] * 7)
    add("S13", "heterogeneous repositories, fixed, tau 0.05 (mean delta_r 0)", [b] * 7, targets=list(0.05 * HET))
    add("S14", "heterogeneous repositories, fixed, tau 0.08 (mean delta_r 0; delta_r from -0.12 to +0.12)", [b] * 7, targets=list(0.08 * HET))
    covs = [(0.95, 0.80), (0.90, 0.60), (0.85, 0.45), (0.80, 0.30), (0.70, 0.20), (0.60, 0.50), (0.50, 0.40)]
    add("S15", "heterogeneous coverage across repositories (F 0.5-0.95, M 0.2-0.8 on T)",
        [repo(base_F(rT=a), base_M(rT=c)) for a, c in covs])
    add("S16", "random repositories (superpopulation): delta_r ~ N(0, 0.08^2) truncated at +-0.12, redrawn per data set",
        [b] * 7, mode="random", tau=0.08)
    add("S17", "margin boundary: delta_r = 0.10 everywhere, H0: delta <= 0.10 (B2, exploratory)", [b] * 7,
        targets=[0.10] * 7, d0=0.10)
    return S


def prepare(sc):
    if sc["mode"] == "uncalibrated":
        return [copy.deepcopy(r) for r in sc["repos"]]
    if sc["mode"] == "random":
        return None
    return [calibrate(r, t, tu) for r, t, tu in zip(sc["repos"], sc["targets"], sc["tunes"])]


def run_scenario(args):
    i, sc, reps, B = args
    rng = np.random.default_rng([20261113, 7, i])
    t0 = time.time()
    fixed = prepare(sc)
    rej = np.zeros(len(LEVELS)); rej_gate = np.zeros(len(LEVELS)); rej_b = np.zeros(len(LEVELS))
    ests, sds, pops, gates, k0, klow, cov, etas, bmeans = [], [], [], 0, 0, 0, [], [], []
    for _ in range(reps):
        if fixed is None:
            dr = rng.normal(0, sc["tau"], 7)
            reps_r = []
            for r, t in zip(sc["repos"], dr):
                reps_r.append(calibrate(r, float(np.clip(t, -0.12, 0.12))))   # symmetric truncation keeps mean 0
            pop = float(np.mean([pop_delta(r) for r in reps_r]))
        else:
            reps_r = fixed
            pop = float(np.mean([pop_delta(r) for r in reps_r]))
        data = [draw_repo(r, rng) for r in reps_r]
        est, p, sd, ks, ns, gate, eta, pb, bm = analyse(data, B, rng, sc["d0"])
        for j, a in enumerate(LEVELS):
            rej[j] += p <= a
            rej_gate[j] += (p <= a) and gate
            rej_b[j] += pb <= a
        ests.append(est); sds.append(sd); pops.append(pop); gates += gate; etas.append(eta); bmeans.append(bm)
        k0 += int((ks == 0).sum()); klow += int((ks < K_MIN).sum()); cov.append(ks.sum() / ns.sum())
    ests, pops = np.array(ests), np.array(pops)
    # the null holds for the superpopulation mean (0) in random mode, and for the fixed population delta otherwise
    truth = 0.0 if fixed is None else float(pops.mean())
    row = dict(id=sc["id"], description=sc["desc"], reps=reps, B=B, d0=sc["d0"], pop_delta=truth,
               matched_cov=float(np.mean(cov)), p_k0=k0 / (7 * reps), p_klow=klow / (7 * reps), p_gate=gates / reps,
               mean_est=float(ests.mean()), bias=float(ests.mean() - truth), sd_est=float(ests.std(ddof=1)),
               mean_boot_sd=float(np.mean(sds)), bias_tie_avg=float(np.mean(etas) - truth),
               sd_tie_avg=float(np.std(etas, ddof=1)), mean_boot_center_minus_est=float(np.mean(np.array(bmeans) - np.array(etas))),
               seconds=round(time.time() - t0, 1))
    for j, name in enumerate(("a3", "a2", "a1")):
        rate = rej[j] / reps
        row[f"rej_{name}"] = rate
        row[f"mcse_{name}"] = float(np.sqrt(max(rate, 1e-12) * (1 - rate) / reps))
        row[f"rej_gate_{name}"] = rej_gate[j] / reps
        rb = rej_b[j] / reps
        row[f"basic_rej_{name}"] = rb
        row[f"basic_mcse_{name}"] = float(np.sqrt(max(rb, 1e-12) * (1 - rb) / reps))
    return row


# --------------------------------------------------------------------------------------------- power vs coverage
def power_cells():
    cells = []
    for gap, qF, qM in ((0.15, 0.90, 0.75), (0.30, 0.95, 0.65)):
        for rM in (0.06, 0.12, 0.24, 0.35, 0.53):
            F = arm(0.85, (0, 0.1, 0.6, 0.3), (qF,) * 4, rI=0.0)
            M = arm(rM, (0.1, 0.9, 0, 0), (qM,) * 4, rI=0.0)
            cells.append(dict(gap=gap, rM=rM, repo=repo(F, M, pT=0.85, pN=0.0, pI=0.15)))
    return cells


def run_power(args):
    i, cell, reps, B = args
    rng = np.random.default_rng([20261113, 8, i])
    R = cell["repo"]
    pop = pop_delta(R)
    rej = np.zeros(len(LEVELS)); rejb = np.zeros(len(LEVELS)); gates = 0; cov = []
    for _ in range(reps):
        data = [draw_repo(R, rng) for _ in range(7)]
        est, p, sd, ks, ns, gate, eta, pb, bm = analyse(data, B, rng, 0.0)
        rej += np.array([p <= a for a in LEVELS]); rejb += np.array([pb <= a for a in LEVELS])
        gates += gate; cov.append(ks.sum() / ns.sum())
    return dict(precision_gap=cell["gap"], pop_matched_cov=min(coverage(R, R["F"]), coverage(R, R["M"])),
                mean_matched_cov=float(np.mean(cov)), pop_delta=pop, reps=reps, B=B,
                power_a3=rej[0] / reps, power_a2=rej[1] / reps, power_a1=rej[2] / reps, p_gate=gates / reps,
                basic_power_a3=rejb[0] / reps, basic_power_a1=rejb[2] / reps)


# --------------------------------------------------------------------------------------------- tie-break variability
def run_ties(args):
    i, sc, reps = args
    rng = np.random.default_rng([20261113, 9, i])
    fixed = prepare(sc)
    within, means, flip_point = [], [], 0
    for _ in range(reps):
        data = [draw_repo(r, rng) for r in fixed]
        vals = np.zeros(100)
        for F, M in data:
            n = F[0].size
            idx = np.repeat(np.arange(n)[None, :], 100, 0)
            d, _ = MR.matched_delta_batch(F, M, idx, rng.random((100, n)), rng.random((100, n)))
            vals += d
        vals /= len(data)
        within.append(vals.std(ddof=1)); means.append(vals.mean())
        flip_point += (vals.min() <= 0 < vals.max())
    return dict(id=sc["id"], description=sc["desc"], reps=reps, mean_within_dataset_tie_sd=float(np.mean(within)),
                sd_of_tie_averaged_estimate=float(np.std(means, ddof=1)),
                share_datasets_point_estimate_sign_changes_across_100_seeds=flip_point / reps)


# --------------------------------------------------------------------------------------------- main
BCHECK = ("S01", "S04", "S06", "S09")      # re-run with B = 5000 to check that B = 1000 does not drive the rates


def main():
    quick = "--quick" in sys.argv
    reps, B, preps, treps, breps, bB = (60, 200, 40, 50, 40, 400) if quick else (20000, 1000, 2000, 1000, 4000, 5000)
    sc = scenarios()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=16) as ex:
        f_rows = ex.map(run_scenario, [(i, s, reps, B) for i, s in enumerate(sc)])
        f_prow = ex.map(run_power, [(i, c, preps, B) for i, c in enumerate(power_cells())])
        f_trow = ex.map(run_ties, [(i, s, treps) for i, s in enumerate(sc) if s["id"] in ("S01", "S08", "S09", "S15")])
        f_brow = ex.map(run_scenario, [(100 + i, s, breps, bB) for i, s in enumerate(sc) if s["id"] in BCHECK])
        rows, prow, trow, brow = list(f_rows), list(f_prow), list(f_trow), list(f_brow)
    suffix = "_quick" if quick else ""
    for name, data in (("calib_matching", rows), ("calib_power", prow), ("calib_ties", trow), ("calib_bcheck", brow)):
        with (OUT / f"{name}{suffix}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader(); w.writerows(data)
    write_md(rows, prow, trow, brow, reps, B, preps, treps, breps, bB, suffix, time.time() - t0)
    print(f"done in {time.time() - t0:.0f} s")


def _rate(r, key):
    return f"{r[key]:.4f}"


def write_md(rows, prow, trow, brow, reps, B, preps, treps, breps, bB, suffix, secs):
    L = ["# Re-matching bootstrap calibration (PROPOSED, NOT ADOPTED; simulated planning figures, not results)", "",
         f"Generated by `scripts/calib_matching_v4.py`; {reps} data sets per scenario x B = {B} resamples; 7 repositories x 30 "
         f"sites; seeds numpy default_rng([20261113, 7, scenario index]); run time {secs / 60:.1f} min. Model and tests: script docstring.",
         "", "Every scenario except S00 has population delta exactly equal to d0, so rejection rates are Type I error rates. "
         "Holm thresholds for m = 3: a/3 = 0.00833, a/2 = 0.0125, a = 0.025.",
         f"MC SE with {reps} data sets: about 0.0011 at 0.025, 0.0008 at 0.0125, 0.0006 at 0.0083.", "",
         "**Percentile** = the test specified in R4-02 Sec. 5: p = (1 + #{delta* <= d0}) / (B + 1). "
         "**Basic** = reverse-percentile test on the seed-free tie-averaged estimate: p = (1 + #{delta* >= 2 est_ta - d0}) / (B + 1).", "",
         "## A. Design diagnostics", "",
         "| id | scenario | matched cov. | P(k_r=0) | P(k_r<5) | P(gate) | bias (seeded est.) | bias (tie-avg est.) | SD est. | mean boot SD | boot centre - est_ta |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['id']} | {r['description']} | {r['matched_cov']:.3f} | {r['p_k0']:.3f} | {r['p_klow']:.3f} | {r['p_gate']:.3f} | "
                 f"{r['bias']:+.4f} | {r['bias_tie_avg']:+.4f} | {r['sd_est']:.4f} | {r['mean_boot_sd']:.4f} | {r['mean_boot_center_minus_est']:+.4f} |")
    L += ["", "## B. Type I error (rejection rate; MC SE in brackets for the a column)", "",
          "| id | percentile a/3 | percentile a/2 | percentile a | percentile a, gate applied | basic a/3 | basic a/2 | basic a |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['id']} | {_rate(r, 'rej_a3')} | {_rate(r, 'rej_a2')} | {r['rej_a1']:.4f} ({r['mcse_a1']:.4f}) | {_rate(r, 'rej_gate_a1')} | "
                 f"{_rate(r, 'basic_rej_a3')} | {_rate(r, 'basic_rej_a2')} | {r['basic_rej_a1']:.4f} ({r['basic_mcse_a1']:.4f}) |")
    L += ["", f"## C. Check of the number of resamples: {breps} data sets with B = {bB} (independent seeds)", "",
          "| id | percentile a/3 | percentile a | basic a/3 | basic a |", "|---|---|---|---|---|"]
    for r in brow:
        L.append(f"| {r['id']} | {_rate(r, 'rej_a3')} | {r['rej_a1']:.4f} ({r['mcse_a1']:.4f}) | {_rate(r, 'basic_rej_a3')} | "
                 f"{r['basic_rej_a1']:.4f} ({r['basic_mcse_a1']:.4f}) |")
    L += ["", f"## D. Power of B1 as a function of matched coverage ({preps} data sets per cell, B = {B})", "",
          "F recommends with constant precision q_F, M with q_M (precision gap = q_F - q_M); no indeterminate or NONE-expected "
          "recommendations, so the population delta = matched coverage x precision gap.", "",
          "| precision gap | matched coverage (pop.) | pop. delta | percentile power a/3 | percentile power a | basic power a/3 | basic power a | P(gate) |",
          "|---|---|---|---|---|---|---|---|"]
    for r in prow:
        L.append(f"| {r['precision_gap']:.2f} | {r['pop_matched_cov']:.3f} | {r['pop_delta']:+.4f} | {r['power_a3']:.3f} | "
                 f"{r['power_a1']:.3f} | {r['basic_power_a3']:.3f} | {r['basic_power_a1']:.3f} | {r['p_gate']:.3f} |")
    L += ["", f"## E. Tie-break variability of the seeded point estimate (null scenarios; {treps} data sets, 100 tie seeds each)", "",
          "| id | scenario | mean SD across tie seeds | SD of tie-averaged estimate across data sets | share of data sets whose point-estimate sign differs across seeds |",
          "|---|---|---|---|---|"]
    for r in trow:
        L.append(f"| {r['id']} | {r['description']} | {r['mean_within_dataset_tie_sd']:.4f} | {r['sd_of_tie_averaged_estimate']:.4f} | "
                 f"{r['share_datasets_point_estimate_sign_changes_across_100_seeds']:.3f} |")
    (OUT / f"calib_matching{suffix}.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
