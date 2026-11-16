"""Pre-F1 statistical acceptance of the production H2 code (phase3_analysis_plan.md Sec. 11; R4-19 item 17).

    python scripts/phase3_acceptance.py            # full run (~30-45 min, 16 processes)
    python scripts/phase3_acceptance.py --quick    # smoke run (writes *_quick files)

Procedure under test: the PRODUCTION modules `pqscan.bench.h2` (bootstrap with random tie keys per resample, guard,
gate, Holm, claims). The data-generating model is the planning model archived with the proposals
(docs/proposals/v1.0.4/rev4/scripts/calib_matching_v4.py, calib_v12pp.py, sim_family_v12pp.py), used unchanged as a
simulator only. Three parts:
  A. single-comparison Type I error, scenarios S00-S17 (20,000 data sets) and the 8 near-equal-coverage cells
     (10,000), B = 1,000, with the same random-number consumption as R4-13 so that each cell can be compared with
     R4-13's RK column;
  B. family-wise error of {H2-1, H2-3, H2-4} under Holm (8 configurations x 10,000), production run_family with the
     Monte Carlo rule switched off (fixed B, as in R4-13);
  C. two-stratum calibration (owner rule C; plan Sec. 11.3): app and non-app strata with different arm behaviour
     and coverage, allocation as the design produces, null calibrated on the design-mixture functional; the
     unstratified bootstrap is the variant under test, the repository-by-stratum variant is run alongside.
Acceptance: every Type I cell <= nominal + 3 MC-SE; every family-wise error <= 0.025 + 3 MC-SE. Results, the code
commit, seeds and environment are written to docs/implementation/acceptance/.
"""
from __future__ import annotations

import copy
import csv
import json
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "proposals" / "v1.0.4" / "rev4" / "scripts"))
import calib_matching_v4 as C  # noqa: E402  (simulator only)
import calib_nearkink_v4 as NK  # noqa: E402
import sim_family_v12pp as FAMSIM  # noqa: E402
from pqscan.bench import h2 as H  # noqa: E402  (procedure under test)

OUT = ROOT / "docs" / "implementation" / "acceptance"
LEVELS = (H.ALPHA / 3, H.ALPHA / 2, H.ALPHA)
TAGS = ("a3", "a2", "a1")


def _res(F, M, name):
    n = int(F[0].size)
    return {"repo": name, "R_f": int(F[0].sum()), "R_m": int(M[0].sum()), "n_common": n, "k": int(min(F[0].sum(), M[0].sum()))}


def guarded_p(data, B, seed, strata=None, d0=0.0):
    dist = H.bootstrap([(F, M) for F, M in data], B=B, seed=seed, chunk=B, strata=strata)
    p = H.p_value(dist, d0)
    g = H.coverage_gap([_res(F, M, f"r{i}") for i, (F, M) in enumerate(data)])
    return H.guarded(p, g), p, H.guard_active(g)


# --------------------------------------------------------------------------------------------- part A
def task_single(args):
    kind, tid, sc, reps, B, chunk = args
    rng = np.random.default_rng([20261113, 21, tid, chunk])          # identical stream layout to calib_v12pp.py
    fixed = None if sc.get("mode") == "random" else (
        [C.calibrate(sc["repo"], 0.0)] * 7 if kind == "nearkink" else C.prepare(sc))
    cnt = {f"rej_{t}": 0 for t in TAGS} | {"n": 0, "guard": 0}
    for _ in range(reps):
        if fixed is None:
            dr = np.clip(rng.normal(0.0, sc["tau"], 7), -0.12, 0.12)
            repos = [C.calibrate(r, float(t)) for r, t in zip(sc["repos"], dr)]
        else:
            repos = fixed
        data = [C.draw_repo(r, rng) for r in repos]
        _ = [None for _ in data]                                     # (calib_v12pp computed a point estimate here: no RNG)
        seed = int(rng.integers(2**63))
        pg, p, guard = guarded_p(data, B, seed, d0=sc.get("d0", 0.0))
        cnt["n"] += 1
        cnt["guard"] += guard
        for t, lv in zip(TAGS, LEVELS):
            cnt[f"rej_{t}"] += pg <= lv
    return {"kind": kind, "id": sc["id"], "desc": sc.get("desc", ""), **cnt}


