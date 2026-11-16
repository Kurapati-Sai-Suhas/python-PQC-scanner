"""Family-wise error of the complete V12'' procedure for the confirmatory family F-B = {H2-1, H2-3, H2-4}
(R4-13 Sec. D). PROPOSED, NOT ADOPTED. Simulated planning figures, not results.

    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/sim_family_v12pp.py [--quick]

One full arm F and three comparators M1 (method+args-like: tiers T0/T1), M2 (method+args+recv-like: T0-T2) and
M3 (method-only-like: T0/T1) are drawn jointly on the same sites (shared site truth; each comparator shares F's
action/tier/correctness uniforms with probability rho_j, which correlates the three comparisons through F).
Each comparator is calibrated (bisection on its own correctness, so F is common to all) to a stated population
matched delta against F. For every data set the full V12'' procedure runs per comparison -- natural coverage,
guard, within-repository matching, tier withdrawal, frozen-model scoring, re-matching bootstrap (the same resample
indices and tie keys for the three comparisons, as with one seed; RK = random tie keys, recommended; TA = exact
tie-averaging inside resamples, rejected), percentile p, guarded p -- and then Holm
(m = 3) at one-sided family alpha 0.025. FWER = P(at least one true null rejected).
Seeds: numpy default_rng([20261113, 31, config index, chunk]).
"""
from __future__ import annotations

import copy
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calib_matching_v4 as C  # noqa: E402
import matching_ref_v4 as MR  # noqa: E402

ALPHA = 0.025
P_CAT = dict(T=0.75, N=0.10, I=0.15)


def M1(**kw):
    return C.base_M(**kw)


def M2(**kw):
    a = dict(rT=0.70, piT=(0.05, 0.45, 0.50, 0), q=(0.70, 0.80, 0.88, 0), rN=0.10, piN=(0.1, 0.5, 0.4, 0), g=0.50,
             rI=0.25, piI=(0.2, 0.5, 0.3, 0), h=0.02)
    a.update(kw)
    return C.arm(**a)


def M3(**kw):
    a = dict(rT=0.45, piT=(0.55, 0.45, 0, 0), q=(0.72, 0.80, 0, 0), rN=0.05, piN=(0.5, 0.5, 0, 0), g=0.20,
             rI=0.15, piI=(0.5, 0.5, 0, 0), h=0.0)
    a.update(kw)
    return C.arm(**a)


def calibrate_M(F, M, target, p=P_CAT):
    """Shift the comparator's recommendation correctness q and its FLAG_NO_TARGET correctness g together by theta
    (delta decreases monotonically in theta) so that pop_delta(F, M) = target. F is never changed (it is shared)."""
    def make(th):
        M2_ = copy.deepcopy(M)
        M2_["q"] = np.clip(M["q"] + th, 0, 1) * (M["q"] > 0)
        M2_["g"] = float(np.clip(M["g"] + th, 0, 1 - M["r"]["N"]))
        return C.repo(F, M2_, pT=p["T"], pN=p["N"], pI=p["I"])
    lo, hi = -1.0, 1.0
    flo, fhi = C.pop_delta(make(lo)) - target, C.pop_delta(make(hi)) - target
    if not (flo >= 0 >= fhi):
        raise ValueError(f"target {target} unreachable by tuning the comparator: [{fhi + target:.3f}, {flo + target:.3f}]")
    for _ in range(80):
        mid = (lo + hi) / 2
        if C.pop_delta(make(mid)) - target > 0:
            lo = mid
        else:
            hi = mid
    R = make((lo + hi) / 2)
    assert abs(C.pop_delta(R) - target) < 1e-9
    return R["M"]


