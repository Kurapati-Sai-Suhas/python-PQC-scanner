"""Coverage matching (R4_03): implementation, worked example and validity simulation (PROPOSED rev4; not results).

    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/sim_matching_v4.py

Matching rule (within each repository, per comparison): coverage = RECOMMEND / eligible (data dictionary). Let
k_r = min(#RECOMMEND of arm F, #RECOMMEND of arm M) on the repository's primary-set eligible sites. The arm with more
RECOMMEND decisions withdraws decisions, lowest evidence tier first (T0 < T1 < T2 < T3), ties broken by a seeded
random order of candidate IDs, until it has exactly k_r. A withdrawn decision becomes ABSTAIN and is scored by the
frozen policy (CORRECT on an INDETERMINATE site, UNASSESSABLE (not correct) on a DETERMINATE one). Labels are never
used for matching. Every eligible site keeps one outcome per arm, so outcomes stay paired on an identical denominator.

Validity check: matching makes a site's outcome depend on the other sampled sites (through k_r and the ranks).
The simulation estimates (a) the ratio of the empirical variance of the pooled matched difference to the mean
multinomial variance estimate used by the score test, and (b) the rejection rate of the Tango test of
H0: delta <= delta_true at one-sided 0.025, where delta_true is the matched difference in a 200,000-site population.
Writes ../results/matching.md.
"""
from pathlib import Path
import numpy as np
import stats_v4 as S

OUT = Path(__file__).resolve().parents[1] / "results"
TIER = {"T0": 0, "T1": 1, "T2": 2, "T3": 3}


def match(rec_f, tier_f, rec_m, tier_m, ids, seed):
    """Return withdrawal masks (wf, wm): True where the arm's RECOMMEND is withdrawn."""
    k = min(rec_f.sum(), rec_m.sum())
    wf, wm = np.zeros(rec_f.size, bool), np.zeros(rec_m.size, bool)
    for rec, tier, w in ((rec_f, tier_f, wf), (rec_m, tier_m, wm)):
        excess = rec.sum() - k
        if excess > 0:
            rng = np.random.default_rng(seed)
            tiebreak = rng.permutation(len(ids))
            cand = np.flatnonzero(rec)
            order = cand[np.lexsort((tiebreak[cand], tier[cand]))]   # lowest tier first, then seeded order
            w[order[:excess]] = True
    return wf, wm


def gen_sites(n, rng):
    """Generative model (assumed, illustrative): indeterminate share 0.15; full arm F (threshold T0) recommends on 85%
    of determinate sites (T3 45%, else T2; correct 0.93 / 0.80) and on 25% of indeterminate sites (never correct);
    comparator M recommends on 50% of determinate sites (T1 90%, else T0; correct 0.82) and on 10% of indeterminate ones."""
    ind = rng.random(n) < 0.15
    rf = np.where(ind, rng.random(n) < 0.25, rng.random(n) < 0.85)
    tf = np.where(rng.random(n) < 0.45, 3, 2)
    cf = np.where(tf == 3, rng.random(n) < 0.93, rng.random(n) < 0.80) & ~ind
    rm = np.where(ind, rng.random(n) < 0.10, rng.random(n) < 0.50)
    tm = np.where(rng.random(n) < 0.90, 1, 0)
    cm = (rng.random(n) < 0.82) & ~ind
    return ind, rf, tf, cf, rm, tm, cm


def outcomes(ind, rf, tf, cf, rm, tm, cm, seed):
    wf, wm = match(rf, tf, rm, tm, np.arange(ind.size), seed)
    xf = np.where(rf & ~wf, cf, ind)        # decided -> correctness; abstained/withdrawn -> correct only if indeterminate
    xm = np.where(rm & ~wm, cm, ind)
    return xf.astype(int), xm.astype(int), (rf & ~wf).sum(), (rm & ~wm).sum()