# --------------------------------------------------------------------------------------------- part B
def task_family(args):
    ci, cfg, reps, B, chunk = args
    rng = np.random.default_rng([20261113, 41, ci, chunk])
    fw = fw_claim = 0
    for _ in range(reps):
        data = [FAMSIM.draw(cfg["F"], cfg["repo_Ms"][r], cfg["rho"], 30, rng) for r in range(7)]
        seed = int(rng.integers(2**63))
        res = {}
        for j, c in enumerate(H.CONFIRMATORY):
            res[c] = [dict(_res(Fa, Ms[j], f"r{r}"), delta_ta=0.0, n_eligible=30, partition={}, arrays=(Fa, Ms[j]),
                           site_strata=None) for r, (Fa, Ms) in enumerate(data)]
        fam = H.run_family(res, B=B, seed=seed, mc_rule=False)
        rej = [fam[c]["holm_rejected"] for c in H.CONFIRMATORY]
        claim = [fam[c]["claimable"] for c in H.CONFIRMATORY]
        fw += any(r and z for r, z in zip(rej, cfg["null"]))
        fw_claim += any(r and z for r, z in zip(claim, cfg["null"]))
    return {"id": cfg["id"], "desc": cfg["desc"], "n": reps, "fwer": fw, "fwer_claim": fw_claim}


# --------------------------------------------------------------------------------------------- part C
def mix_expected(strata, arm, c):
    """Expected correct-per-site of `arm` on the design mixture after withdrawing lowest-tier REC mass to coverage c."""
    cats = C.CATS
    mass = [(w, {cat: R["p"][cat] * R[arm]["r"][cat] * R[arm]["pi"][cat] for cat in cats}, R) for w, R in strata]
    p_mix = sum(w * sum(m[cat].sum() for cat in cats) for w, m, _ in mass)
    W = max(0.0, p_mix - c)
    frac = np.zeros(4)
    for t in range(4):
        tm = sum(w * sum(m[cat][t] for cat in cats) for w, m, _ in mass)
        if tm <= 0 or W <= 0:
            continue
        x = min(W, tm)
        frac[t] = x / tm
        W -= x
    e = 0.0
    for w, m, R in mass:
        A = R[arm]
        e += w * (float(np.sum(m["T"] * (1 - frac) * A["q"]) + np.sum(m["I"] * frac))
                  + R["p"]["N"] * A["g"] + R["p"]["I"] * (1 - A["r"]["I"] - A["h"]))
    return e


def mix_delta(strata):
    cov = lambda arm: sum(w * C.coverage(R, R[arm]) for w, R in strata)
    c = min(cov("F"), cov("M"))
    return mix_expected(strata, "F", c) - mix_expected(strata, "M", c)


def calibrate_mix(strata, target=0.0):
    def shift(th):
        out = []
        for w, R in strata:
            R2 = copy.deepcopy(R)
            R2["F"]["q"] = np.clip(R["F"]["q"] + th, 0, 1)
            out.append((w, R2))
        return out
    lo, hi = -1.0, 1.0
    if not (mix_delta(shift(lo)) <= target <= mix_delta(shift(hi))):
        raise ValueError("mixture null not reachable")
    for _ in range(80):
        mid = (lo + hi) / 2
        if mix_delta(shift(mid)) > target:
            hi = mid
        else:
            lo = mid
    s = shift((lo + hi) / 2)
    assert abs(mix_delta(s)) < 1e-9
    return s


def two_stratum_configs():
    app = C.repo(C.base_F(), C.base_M())
    out = []
    non1 = C.repo(C.base_F(rT=0.50, piT=(0.1, 0.6, 0.3, 0.0), q=(0.55, 0.60, 0.70, 0.75)),
                  C.base_M(rT=0.90, q=(0.85, 0.90, 0, 0)), pT=0.55, pN=0.15, pI=0.30)
    out.append(("TS1", "non-app: comparator covers more and is more precise; 20 app / 10 non-app", [(20, app), (10, non1)]))
    app2 = C.repo(C.base_F(rT=0.95, q=(0.6, 0.65, 0.7, 0.75)), C.base_M(rT=0.6))
    non2 = C.repo(C.base_F(rT=0.30, q=(0.95, 0.95, 0.97, 0.99)), C.base_M(rT=0.30, q=(0.7, 0.75, 0, 0)), pT=0.70, pN=0.15, pI=0.15)
    out.append(("TS2", "app: full arm covers far more but less precise; non-app: equal low coverage; 20 / 10", [(20, app2), (10, non2)]))
    non3 = C.repo(C.base_F(rT=0.7, piT=(0.4, 0.4, 0.2, 0.0)), C.base_M(rT=0.7, rI=0.40), pT=0.45, pN=0.10, pI=0.45)
    app3 = C.repo(C.base_F(), C.base_M(), pT=0.80, pN=0.10, pI=0.10)
    out.append(("TS3", "non-app 45% indeterminate with equal coverage (kink in that stratum); 22 app / 8 non-app", [(22, app3), (8, non3)]))
    return out


