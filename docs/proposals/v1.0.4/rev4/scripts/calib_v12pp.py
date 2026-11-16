"""Complete-procedure calibration of V12'' (R4-13). PROPOSED, NOT ADOPTED. Simulated planning figures, not results.

    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/calib_v12pp.py          # full (~30-40 min, 16 processes)
    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/calib_v12pp.py --quick  # smoke run (writes *_quick files)

Procedure tested on every simulated data set, exactly as specified in R4-03a/R4-11:
  1. natural coverage per repository (R_F, R_M on the common evaluable set);
  2. signed coverage gap g = (1/K) sum_r (R_F,r - R_M,r)/n_r (exact fraction) and the guard (active iff g < 0.10);
  3. repository-specific matching, k_r = min(R_F,r, R_M,r);
  4. lowest-evidence-tier withdrawal;
  5. ties: the point estimate is the exact tie-average (no tie seed). Two bootstrap variants run on the same resamples:
     RK = fresh uniform tie keys inside each resample (the recommended V12'' test) and TA = exact tie-averaging inside
     each resample (calibrated and rejected: liberal, R4-13);
  6. frozen scoring (model restricted to the actions Module C emits; see calib_matching_v4.py);
  7. stratified re-matching bootstrap (sites within repositories, B resamples, percentile p);
  8. Holm: single comparisons here report rejection at the three Holm levels a/3, a/2, a; the joint three-comparison
     family is simulated in sim_family_v12pp.py.
Model, scenarios S00-S17 and near-kink cells are those of calib_matching_v4.py / calib_nearkink_v4.py. Power variants
shift every repository's population delta to +0.05 (S17: 0.15 against d0 = 0.10; S00: its own delta_true against 0).
Seeds: numpy default_rng([20261113, 21, task index, chunk]).
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
import calib_matching_v4 as C  # noqa: E402
import calib_nearkink_v4 as NK  # noqa: E402
import matching_ref_v4 as MR  # noqa: E402

OUT = C.OUT
LEVELS = (C.ALPHA / 3, C.ALPHA / 2, C.ALPHA)
TAGS = ("a3", "a2", "a1")


def analyse_full(data, B, rng, d0):
    ns = [F[0].size for F, _ in data]
    RF = [int(F[0].sum()) for F, _ in data]
    RM = [int(M[0].sum()) for _, M in data]
    ks = [min(a, b) for a, b in zip(RF, RM)]
    est, _ = MR.point_estimate_ta(data)
    g = MR.coverage_gap(RF, RM, ns)
    gate = MR.feasibility(ks, ns)["passes"]
    brng = np.random.default_rng(int(rng.integers(2**63)))
    vta = np.empty((B, len(data))); vrk = np.empty((B, len(data)))
    for j, (F, M) in enumerate(data):
        n = ns[j]
        idx = brng.integers(0, n, size=(B, n))
        vta[:, j] = MR.tie_average_batch(F, M, idx)[0]
        vrk[:, j] = MR.matched_delta_batch(F, M, idx, brng.random((B, n)), brng.random((B, n)))[0]
    dta, drk = vta.mean(1), vrk.mean(1)
    p_ta = (1 + np.count_nonzero(dta <= d0 + 1e-12)) / (B + 1)
    p_rk = (1 + np.count_nonzero(drk <= d0 + 1e-12)) / (B + 1)
    return dict(est=est, p=p_ta, p_guard=MR.guarded_p(p_ta, g), p_rk=p_rk, p_rk_guard=MR.guarded_p(p_rk, g),
                guard=MR.guard_active(g), gate=gate,
                g=float(g), boot_sd=float(dta.std(ddof=1)), lower=float(np.quantile(dta, 0.025)))


def _null_repos(sc):
    if sc["mode"] == "random":
        return None
    return C.prepare(sc)


def _shift(sc, delta):
    """Alternative version of a scenario: every repository's population delta moved to `delta` (or d0 + 0.05)."""
    s = copy.deepcopy(sc)
    if s["mode"] == "uncalibrated":
        s["d0"] = 0.0          # S00: its own delta_true (> 0) tested against 0
        return s
    if s["id"] == "S17":
        s["targets"] = [0.12] * 7          # 0.12 is the model's reachable maximum; tested against d0 = 0.10
        return s
    base = np.array(s["targets"], float)
    # heterogeneous patterns are capped at the reachable maximum 0.12; the realised mean is reported as pop. delta
    s["targets"] = list(np.minimum(base - base.mean() + delta, 0.12))
    s["tau_mean"] = delta
    return s