def configs():
    F = C.base_F()
    het = np.array([-3, -2, -1, 0, 1, 2, 3]) / 2.0
    out = [
        dict(id="C1", desc="global null; comparator coverages 0.40 / 0.58 / 0.36; rho 0.5",
             Ms=(M1(), M2(), M3()), targets=(0, 0, 0), rho=(0.5, 0.5, 0.5)),
        dict(id="C2", desc="global null; H2-3 comparator at equal natural coverage (guard on for H2-3)",
             Ms=(M1(), M2(rT=0.85, rN=0.10, rI=0.30), M3()), targets=(0, 0, 0), rho=(0.5, 0.5, 0.5)),
        dict(id="C3", desc="global null; strong dependence (rho 0.9 for all three)",
             Ms=(M1(), M2(), M3()), targets=(0, 0, 0), rho=(0.9, 0.9, 0.9)),
        dict(id="C4", desc="partial null: H2-1 null; H2-3 and H2-4 true delta +0.08",
             Ms=(M1(), M2(), M3()), targets=(0, 0.08, 0.08), rho=(0.5, 0.5, 0.5)),
        dict(id="C5", desc="partial null: H2-3 null at equal coverage (guard); H2-1 and H2-4 true delta +0.08",
             Ms=(M1(), M2(rT=0.85, rN=0.10, rI=0.30), M3()), targets=(0.08, 0, 0.08), rho=(0.5, 0.5, 0.5)),
        dict(id="C6", desc="global null; low comparator coverage (gate often fails)",
             Ms=(M1(rT=0.15, rI=0.05), M2(rT=0.20, rI=0.05), M3(rT=0.12, rI=0.05)), targets=(0, 0, 0), rho=(0.5, 0.5, 0.5)),
        dict(id="C7", desc="global null on average; fixed repository heterogeneity tau 0.015 (delta_r -0.0225 to +0.0225; larger is not reachable for every comparator in this model), different pattern per comparison",
             Ms=(M1(), M2(), M3()), targets=(0, 0, 0), rho=(0.5, 0.5, 0.5), het=(het, het[::-1], np.roll(het, 3))),
        dict(id="C8", desc="partial null with H2-1 comparator above the full arm's coverage (guard on); others +0.08",
             Ms=(M1(rT=1.0, rN=0.10, rI=0.30), M2(), M3()), targets=(0, 0.08, 0.08), rho=(0.5, 0.5, 0.5)),
    ]
    for c in out:
        c["F"] = F
        reps = []
        for r in range(7):
            ms = []
            for j, (M, t) in enumerate(zip(c["Ms"], c["targets"])):
                tt = t + (0.015 * c["het"][j][r] if "het" in c else 0.0)
                ms.append(calibrate_M(F, M, tt))
            reps.append(ms)
        c["repo_Ms"] = reps
        c["null"] = tuple(t == 0 for t in c["targets"])
    return out


def draw(F, Ms, rhos, n, rng):
    p = np.array([P_CAT["T"], P_CAT["N"], P_CAT["I"]])
    cat = np.minimum((rng.random(n)[:, None] > np.cumsum(p)[None, :]).sum(1), 2)
    uF = rng.random((3, n))
    Fa = C._draw_arm(F, cat, *uF)
    out = []
    for M, rho in zip(Ms, rhos):
        sh = rng.random(n) < rho
        uM = np.where(sh[None, :], uF, rng.random((3, n)))
        out.append(C._draw_arm(M, cat, *uM))
    return Fa, out


def run(args):
    ci, cfg, reps, B, chunk = args
    rng = np.random.default_rng([20261113, 31, ci, chunk])
    keys = ("fwer_guard", "fwer_noguard", "fwer_claim", "fwer_rk", "fwer_rk_noguard", "fwer_rk_claim")
    cnt = {k: 0 for k in keys}
    rej = np.zeros(3); rej_rk = np.zeros(3); guard_on = np.zeros(3); gate_ok = np.zeros(3)
    for _ in range(reps):
        data = [draw(cfg["F"], cfg["repo_Ms"][r], cfg["rho"], 30, rng) for r in range(7)]
        idx = [rng.integers(0, 30, size=(B, 30)) for _ in range(7)]          # one resample set, shared
        pg, pu, gates, pgr, pur = [], [], [], [], []
        keys_rk = [(rng.random((B, 30)), rng.random((B, 30))) for _ in range(7)]   # tie keys, shared by the comparisons
        for j in range(3):
            pairs = [(Fa, Ms[j]) for Fa, Ms in data]
            RF = [int(F[0].sum()) for F, _ in pairs]; RM = [int(M[0].sum()) for _, M in pairs]
            g = MR.coverage_gap(RF, RM, [30] * 7)
            dist = np.mean([MR.tie_average_batch(F, M, ix)[0] for (F, M), ix in zip(pairs, idx)], axis=0)
            p = (1 + np.count_nonzero(dist <= 1e-12)) / (B + 1)
            pg.append(MR.guarded_p(p, g)); pu.append(p)
            drk = np.mean([MR.matched_delta_batch(F, M, ix, kf, km)[0] for (F, M), ix, (kf, km) in zip(pairs, idx, keys_rk)], axis=0)
            prk = (1 + np.count_nonzero(drk <= 1e-12)) / (B + 1)
            pgr.append(MR.guarded_p(prk, g)); pur.append(prk)
            gates.append(MR.feasibility([min(a, b) for a, b in zip(RF, RM)], [30] * 7)["passes"])
            guard_on[j] += MR.guard_active(g); gate_ok[j] += gates[-1]
        rg = [a <= ALPHA for a in MR.holm(pg)]
        ru = [a <= ALPHA for a in MR.holm(pu)]
        nulls = cfg["null"]
        cnt["fwer_guard"] += any(r and z for r, z in zip(rg, nulls))
        cnt["fwer_noguard"] += any(r and z for r, z in zip(ru, nulls))
        cnt["fwer_claim"] += any(r and z and gt for r, z, gt in zip(rg, nulls, gates))
        rej += np.array(rg, float)
        rgr = [a <= ALPHA for a in MR.holm(pgr)]
        rur = [a <= ALPHA for a in MR.holm(pur)]
        cnt["fwer_rk"] += any(r and z for r, z in zip(rgr, nulls))
        cnt["fwer_rk_noguard"] += any(r and z for r, z in zip(rur, nulls))
        cnt["fwer_rk_claim"] += any(r and z and gt for r, z, gt in zip(rgr, nulls, gates))
        rej_rk += np.array(rgr, float)
    return dict(id=cfg["id"], chunk=chunk, n=reps, **cnt, rej=rej, rej_rk=rej_rk, guard_on=guard_on, gate_ok=gate_ok)