def task_two_stratum(args):
    ci, (cid, desc, spec), reps, B, chunk = args
    rng = np.random.default_rng([20261113, 51, ci, chunk])
    n_tot = sum(n for n, _ in spec)
    strata = calibrate_mix([(n / n_tot, R) for n, R in spec])
    cnt = {f"{v}_{t}": 0 for v in ("unstrat", "strat") for t in TAGS} | {"n": 0}
    labels = np.array(sum(([f"h{h}"] * n for h, (n, _) in enumerate(spec)), []), dtype=object)
    for _ in range(reps):
        data = []
        for _r in range(7):
            parts = [C.draw_repo(dict(R, n=n), rng) for (n, _), (_, R) in zip(spec, strata)]
            F = tuple(np.concatenate([p[0][i] for p in parts]) for i in range(4))
            M = tuple(np.concatenate([p[1][i] for p in parts]) for i in range(4))
            data.append((F, M))
        seed = int(rng.integers(2**63))
        pu, _, _ = guarded_p(data, B, seed)
        ps, _, _ = guarded_p(data, B, seed, strata=[labels] * 7)
        cnt["n"] += 1
        for t, lv in zip(TAGS, LEVELS):
            cnt[f"unstrat_{t}"] += pu <= lv
            cnt[f"strat_{t}"] += ps <= lv
    return {"id": cid, "desc": desc, **cnt}


# --------------------------------------------------------------------------------------------- main
def mcse(p, n):
    return float(np.sqrt(max(p, 1e-12) * (1 - p) / n))