def run_task(args):
    kind, tid, sc, reps, B, chunk = args
    rng = np.random.default_rng([20261113, 21, tid, chunk])
    try:
        fixed = _null_repos(sc) if kind != "nearkink" else [C.calibrate(sc["repo"], 0.0)] * 7
    except ValueError as e:
        return dict(kind=kind, id=sc["id"], chunk=chunk, error=str(e))
    cnt = dict(n=0, guard=0, gate=0, est=0.0, est2=0.0, pop=0.0)
    for t in TAGS:
        for key in ("rej", "rej_guard", "rej_rk", "rej_claim", "rej_rkg", "rej_rkclaim"):
            cnt[f"{key}_{t}"] = 0
    for _ in range(reps):
        if fixed is None:
            mu = sc.get("tau_mean", 0.0)
            # truncation at mu +- 0.12, capped at +0.12 (the model's reachable maximum); symmetric when mu = 0
            dr = np.clip(rng.normal(mu, sc["tau"], 7), mu - 0.12, min(mu + 0.12, 0.12))
            repos = [C.calibrate(r, float(t)) for r, t in zip(sc["repos"], dr)]
            pop = float(dr.mean())
        else:
            repos = fixed
            pop = float(np.mean([C.pop_delta(r) for r in repos]))
        data = [C.draw_repo(r, rng) for r in repos]
        a = analyse_full(data, B, rng, sc["d0"])
        cnt["n"] += 1; cnt["guard"] += a["guard"]; cnt["gate"] += a["gate"]
        cnt["est"] += a["est"]; cnt["est2"] += a["est"] ** 2; cnt["pop"] += pop
        for t, lv in zip(TAGS, LEVELS):
            cnt[f"rej_{t}"] += a["p"] <= lv
            cnt[f"rej_guard_{t}"] += a["p_guard"] <= lv
            cnt[f"rej_rk_{t}"] += a["p_rk"] <= lv
            cnt[f"rej_claim_{t}"] += (a["p_guard"] <= lv) and a["gate"]
            cnt[f"rej_rkg_{t}"] += a["p_rk_guard"] <= lv
            cnt[f"rej_rkclaim_{t}"] += (a["p_rk_guard"] <= lv) and a["gate"]
    cnt.update(kind=kind, id=sc["id"], chunk=chunk, description=sc.get("desc", ""), d0=sc["d0"])
    return cnt


def aggregate(results):
    rows = {}
    for r in results:
        key = (r["kind"], r["id"])
        if "error" in r:
            rows[key] = dict(kind=r["kind"], id=r["id"], error=r["error"])
            continue
        agg = rows.setdefault(key, {k: 0 for k in r if isinstance(r[k], (int, float, np.integer, np.floating, bool)) and k != "chunk"})
        if "error" in agg:
            continue
        for k in agg:
            agg[k] += r[k]
        agg.update(kind=r["kind"], id=r["id"], description=r["description"], d0=r["d0"])
    out = []
    for key, a in rows.items():
        if "error" in a:
            out.append(a); continue
        n = a["n"]
        row = dict(kind=a["kind"], id=a["id"], description=a["description"], d0=a["d0"], reps=n,
                   pop_delta=a["pop"] / n, mean_est=a["est"] / n, sd_est=float(np.sqrt(max(a["est2"] / n - (a["est"] / n) ** 2, 0))),
                   p_guard_on=a["guard"] / n, p_gate=a["gate"] / n)
        for t in TAGS:
            for key2 in ("rej", "rej_guard", "rej_rk", "rej_claim", "rej_rkg", "rej_rkclaim"):
                row[f"{key2}_{t}"] = a[f"{key2}_{t}"] / n
            row[f"mcse_{t}"] = float(np.sqrt(max(row[f"rej_rkg_{t}"], 1e-12) * (1 - row[f"rej_rkg_{t}"]) / n))
            row[f"mcse_ta_{t}"] = float(np.sqrt(max(row[f"rej_guard_{t}"], 1e-12) * (1 - row[f"rej_guard_{t}"]) / n))
        out.append(row)
    return out