def worked_example():
    # 10 hypothetical sites in one repository (illustration only)
    rows = [  # id, indeterminate, F rec, F tier, F correct-if-decided, M rec, M tier, M correct-if-decided
        ("s1", 0, 1, "T3", 1, 1, "T1", 1), ("s2", 0, 1, "T3", 1, 0, "T1", 0), ("s3", 0, 1, "T2", 1, 1, "T1", 0),
        ("s4", 0, 1, "T2", 0, 0, "T1", 0), ("s5", 0, 1, "T2", 1, 1, "T0", 1), ("s6", 1, 0, "T2", 0, 0, "T1", 0),
        ("s7", 0, 1, "T3", 1, 0, "T1", 0), ("s8", 0, 1, "T2", 1, 1, "T1", 1), ("s9", 0, 0, "T2", 0, 0, "T0", 0),
        ("s10", 1, 1, "T2", 0, 0, "T1", 0)]
    ind = np.array([r[1] for r in rows], bool)
    rf = np.array([r[2] for r in rows], bool); tf = np.array([TIER[r[3]] for r in rows])
    cf = np.array([r[4] for r in rows], bool)
    rm = np.array([r[5] for r in rows], bool); tm = np.array([TIER[r[6]] for r in rows])
    cm = np.array([r[7] for r in rows], bool)
    wf, wm = match(rf, tf, rm, tm, np.arange(10), seed=20261113)
    xf = np.where(rf & ~wf, cf, ind).astype(int)
    xm = np.where(rm & ~wm, cm, ind).astype(int)
    xf_nat = np.where(rf, cf, ind).astype(int)
    lines = ["## Worked example (hypothetical; 10 sites, one repository)", "",
             "| site | indeterminate | F action (tier) | F withdrawn | F correct (matched) | M action (tier) | M correct | pair (F,M) |",
             "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows):
        fa = f"REC ({r[3]})" if r[2] else "ABSTAIN"
        ma = f"REC ({r[6]})" if r[5] else "ABSTAIN"
        lines.append(f"| {r[0]} | {'yes' if r[1] else 'no'} | {fa} | {'yes' if wf[i] else '-'} | {xf[i]} | {ma} | {xm[i]} | ({xf[i]},{xm[i]}) |")
    b, c = int(((xf == 1) & (xm == 0)).sum()), int(((xf == 0) & (xm == 1)).sum())
    lines += ["", f"Natural coverage: F {rf.sum()}/10, M {rm.sum()}/10. k = {min(rf.sum(), rm.sum())}; F withdraws "
              f"{int(wf.sum())} recommendation(s), lowest tier first (all T2; seeded tie-break), so both cover {min(rf.sum(), rm.sum())}/10.",
              f"Matched correctness: F {xf.sum()}/10, M {xm.sum()}/10, delta = {(xf.sum() - xm.sum()) / 10:+.2f}; discordant pairs b = {b}, c = {c}.",
              f"Natural-coverage correctness (secondary): F {xf_nat.sum()}/10, M {xm.sum() if not wm.any() else 'n/a'}/10, delta = {(xf_nat.sum() - xm.sum()) / 10:+.2f}.",
              "Numerator = sites judged CORRECT; denominator = all 10 eligible sites, for both arms (abstentions stay in the denominator)."]
    return lines


def main():
    rng = np.random.default_rng(20261113)
    pop = gen_sites(200_000, rng)
    xf, xm, kf, km = outcomes(*pop, seed=1)
    true_delta = (xf.mean() - xm.mean())
    lines = ["# Coverage matching: validity simulation and worked example (PROPOSED rev4; not results)", "",
             f"Population (200,000 sites, assumed generative model in the script): matched coverage {kf / 2e5:.3f} for both arms; "
             f"matched difference delta_true = {true_delta:+.4f}.", ""]
    reps, ests, vhat, rej = 4000, [], [], 0
    for r in range(reps):
        b_tot = c_tot = 0
        for repo in range(7):
            site = gen_sites(30, rng)
            f, m, _, _ = outcomes(*site, seed=20261113 + 1000 * r + repo)
            b_tot += int(((f == 1) & (m == 0)).sum()); c_tot += int(((f == 0) & (m == 1)).sum())
        n = 210
        d = (b_tot - c_tot) / n
        ests.append(d)
        vhat.append(((b_tot + c_tot) / n - d * d) / n)
        rej += float(S.tango_p_upper(b_tot, c_tot, n, true_delta)) <= 0.025
    ests = np.array(ests)
    lines += [f"Samples: {reps} x (7 repositories x 30 sites), matching within each repository.", "",
              f"- mean estimate {ests.mean():+.4f} vs delta_true {true_delta:+.4f} (bias {ests.mean() - true_delta:+.4f})",
              f"- empirical variance / mean multinomial variance estimate = {ests.var(ddof=1) / np.mean(vhat):.3f} (<= 1 means the test's variance is not understated)",
              f"- rejection rate of Tango H0: delta <= delta_true at one-sided 0.025: {rej / reps:.4f} (MC SE about 0.0025)", ""]
    lines += worked_example()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "matching.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()


def bootstrap_check(reps=2000, boots=400, seed=20261114):
    """Calibration of the stratified re-matching bootstrap: resample sites within each repository WITH their arm
    outputs, re-apply matching, recompute the pooled matched difference; one-sided lower 97.5% percentile bound.
    Reports P(lower bound > delta_true), which should be about 0.025."""
    rng = np.random.default_rng(seed)
    pop = gen_sites(200_000, np.random.default_rng(20261113))
    xf, xm, _, _ = outcomes(*pop, seed=1)
    true_delta = xf.mean() - xm.mean()
    miss = 0
    for r in range(reps):
        repos = [gen_sites(30, rng) for _ in range(7)]
        stats = np.empty(boots)
        for bi in range(boots):
            tot = 0.0
            for k, site in enumerate(repos):
                idx = rng.integers(0, 30, 30)
                f, m, _, _ = outcomes(*(a[idx] for a in site), seed=bi * 7 + k)
                tot += f.mean() - m.mean()
            stats[bi] = tot / 7
        miss += np.quantile(stats, 0.025) > true_delta
    return true_delta, miss / reps


if __name__ == "__main__" and "--bootstrap" in __import__("sys").argv:
    td, rate = bootstrap_check()
    line = f"- stratified re-matching bootstrap: P(lower 97.5% bound > delta_true) = {rate:.4f} (2000 data sets x 400 resamples; MC SE about 0.0035)"
    print(line)
    with (OUT / "matching.md").open("a", encoding="utf-8") as fh:
        fh.write("\n" + line + "\n")