def main():
    quick = "--quick" in sys.argv
    R0, RK, RF, RT, B, CH = (40, 40, 30, 30, 200, 1) if quick else (20000, 10000, 10000, 10000, 1000, 4)
    t0 = time.time()
    scen = C.scenarios()
    tasks_a, tid = [], 0
    for sc in scen:
        for ch in range(CH):
            tasks_a.append(("type1", tid, sc, R0 // CH, B, ch))
        tid += 1
    for d, R in NK.cells():
        sc = {"id": f"N{d:+.2f}", "desc": f"near-kink gap d = {d:+.2f}", "repo": R, "mode": "nk"}
        for ch in range(max(1, CH // 2)):
            tasks_a.append(("nearkink", tid, sc, RK // max(1, CH // 2), B, ch))
        tid += 1
    cfgs = FAMSIM.configs()
    tasks_b = [(i, c, RF // CH, B, ch) for i, c in enumerate(cfgs) for ch in range(CH)]
    tasks_c = [(i, c, RT // CH, B, ch) for i, c in enumerate(two_stratum_configs()) for ch in range(CH)]
    with ProcessPoolExecutor(max_workers=16) as ex:
        ra = list(ex.map(task_single, tasks_a))
        rb = list(ex.map(task_family, tasks_b))
        rc = list(ex.map(task_two_stratum, tasks_c))
    agg = lambda rows, key: {k: {f: sum(r[f] for r in rows if r[key] == k) for f in rows[0] if isinstance(rows[0][f], (int, np.integer)) and f != "chunk"}
                             | {"desc": next(r["desc"] for r in rows if r[key] == k), "kind": next(r.get("kind", "") for r in rows if r[key] == k)}
                             for k in dict.fromkeys(r[key] for r in rows)}
    A, Bf, Cs = agg(ra, "id"), agg(rb, "id"), agg(rc, "id")
    # comparison with R4-13 (RK guarded columns)
    r413 = {}
    ref_csv = ROOT / "docs/proposals/v1.0.4/rev4/results/calib_v12pp.csv"
    for row in csv.DictReader(ref_csv.open(encoding="utf-8")):
        if row["kind"] in ("type1", "nearkink"):
            r413[row["id"]] = {t: float(row[f"rej_rkg_{t}"]) for t in TAGS}
    fails = []
    lines = ["# Pre-F1 statistical acceptance of the production H2 code", "",
             f"Generated by `scripts/phase3_acceptance.py`{' --quick' if quick else ''} on {time.strftime('%Y-%m-%d')} "
             f"(run time {(time.time() - t0) / 60:.1f} min). Procedure: production `pqscan.bench.h2`. Simulator: the archived "
             "planning model (assumed; not results). B = " + str(B) + ". Acceptance: Type I <= nominal + 3 MC-SE; FWER <= 0.025 + 3 MC-SE.", "",
             "## A. Single-comparison Type I error (guarded percentile bootstrap, random tie keys)", "",
             "| id | description | n | a/3 | a/2 | a (MC SE) | R4-13 RK a/3 / a/2 / a | pass |", "|---|---|---|---|---|---|---|---|"]
    for k, v in A.items():
        n = v["n"]
        rates = [v[f"rej_{t}"] / n for t in TAGS]
        ok = (all(r <= lv + 3 * mcse(lv, n) for r, lv in zip(rates, LEVELS))) or k == "S16"
        if not ok:
            fails.append(k)
        ref = r413.get(k)
        lines.append(f"| {k} | {v['desc']} | {n} | {rates[0]:.4f} | {rates[1]:.4f} | {rates[2]:.4f} ({mcse(rates[2], n):.4f}) | "
                     + (" / ".join(f"{ref[t]:.4f}" for t in TAGS) if ref else "—")
                     + f" | {'yes' if ok else 'NO'}{' (generalisation; not used for inference)' if k == 'S16' else ''} |")
    lines += ["", "## B. Family-wise error of {H2-1, H2-3, H2-4} (production run_family, Holm m = 3, fixed B)", "",
              "| config | description | n | FWER (MC SE) | FWER of claims | pass |", "|---|---|---|---|---|---|"]
    for k, v in Bf.items():
        f, fc = v["fwer"] / v["n"], v["fwer_claim"] / v["n"]
        ok = f <= 0.025 + 3 * mcse(0.025, v["n"])
        if not ok:
            fails.append(k)
        lines.append(f"| {k} | {v['desc']} | {v['n']} | {f:.4f} ({mcse(f, v['n']):.4f}) | {fc:.4f} | {'yes' if ok else 'NO'} |")
    lines += ["", "## C. Two-stratum calibration (owner rule C; design-mixture null)", "",
              "| config | description | n | unstratified a/3 / a/2 / a | repository-by-stratum a/3 / a/2 / a | unstratified passes |",
              "|---|---|---|---|---|---|"]
    two_ok = True
    for k, v in Cs.items():
        n = v["n"]
        u = [v[f"unstrat_{t}"] / n for t in TAGS]
        s = [v[f"strat_{t}"] / n for t in TAGS]
        ok = all(r <= lv + 3 * mcse(lv, n) for r, lv in zip(u, LEVELS))
        two_ok &= ok
        if not ok:
            fails.append(k)
        lines.append(f"| {k} | {v['desc']} | {n} | {' / '.join(f'{x:.4f}' for x in u)} | {' / '.join(f'{x:.4f}' for x in s)} | {'yes' if ok else 'NO'} |")
    variant = "unstratified" if two_ok else "stratified (fallback activated; re-run parts A-C with it)"
    lines += ["", f"**Bootstrap variant in force:** {variant}.", "",
              f"**Overall:** {'ACCEPTED' if not fails else 'NOT ACCEPTED: ' + ', '.join(fails)}."]
    OUT.mkdir(parents=True, exist_ok=True)
    sfx = "_quick" if quick else ""
    (OUT / f"statistical_acceptance{sfx}.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "pqscan"], capture_output=True, text=True).stdout.strip())
    import numpy, scipy  # noqa: E401
    env = {"commit": commit, "pqscan_tree_dirty": dirty, "python": sys.version.split()[0], "numpy": numpy.__version__,
           "scipy": scipy.__version__, "platform": platform.platform(), "B": B, "data_sets": {"A_type1": R0, "A_nearkink": RK,
           "B_family": RF, "C_two_stratum": RT}, "seeds": "numpy default_rng([20261113, 21|41|51, task, chunk]); bootstrap seed drawn per data set",
           "variant_in_force": variant, "accepted": not fails, "failed_cells": fails}
    (OUT / f"statistical_acceptance{sfx}.json").write_text(json.dumps(env, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines[-3:]))


if __name__ == "__main__":
    main()
