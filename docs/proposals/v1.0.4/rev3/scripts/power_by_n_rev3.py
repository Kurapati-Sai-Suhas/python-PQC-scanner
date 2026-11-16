"""Does adding sites per repository rescue the literal-margin H2 test with only 7 test repositories?
Repository-level t test of H0: delta <= 0.10, one-sided; Monte Carlo (seed 20261113). PROPOSED rev3; not results.
Writes ../results/power_by_n_rev3.md."""
from pathlib import Path
from stats_rev3 import simulate, cluster_t_p_upper

OUT = Path(__file__).resolve().parents[1] / "results"
lines = ["# Literal-margin power vs. sites per repository (7 repositories; simulated; not results)", "",
         "| true delta | discordance | tau | sites per repo | power a=.025 | power a=.025/3 |", "|---|---|---|---|---|---|"]
for delta in (0.15, 0.20, 0.25):
    for pd, tau in ((0.30, 0.0), (0.30, 0.05), (0.30, 0.10)):
        for n in (30, 60, 100):
            b, c = simulate(delta, pd, tau, K=7, n=n, reps=4000, seed=20261113)
            dr = (b - c) / n
            p = cluster_t_p_upper(dr, 0.10)
            lines.append(f"| {delta:.2f} | {pd:.2f} | {tau:.2f} | {n} | {(p <= .025).mean():.3f} | {(p <= .025/3).mean():.3f} |")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "power_by_n_rev3.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
