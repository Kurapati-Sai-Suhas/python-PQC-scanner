"""Power / size grid for the H2 analysis options (protocol v1.0.4 revision 3, PROPOSED).

    .venv/Scripts/python docs/proposals/v1.0.4/rev3/scripts/power_rev3.py

Design: 7 test repositories x 30 eligible sites (the proposed quota), one-sided alpha 0.025 (equivalent to a two-sided
95% interval), and the worst Holm step for a family of 3 (alpha / 3). Scenario grid:
true delta in {0.10, 0.15, 0.20}; discordance pd in {0.20, 0.30, 0.40}; between-repository SD of the true difference
tau in {0, 0.05, 0.10}. Every number is a Monte Carlo estimate (reps per cell below, seed 20261113); none is a result.
Writes ../results/power_rev3.csv and ../results/power_rev3.md.
"""
from __future__ import annotations
import csv
from pathlib import Path
from stats_rev3 import simulate, decisions

REPS = 4000
OUT = Path(__file__).resolve().parents[1] / "results"
OPTIONS = ["A_site_mcnemar_pos", "A_site_mcnemar_pos_and_obs10", "A_cluster_t_pos_and_obs10", "S1_cluster_t_pos",
           "B_site_tango_margin", "B_cluster_t_margin", "B_cluster_signflip_margin"]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for delta in (0.10, 0.15, 0.20):
        for pd in (0.20, 0.30, 0.40):
            for tau in (0.0, 0.05, 0.10):
                b, c = simulate(delta, pd, tau, K=7, n=30, reps=REPS, seed=20261113)
                for label, alpha in (("a=.025", 0.025), ("a=.025/3", 0.025 / 3), ("a=.025/4", 0.025 / 4)):
                    dec = decisions(b, c, 30, alpha)
                    rows.append({"delta": delta, "pd": pd, "tau": tau, "alpha": label,
                                 **{k: round(float(dec[k].mean()), 3) for k in OPTIONS}})
    with (OUT / "power_rev3.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    hdr = "| true delta | discordance | tau | alpha | " + " | ".join(OPTIONS) + " |"
    lines = ["# H2 power and size grid (simulated; PROPOSED rev3; not results)", "",
             f"7 repositories x 30 sites; one-sided alpha; {REPS} replicates per cell; seed 20261113.",
             "Rows with true delta = 0.10 show the *size* (false-support rate) of the margin tests (B_*) and the power of the positive-difference tests (A_*).", "",
             hdr, "|" + "---|" * (4 + len(OPTIONS))]
    for r in rows:
        lines.append(f"| {r['delta']:.2f} | {r['pd']:.2f} | {r['tau']:.2f} | {r['alpha']} | " + " | ".join(f"{r[k]:.3f}" for k in OPTIONS) + " |")
    (OUT / "power_rev3.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