def main():
    quick = "--quick" in sys.argv
    reps, B, CH = (30, 200, 1) if quick else (10000, 1000, 4)
    cfgs = configs()
    t0 = time.time()
    tasks = [(i, c, reps // CH, B, ch) for i, c in enumerate(cfgs) for ch in range(CH)]
    with ProcessPoolExecutor(max_workers=16) as ex:
        res = list(ex.map(run, tasks))
    agg = {}
    for r in res:
        a = agg.setdefault(r["id"], dict(n=0, fwer_guard=0, fwer_noguard=0, fwer_claim=0, fwer_rk=0, fwer_rk_noguard=0, fwer_rk_claim=0,
                                         rej=np.zeros(3), rej_rk=np.zeros(3), guard_on=np.zeros(3), gate_ok=np.zeros(3)))
        for k in ("n", "fwer_guard", "fwer_noguard", "fwer_claim", "fwer_rk", "fwer_rk_noguard", "fwer_rk_claim"):
            a[k] += r[k]
        for k in ("rej", "rej_rk", "guard_on", "gate_ok"):
            a[k] = a[k] + r[k]
    L = ["# V12'' family-wise error, confirmatory family {H2-1, H2-3, H2-4} (PROPOSED, NOT ADOPTED; simulated, not results)", "",
         f"`scripts/sim_family_v12pp.py`; {reps} data sets per configuration, B = {B}; 7 repositories x 30 sites; Holm m = 3 at one-sided "
         f"family alpha 0.025; run time {(time.time() - t0) / 60:.1f} min. MC SE at 0.025 about {np.sqrt(0.025 * 0.975 / reps):.4f}.", "",
         "FWER = P(at least one true null hypothesis rejected). **RK** = random-key re-matching bootstrap, guarded p into Holm "
         "(recommended primary). **TA** = bootstrap of the exact tie-averaged estimate, guarded (rejected alternative). "
         "**no guard** = raw p into Holm. **claims** = rejections that also pass the feasibility gate. Both variants use the same resamples.", "",
         "| config | description | true nulls (H2-1, H2-3, H2-4) | FWER RK (MC SE) | FWER RK no guard | FWER RK claims | FWER TA | FWER TA no guard | rejection rate per hypothesis (RK) | P(guard on) per hypothesis | P(gate passes) per hypothesis |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in cfgs:
        a = agg[c["id"]]; n = a["n"]
        fw = a["fwer_rk"] / n
        L.append(f"| {c['id']} | {c['desc']} | {', '.join('null' if z else 'alt' for z in c['null'])} | {fw:.4f} ({np.sqrt(max(fw, 1e-12) * (1 - fw) / n):.4f}) | "
                 f"{a['fwer_rk_noguard'] / n:.4f} | {a['fwer_rk_claim'] / n:.4f} | {a['fwer_guard'] / n:.4f} | {a['fwer_noguard'] / n:.4f} | "
                 + " / ".join(f"{x / n:.3f}" for x in a["rej_rk"]) + " | "
                 + " / ".join(f"{x / n:.3f}" for x in a["guard_on"]) + " | " + " / ".join(f"{x / n:.3f}" for x in a["gate_ok"]) + " |")
    sfx = "_quick" if quick else ""
    (C.OUT / f"family_v12pp{sfx}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
