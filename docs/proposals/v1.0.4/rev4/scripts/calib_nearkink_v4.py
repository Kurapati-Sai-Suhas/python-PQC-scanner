"""Near-kink follow-up to calib_matching_v4.py (R4-03 audit). PROPOSED, NOT ADOPTED. Not results.

    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/calib_nearkink_v4.py

Scenario S04 (equal natural coverage of the two arms) inflates the percentile re-matching bootstrap. This run moves
the comparator's population coverage below the full arm's by a gap d and records, at each gap:
  * the rejection rate of the percentile test at the Holm levels a/3, a/2, a;
  * the rejection rate of the same test at half those levels (the proposed guard, applied when the observed
    natural-coverage gap is small);
  * how often the label-free guard condition holds: pooled natural-coverage gap G = (sum R_F - sum R_M) / N < 0.10
    (the full arm does not exceed the comparator by at least 10 points); when it holds, Holm thresholds are halved.
  * for comparison, a per-repository diagnostic (some repository with |R_F - R_M| <= 3), which turned out to fire almost always.
Writes ../results/calib_nearkink.md and .csv. Same model, calibration and seeds scheme as calib_matching_v4.py.
"""
from __future__ import annotations

import csv
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calib_matching_v4 as C  # noqa: E402
import matching_ref_v4 as MR  # noqa: E402

LV = (C.ALPHA / 3, C.ALPHA / 2, C.ALPHA)
KINK_SITES = 3
G_MIN = 0.10


def cells():
    out = []
    for d in (0.0, 0.03, 0.07, 0.10, 0.15, 0.20):
        rT = 0.85 - d / 0.75
        out.append((d, C.repo(C.base_F(), C.base_M(rT=rT, rN=0.10, rI=0.30))))
    # gap of the other sign (comparator above the full arm)
    out.append((-0.07, C.repo(C.base_F(), C.base_M(rT=0.85 + 0.07 / 0.75, rN=0.10, rI=0.30))))
    out.append((-0.11, C.repo(C.base_F(), C.base_M(rT=1.0, rN=0.10, rI=0.30))))
    return out


def run(args):
    i, d, R, reps, B = args
    rng = np.random.default_rng([20261113, 11, i])
    R = C.calibrate(R, 0.0)
    rej = np.zeros(3); rej_half = np.zeros(3); rej_guard = np.zeros(3); fires = 0; repo_fires = 0; bias = []
    for _ in range(reps):
        data = [C.draw_repo(R, rng) for _ in range(7)]
        est, p, sd, ks, ns, gate, eta, pb, bm = C.analyse(data, B, rng, 0.0)
        gaps = np.array([abs(int(F[0].sum()) - int(M[0].sum())) for F, M in data])
        repo_fires += bool((gaps <= KINK_SITES).any())
        G = (sum(int(F[0].sum()) for F, M in data) - sum(int(M[0].sum()) for F, M in data)) / sum(F[0].size for F, M in data)
        fire = G < G_MIN
        fires += fire
        bias.append(eta)
        for j, a in enumerate(LV):
            rej[j] += p <= a
            rej_half[j] += p <= a / 2
            rej_guard[j] += p <= (a / 2 if fire else a)
    pF, pM = C.coverage(R, R["F"]), C.coverage(R, R["M"])
    return dict(gap=d, cov_F=pF, cov_M=pM, reps=reps, B=B, bias=float(np.mean(bias)), p_guard=fires / reps, p_repo_diag=repo_fires / reps,
                rej_a3=rej[0] / reps, rej_a2=rej[1] / reps, rej_a1=rej[2] / reps,
                half_a3=rej_half[0] / reps, half_a2=rej_half[1] / reps, half_a1=rej_half[2] / reps,
                guard_a3=rej_guard[0] / reps, guard_a2=rej_guard[1] / reps, guard_a1=rej_guard[2] / reps)


def main():
    reps, B = (10000, 1000) if "--quick" not in sys.argv else (100, 200)
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(run, [(i, d, R, reps, B) for i, (d, R) in enumerate(cells())]))
    sfx = "_quick" if "--quick" in sys.argv else ""
    with (C.OUT / f"calib_nearkink{sfx}.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    se = np.sqrt(0.025 * 0.975 / reps)
    L = ["# Near-kink calibration of the percentile re-matching bootstrap (PROPOSED, NOT ADOPTED; simulated, not results)", "",
         f"`scripts/calib_nearkink_v4.py`; {reps} data sets per row, B = {B}; base model of `calib_matching_v4.py` with the comparator's "
         f"coverage set below the full arm's (or above it, negative d) by the population gap d; population delta = 0 exactly. MC SE about {se:.4f} at 0.025. "
         f"Run time {(time.time() - t0) / 60:.1f} min.", "",
         f"Guard (label-free, pre-registered): if the pooled natural-coverage gap G = (sum R_F - sum R_M) / N is below "
         f"{G_MIN:.2f}, every Holm threshold for that comparison is halved. The per-repository diagnostic (any |R_F - R_M| <= "
         f"{KINK_SITES}) is shown for comparison only.", "",
         "| gap d | cov F | cov M | bias of estimate | P(guard on) | P(per-repo diag.) | rej a/3 | rej a/2 | rej a | at half level: a/6 | a/4 | a/2 | with guard: a/3 | a/2 | a |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['gap']:+.2f} | {r['cov_F']:.3f} | {r['cov_M']:.3f} | {r['bias']:+.4f} | {r['p_guard']:.3f} | {r['p_repo_diag']:.3f} | "
                 f"{r['rej_a3']:.4f} | {r['rej_a2']:.4f} | {r['rej_a1']:.4f} | {r['half_a3']:.4f} | {r['half_a2']:.4f} | {r['half_a1']:.4f} | "
                 f"{r['guard_a3']:.4f} | {r['guard_a2']:.4f} | {r['guard_a1']:.4f} |")
    (C.OUT / f"calib_nearkink{sfx}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
