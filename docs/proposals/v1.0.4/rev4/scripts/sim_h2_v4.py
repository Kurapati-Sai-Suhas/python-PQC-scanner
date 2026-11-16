"""Type I error and power grid for the H2 tests (PROPOSED rev4; simulated planning figures, not results).

    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/sim_h2_v4.py

Design: 7 repositories x 30 eligible sites. Two inference modes:
  fixed  - repository effects delta_r held FIXED across replicates (inference about the 7 selected repositories);
  random - delta_r = delta + tau * u_r redrawn every replicate (inference about a superpopulation of repositories).
Heterogeneity shapes: normal; skewed (fixed: six equal repositories plus one outlier; random: centred exponential).
Type I: delta at the null boundary (0 for step 1, 0.10 for step 2); tau in {0, .05, .10, .15}; pd in {.2, .3, .4}.
Power: delta in {.10, .15, .20, .25} (cells with delta > pd are infeasible and skipped); tau in {0, .05, .10}.
One-sided alpha levels: .025 (nominal family level), .025/3 and .025/4 (worst Holm steps for m = 3 or 4).
Outputs: ../results/h2_type1.csv, h2_power.csv and h2_tables.md. Seeds: 20261113 + cell index.
"""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
import stats_v4 as S

OUT = Path(__file__).resolve().parents[1] / "results"
REPS = 4000
ALPHAS = {"a=.025": 0.025, "a=.025/3": 0.025 / 3, "a=.025/4": 0.025 / 4}


def effects(mode, kind, delta, tau, pd, reps, rng):
    if mode == "fixed":
        dr, est = S.fixed_heterogeneity(delta, tau, pd, kind)
        return np.tile(dr, (reps, 1)), est
    u = rng.normal(0, 1, (reps, 7)) if kind == "normal" else (rng.exponential(1.0, (reps, 7)) - 1.0)
    dr = np.clip(delta + tau * u, -pd, pd)
    return dr, float(dr.mean())


def run_cell(mode, kind, delta, tau, pd, d0, seed, reps=REPS, wilcoxon=False):
    rng = np.random.default_rng(seed)
    dr, est = effects(mode, kind, delta, tau, pd, reps, rng)
    b, c = S.draw_pairs(dr, pd, 30, rng)
    B, C = b.sum(1), c.sum(1)
    rd = (b - c) / 30
    p = {"site": S.mcnemar_exact_p_upper(B, C) if d0 == 0 else S.tango_p_upper(B, C, 210, d0),
         "repo_t": S.repo_t_p_upper(rd, d0), "repo_signflip": S.signflip_p_upper(rd, d0)}
    if wilcoxon:
        p["repo_wilcoxon"] = S.wilcoxon_exact_p_upper(rd, d0)
    return est, p


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t1, pw = [], []
    i = 0
    for mode in ("fixed", "random"):
        for kind in ("normal", "skewed"):
            for d0 in (0.0, 0.10):
                for pd in (0.2, 0.3, 0.4):
                    for tau in (0.0, 0.05, 0.10, 0.15):
                        i += 1
                        est, p = run_cell(mode, kind, d0, tau, pd, d0, 20261113 + i, reps=REPS, wilcoxon=True)
                        t1.append({"mode": mode, "shape": kind, "null_boundary": d0, "pd": pd, "tau": tau,
                                   "estimand_after_clip": round(est, 4),
                                   **{f"{k}@.025": round(float((v <= 0.025).mean()), 4) for k, v in p.items()}})
        for delta in (0.10, 0.15, 0.20, 0.25):
            for pd in (0.2, 0.3, 0.4):
                if delta > pd:
                    continue
                for tau in (0.0, 0.05, 0.10):
                    i += 1
                    row = {"mode": mode, "delta": delta, "pd": pd, "tau": tau}
                    for d0, step in ((0.0, "step1"), (0.10, "step2")):
                        est, p = run_cell(mode, "normal", delta, tau, pd, d0, 20261113 + i)
                        row["estimand_after_clip"] = round(est, 4)
                        for k, v in p.items():
                            for an, a in ALPHAS.items():
                                row[f"{step}:{k}@{an}"] = round(float((v <= a).mean()), 3)
                    pw.append(row)
    for name, rows in (("h2_type1.csv", t1), ("h2_power.csv", pw)):
        with (OUT / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    md = ["# H2 Type I error and power (simulated, PROPOSED rev4; planning figures, not results)", "",
          f"{REPS} replicates per cell; Monte Carlo SE at a true rate of 0.025 is about 0.0025.", "",
          "## Type I error at the null boundary (one-sided nominal alpha 0.025)", "",
          "Columns: site = pooled exact McNemar (boundary 0) or pooled Tango score test (boundary 0.10); repo_* = repository-level tests.", ""]
    keys = list(t1[0])
    md += ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
    md += ["| " + " | ".join(str(r[k]) for k in keys) + " |" for r in t1]
    md += ["", "## Power (normal heterogeneity); step1 = H0 delta <= 0, step2 = H0 delta <= 0.10", ""]
    keys = list(pw[0])
    md += ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
    md += ["| " + " | ".join(str(r[k]) for k in keys) + " |" for r in pw]
    (OUT / "h2_tables.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {len(t1)} Type I rows and {len(pw)} power rows")


if __name__ == "__main__":
    main()
