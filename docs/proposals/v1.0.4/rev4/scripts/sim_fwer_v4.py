"""Family-wise Type I error of the F-B multiple-testing procedures (PROPOSED rev4; simulated, not results).

    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/sim_fwer_v4.py

Joint site model (shared full-arm outcome, so the three comparisons are positively dependent): per site,
X_full ~ Bernoulli(0.70); for comparator arm j, P(Y_j = 0 | X = 1) = (pd + d_j) / (2 * 0.70) and
P(Y_j = 1 | X = 0) = (pd - d_j) / (2 * 0.30), which gives discordance pd and difference d_j = P(X=1) - P(Y_j=1).
7 repositories x 30 sites; pd = 0.30; repository effects fixed (tau = 0.05, normal shape) for the site-level
procedures, redrawn for the repository-level procedure. One-sided family level alpha = 0.025. 20,000 replicates.

Hypotheses (one-sided): B1 full vs method+args delta <= 0; B2 full vs method+args delta <= 0.10;
B3 full vs method+args+recv delta <= 0; B4 full vs method-only delta <= 0.
Procedures: P3 = Holm over {B1, B3, B4} (B2 reported outside the family); P4 = Holm over {B1, B2, B3, B4}.
Writes ../results/fwer.md.
"""
from pathlib import Path
import numpy as np
import stats_v4 as S

OUT = Path(__file__).resolve().parents[1] / "results"
REPS, K, N, PD, PX, ALPHA = 20000, 7, 30, 0.30, 0.70, 0.025
CONFIGS = {  # name: (d_ma, d_mar, d_mo)
    "C1 all zero": (0.00, 0.00, 0.00),
    "C2 ma at margin, others zero": (0.10, 0.00, 0.00),
    "C3 ma 0.05, others zero": (0.05, 0.00, 0.00),
    "C4 ma at margin, others large": (0.10, 0.20, 0.30),
    "C5 ma zero, others large": (0.00, 0.20, 0.30),
}


def simulate(deltas, mode, rng):
    """Returns per-arm (b, c) arrays of shape (REPS, K)."""
    out = []
    X = rng.random((REPS, K, N)) < PX
    for j, d in enumerate(deltas):
        if mode == "fixed":
            dr, _ = S.fixed_heterogeneity(d, 0.05, PD, "normal")
            dr = np.tile(dr, (REPS, 1))
        else:
            dr = np.clip(d + 0.05 * rng.normal(0, 1, (REPS, K)), -PD, PD)
        a = (PD + dr) / (2 * PX)
        bb = (PD - dr) / (2 * (1 - PX))
        U = rng.random((REPS, K, N))
        Y = np.where(X, U >= a[..., None], U < bb[..., None])
        out.append(((X & ~Y).sum(-1), (~X & Y).sum(-1)))
    return out


def pvals(bc, mode):
    (b1, c1), (b3, c3), (b4, c4) = bc
    if mode == "fixed":
        f0 = lambda b, c: S.mcnemar_exact_p_upper(b.sum(1), c.sum(1))  # noqa: E731
        fm = lambda b, c: S.tango_p_upper(b.sum(1), c.sum(1), K * N, 0.10)  # noqa: E731
    else:
        f0 = lambda b, c: S.repo_t_p_upper((b - c) / N, 0.0)  # noqa: E731
        fm = lambda b, c: S.repo_t_p_upper((b - c) / N, 0.10)  # noqa: E731
    return {"B1": f0(b1, c1), "B2": fm(b1, c1), "B3": f0(b3, c3), "B4": f0(b4, c4)}


def holm_reject(P, names):
    M = np.column_stack([P[n] for n in names])
    adj = np.apply_along_axis(S.holm_adjust, 1, M)
    return {n: adj[:, i] <= ALPHA for i, n in enumerate(names)}


def main():
    lines = ["# Family-wise error of F-B procedures (simulated; PROPOSED rev4; not results)", "",
             f"{REPS} replicates; one-sided family alpha {ALPHA}; Monte Carlo SE at 0.025 is about 0.0011.", "",
             "| Mode / tests | Configuration | True nulls | FWER P3 (Holm B1,B3,B4) | P(B2 rejected) under P3-outside-family at 0.025 | FWER P4 (Holm B1-B4) |",
             "|---|---|---|---|---|---|"]
    for mode, label in (("fixed", "fixed repositories / site-level exact McNemar + Tango"), ("random", "random repositories / repository-level t")):
        for i, (name, ds) in enumerate(CONFIGS.items()):
            rng = np.random.default_rng(20261113 + 100 * i + (0 if mode == "fixed" else 7))
            P = pvals(simulate(ds, mode, rng), mode)
            true = [h for h, t in (("B1", ds[0] <= 0), ("B2", ds[0] <= 0.10), ("B3", ds[1] <= 0), ("B4", ds[2] <= 0)) if t]
            r3, r4 = holm_reject(P, ["B1", "B3", "B4"]), holm_reject(P, ["B1", "B2", "B3", "B4"])
            fw3 = np.any(np.column_stack([r3[h] for h in true if h in r3] or [np.zeros(REPS, bool)]), axis=1).mean()
            fw4 = np.any(np.column_stack([r4[h] for h in true] or [np.zeros(REPS, bool)]), axis=1).mean()
            b2 = (P["B2"] <= ALPHA).mean() if "B2" in true else float("nan")
            lines.append(f"| {label} | {name} | {', '.join(true)} | {fw3:.4f} | {b2:.4f} | {fw4:.4f} |")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "fwer.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