def main():
    quick = "--quick" in sys.argv
    R0, RK, RP, RC, B, CH = (40, 40, 40, 40, 200, 1) if quick else (20000, 10000, 4000, 2000, 1000, 4)
    scen = C.scenarios()
    tasks, tid = [], 0
    for sc in scen:                                                     # Type I, all 18
        for ch in range(CH):
            tasks.append(("type1", tid, sc, R0 // CH, B, ch))
        tid += 1
    for d, R in NK.cells():                                             # near-kink Type I
        sc = dict(id=f"N{d:+.2f}", desc=f"near-kink gap d = {d:+.2f}", d0=0.0, repo=R, mode="nk")
        for ch in range(max(1, CH // 2)):
            tasks.append(("nearkink", tid, sc, RK // max(1, CH // 2), B, ch))
        tid += 1
    for sc in scen:                                                     # power versions of all 18
        s2 = _shift(sc, 0.05)
        s2["id"] = sc["id"] + "+"
        for ch in range(max(1, CH // 2)):
            tasks.append(("power", tid, s2, RP // max(1, CH // 2), B, ch))
        tid += 1
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=16) as ex:
        res = list(ex.map(run_task, tasks))
    rows = aggregate(res)
    sfx = "_quick" if quick else ""
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("kind", "id", "description"), k))
    with (OUT / f"calib_v12pp{sfx}.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    write_md(rows, R0, RK, RP, B, sfx, time.time() - t0)
    print(f"done in {time.time() - t0:.0f} s")


def _f(x):
    return f"{x:.4f}"


def write_md(rows, R0, RK, RP, B, sfx, secs):
    L = ["# V12'' complete-procedure calibration (PROPOSED, NOT ADOPTED; simulated planning figures, not results)", "",
         f"`scripts/calib_v12pp.py`; B = {B}; Type I {R0} data sets per scenario, near-kink {RK}, power {RP}; 7 repositories x 30 sites; "
         f"run time {secs / 60:.1f} min. Procedure: script docstring. Holm levels for m = 3: a/3 = 0.00833, a/2 = 0.0125, a = 0.025.", "",
         "Two bootstrap variants were run on the **same** resamples of every data set; the point estimate is the exact tie-average in both:",
         "- **RK** (recommended primary): re-matching bootstrap with fresh uniform tie keys inside each resample (ties averaged in distribution), "
         "percentile p, coverage-gap guard (p -> 2p if g < 0.10). **RK claim** = RK rejection that also passes the feasibility gate.",
         "- **TA** (rejected alternative): re-matching bootstrap of the exact tie-averaged estimate itself, percentile p, same guard.", "",
         "## A. Type I error, scenarios S00-S17 (population delta = d0 exactly; S00 tests its own delta_true)", "",
         "| id | scenario | P(guard on) | P(gate) | RK a/3 | RK a/2 | RK a (MC SE) | RK claim a | RK unguarded a | TA a/3 | TA a (MC SE) |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] != "type1":
            continue
        L.append(f"| {r['id']} | {r['description']} | {r['p_guard_on']:.3f} | {r['p_gate']:.3f} | {_f(r['rej_rkg_a3'])} | {_f(r['rej_rkg_a2'])} | "
                 f"{_f(r['rej_rkg_a1'])} ({r['mcse_a1']:.4f}) | {_f(r['rej_rkclaim_a1'])} | {_f(r['rej_rk_a1'])} | {_f(r['rej_guard_a3'])} | "
                 f"{_f(r['rej_guard_a1'])} ({r['mcse_ta_a1']:.4f}) |")
    L += ["", "## B. Type I error near equal natural coverage (population gap d = cov_F - cov_M)", "",
          "| cell | P(guard on) | RK a/3 | RK a/2 | RK a (MC SE) | RK unguarded a/3 | RK unguarded a | TA a/3 | TA a/2 | TA a (MC SE) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] != "nearkink":
            continue
        L.append(f"| {r['description']} | {r['p_guard_on']:.3f} | {_f(r['rej_rkg_a3'])} | {_f(r['rej_rkg_a2'])} | {_f(r['rej_rkg_a1'])} ({r['mcse_a1']:.4f}) | "
                 f"{_f(r['rej_rk_a3'])} | {_f(r['rej_rk_a1'])} | {_f(r['rej_guard_a3'])} | {_f(r['rej_guard_a2'])} | {_f(r['rej_guard_a1'])} ({r['mcse_ta_a1']:.4f}) |")
    L += ["", "## C. Power, the same 18 scenarios with the population delta at about +0.05", "",
          "(S00: its own delta_true, tested against 0; S13/S14: heterogeneous pattern + 0.05 capped at 0.12; S16: superpopulation mean about +0.05 (truncation); S17: delta 0.12 against d0 = 0.10.)", "",
          "| id | pop. delta | P(guard on) | P(gate) | RK power a/3 | RK power a | RK claim power a | RK unguarded power a | TA power a |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] != "power":
            continue
        if "error" in r:
            L.append(f"| {r['id']} | not reachable in this model ({r['error'][:60]}) | | | | | | | |"); continue
        L.append(f"| {r['id']} | {r['pop_delta']:+.4f} | {r['p_guard_on']:.3f} | {r['p_gate']:.3f} | {r['rej_rkg_a3']:.3f} | "
                 f"{r['rej_rkg_a1']:.3f} | {r['rej_rkclaim_a1']:.3f} | {r['rej_rk_a1']:.3f} | {r['rej_guard_a1']:.3f} |")
    (OUT / f"calib_v12pp{sfx}.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
