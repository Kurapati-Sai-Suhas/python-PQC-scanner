"""F-A Type I error simulation (owner decision F05; analysis plan v1.0.1 Sec. 9 and Sec. 11.6).

    python scripts/fa_type1_simulation.py           # full run -> docs/implementation/acceptance/fa_type1.{json,md}
    python scripts/fa_type1_simulation.py --quick   # smoke run (small R) -> *_quick files

Procedure under test (unchanged): for each baseline j, a one-sided exact McNemar test on the pooled discordant pairs
(b_j sites where the proposed system is correct and j is not, c_j the reverse) over the sites where both ran, at
natural coverage; Holm across the baselines at alpha = 0.025 (analysis plan Sec. 9). The p-value is
P(X >= b), X ~ Binomial(b + c, 1/2), as in pqscan.bench.stats.mcnemar_exact_one_sided (imported read-only; this script
does not modify any file of the E30 calibration closure).

Design simulated (design-based inference over fixed finite frames, as in the analysis plan): 7 repositories, strata
app / non-app, stratified simple random sampling WITHOUT replacement of m_app = 20 and m_nonapp = 10 sites per
repository (the allocation of the H2 two-stratum calibration), frames of very different sizes (sampling fractions from
0.83 down to 0.03), optional execution failures. Every configuration is constructed AT OR INSIDE the null boundary:
the design expectation of b - c over the both-ran sites is <= 0 (it is reported exactly).

Acceptance criteria (approved with the decision register): every single-test rejection rate <= 0.025 + 3 MC-SE and
every Holm family-wise error over the null baselines <= 0.025 + 3 MC-SE, with MC-SE = sqrt(0.025 * 0.975 / R) at the
nominal level. If any criterion fails, the run reports FAIL and nothing else changes: the owner decides on any
alternative method separately.

Seeds: configuration k uses numpy.random.default_rng(seed_int(k)), seed_int(k) = the first 8 bytes (big-endian) of
SHA-256("20261113:fa-type1:<k>"). Results depend only on (k, R).
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats as sps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pqscan.bench import stats as ST  # noqa: E402  (read-only use)

ALPHA = 0.025
N_REPOS = 7
M_APP, M_NON = 20, 10
FRAME_APP = (40, 60, 90, 150, 220, 300, 400)
FRAME_NON = (12, 20, 35, 60, 100, 150, 250)
OUT = ROOT / "docs" / "implementation" / "acceptance"


def seed_int(key: str) -> int:
    return int.from_bytes(hashlib.sha256(f"20261113:fa-type1:{key}".encode("utf-8")).digest()[:8], "big")


def p_one_sided(b: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Vectorised pqscan.bench.stats.mcnemar_exact_one_sided: P(X >= b), X ~ Bin(b + c, 1/2); 1.0 when b + c = 0."""
    n = b + c
    p = sps.binom.sf(b - 1, n, 0.5)
    return np.where(n == 0, 1.0, p)


def holm_reject(p: np.ndarray, alpha: float = ALPHA) -> np.ndarray:
    """Vectorised Holm step-down. p: (R, m). Returns the (R, m) rejection matrix."""
    R, m = p.shape
    order = np.argsort(p, axis=1, kind="stable")
    ps = np.take_along_axis(p, order, axis=1)
    thr = alpha / (m - np.arange(m))
    ok = np.cumprod(ps <= thr, axis=1).astype(bool)
    rej = np.zeros_like(ok)
    np.put_along_axis(rej, order, ok, axis=1)
    return rej


# ------------------------------------------------------------------------------------------- frames
def stratum_frame(N: int, d: float, s: float) -> tuple[int, int, int]:
    """(B, C, concordant) for a frame of N sites with discordance share d, of which share s favours the proposed system."""
    disc = int(round(N * d))
    B = int(round(disc * s))
    return B, disc - B, N - disc


def design_expectation(frames, m, fail) -> float:
    """Exact design expectation of b - c over both-ran sites: sum_h m_h (1 - f_h) (B_h - C_h) / N_h."""
    return float(sum(mh * (1 - fh) * (B - C) / (B + C + K) for (B, C, K), mh, fh in zip(frames, m, fail)))


def to_null_side(frames, m, fail):
    """Place the configuration ON the null boundary despite integer rounding: move single sites between a discordant
    type and the concordant type, always in the stratum with the smallest step m_h (1 - f_h) / N_h, until
    -step_min < E[b - c] <= 0. Being far inside the null would understate the Type I error, so both directions are
    corrected."""
    frames = [list(f) for f in frames]
    step = [mh * (1 - fh) / sum(f) for f, mh, fh in zip(frames, m, fail)]
    order = sorted(range(len(frames)), key=lambda i: step[i])
    smin = step[order[0]]

    def move(kind: int) -> None:                 # kind 0: B -> concordant (lowers E); 1: C -> concordant (raises E)
        for i in order:
            if frames[i][kind] > 0:
                frames[i][kind] -= 1
                frames[i][2] += 1
                return
        raise ValueError("cannot reach the null boundary")

    while design_expectation(frames, m, fail) > 1e-12:
        move(0)
    while design_expectation(frames, m, fail) + smin <= 1e-12:
        move(1)
    return [tuple(f) for f in frames]


def build(spec: dict):
    """Strata of one single-baseline configuration: lists of frames, sample sizes and failure probabilities."""
    frames, m, fail = [], [], []
    for r in range(N_REPOS):
        for h, (N, mh) in enumerate(((FRAME_APP[r], M_APP), (FRAME_NON[r], M_NON))):
            d, s = spec["d"](r, h), spec["s"](r, h)
            frames.append(stratum_frame(N, d, s))
            m.append(mh)
            fail.append(spec.get("fail", lambda r, h: 0.0)(r, h))
    return to_null_side(frames, m, fail), m, fail


def simulate_single(spec: dict, R: int, key: str) -> dict:
    rng = np.random.default_rng(seed_int(key))
    frames, m, fail = build(spec)
    b = np.zeros(R, dtype=np.int64)
    c = np.zeros(R, dtype=np.int64)
    for (B, C, K), mh, fh in zip(frames, m, fail):
        draw = rng.multivariate_hypergeometric([B, C, K], mh, size=R)     # sampling without replacement
        bb, cc = draw[:, 0], draw[:, 1]
        if fh > 0:                                                         # failures independent of the outcome type
            bb = rng.binomial(bb, 1 - fh)
            cc = rng.binomial(cc, 1 - fh)
        b += bb
        c += cc
    p = p_one_sided(b, c)
    rate = float(np.mean(p <= ALPHA))
    return {"R": R, "rejection_rate": rate, "mean_discordant": float(np.mean(b + c)),
            "design_E_b_minus_c": design_expectation(frames, m, fail)}


def family_frames(rng, null_mask: list[bool], d: float, core: float, s_alt: float):
    """Per stratum, explicit frames: X (proposed correct) and Y_j for 8 baselines. Each baseline's discordant units are
    a shared core (fraction `core` of its discordant units, common to all baselines -> correlated tests) plus its own
    extra units. Null baselines have B_j = C_j exactly in every stratum; alternative ones favour the proposed system."""
    strata = []
    for r in range(N_REPOS):
        for N, mh in ((FRAME_APP[r], M_APP), (FRAME_NON[r], M_NON)):
            X = np.zeros(N, dtype=bool)
            X[: N // 2 + N // 10] = True
            rng.shuffle(X)
            ones, zeros = np.flatnonzero(X), np.flatnonzero(~X)
            disc = max(2, int(round(N * d)))
            k_core = int(round(disc * core / 2))
            core1 = rng.choice(ones, size=min(k_core, len(ones)), replace=False)
            core0 = rng.choice(zeros, size=min(k_core, len(zeros)), replace=False)
            Y = np.repeat(X[None, :], len(null_mask), axis=0)
            for j, is_null in enumerate(null_mask):
                s = 0.5 if is_null else s_alt
                nb, nc = int(round(disc * s)), disc - int(round(disc * s))
                if is_null:
                    nb = nc = disc // 2
                pick1 = list(core1[: min(len(core1), nb)])
                pick0 = list(core0[: min(len(core0), nc)])
                rest1 = np.setdiff1d(ones, pick1)
                rest0 = np.setdiff1d(zeros, pick0)
                pick1 += list(rng.choice(rest1, size=max(0, nb - len(pick1)), replace=False))
                pick0 += list(rng.choice(rest0, size=max(0, nc - len(pick0)), replace=False))
                Y[j, pick1] = False          # proposed right, baseline wrong  -> b-type
                Y[j, pick0] = True           # proposed wrong, baseline right  -> c-type
            strata.append((X, Y, mh))
    return strata


def simulate_family(null_mask: list[bool], R: int, key: str, d=0.2, core=0.6, s_alt=0.75, fail=0.0) -> dict:
    rng = np.random.default_rng(seed_int(key))
    strata = family_frames(rng, null_mask, d, core, s_alt)
    J = len(null_mask)
    b = np.zeros((R, J), dtype=np.int64)
    c = np.zeros((R, J), dtype=np.int64)
    exp = np.zeros(J)
    for X, Y, mh in strata:
        N = X.size
        idx = np.argsort(rng.random((R, N)), axis=1)[:, :mh]          # SRS without replacement, R times
        xs = X[idx]                                                       # (R, mh)
        for j in range(J):
            ys = Y[j][idx]
            ran = rng.random(ys.shape) >= fail if fail > 0 else np.ones(ys.shape, dtype=bool)
            b[:, j] += np.sum(xs & ~ys & ran, axis=1)
            c[:, j] += np.sum(~xs & ys & ran, axis=1)
            exp[j] += mh * (1 - fail) * (np.sum(X & ~Y[j]) - np.sum(~X & Y[j])) / N
    p = p_one_sided(b, c)
    rej = holm_reject(p)
    nulls = np.array(null_mask)
    fwer = float(np.mean(rej[:, nulls].any(axis=1))) if nulls.any() else 0.0
    single = [float(np.mean(p[:, j] <= ALPHA)) for j in range(J)]
    corr = float(np.corrcoef(b[:, nulls].T)[np.triu_indices(int(nulls.sum()), 1)].mean()) if nulls.sum() > 1 else None
    return {"R": R, "fwer_null_baselines": fwer, "single_rejection_rates": single,
            "design_E_b_minus_c": [float(e) for e in exp], "null_mask": null_mask,
            "mean_corr_b_between_null_baselines": corr}


SINGLE = {
    "S1-homogeneous": {"desc": "every stratum: discordance 0.20, exactly balanced",
                       "d": lambda r, h: 0.20, "s": lambda r, h: 0.5},
    "S2-repo-heterogeneous": {"desc": "repositories favour opposite arms (shares 0.8/0.2, 0.75/0.25, 0.7/0.3, 0.5), "
                                      "cancelling under the design",
                              "d": lambda r, h: 0.20, "s": lambda r, h: (0.8, 0.2, 0.75, 0.25, 0.7, 0.3, 0.5)[r]},
    "S3-stratum-heterogeneous": {"desc": "app favours the proposed system (d 0.15, share 0.7), non-app the baseline "
                                         "(d 0.30, share 0.3); small non-app frames (fractions up to 0.83)",
                                 "d": lambda r, h: (0.15, 0.30)[h], "s": lambda r, h: (0.7, 0.3)[h]},
    "S4-sparse": {"desc": "discordance 0.03 (about 6 discordant pairs per data set)",
                  "d": lambda r, h: 0.03, "s": lambda r, h: 0.5},
    "S5-failures-random": {"desc": "S2 with 10% execution failures independent of the outcome",
                           "d": lambda r, h: 0.20, "s": lambda r, h: (0.8, 0.2, 0.75, 0.25, 0.7, 0.3, 0.5)[r],
                           "fail": lambda r, h: 0.10},
    "S6-failures-by-stratum": {"desc": "S3-type heterogeneity with failures 5% (app) and 30% (non-app); null on the "
                                       "both-ran sites (estimand of plan Sec. 9 item 4)",
                               "d": lambda r, h: (0.15, 0.30)[h], "s": lambda r, h: (0.7, 0.2286)[h],
                               "fail": lambda r, h: (0.05, 0.30)[h]},
}
FAMILY = {
    "F1-all-null-correlated": {"desc": "8 baselines, all null, shared discordant core 60% (correlated tests)",
                               "null_mask": [True] * 8, "kw": {}},
    "F2-half-alternative": {"desc": "baselines 1-4 favour the proposed system (share 0.75), 5-8 null; FWER over 5-8",
                            "null_mask": [False] * 4 + [True] * 4, "kw": {}},
    "F3-all-null-failures": {"desc": "F1 with 10% execution failures",
                             "null_mask": [True] * 8, "kw": {"fail": 0.10}},
    "F4-all-null-sparse": {"desc": "F1 with discordance 0.05",
                           "null_mask": [True] * 8, "kw": {"d": 0.05}},
}


def mcse(R: int) -> float:
    return math.sqrt(ALPHA * (1 - ALPHA) / R)


def run(R_single: int, R_family: int) -> dict:
    t0 = time.time()
    out = {"procedure": "one-sided exact McNemar per baseline on pooled both-ran discordant pairs; Holm at 0.025",
           "alpha": ALPHA, "design": {"repositories": N_REPOS, "m_app": M_APP, "m_nonapp": M_NON,
                                      "frame_app": FRAME_APP, "frame_nonapp": FRAME_NON},
           "seed_rule": "numpy default_rng(first 8 bytes, big-endian, of SHA-256('20261113:fa-type1:<config>'))",
           "criterion": "rate <= 0.025 + 3 * sqrt(0.025 * 0.975 / R)", "single": {}, "family": {}}
    for k, spec in SINGLE.items():
        res = simulate_single(spec, R_single, k)
        lim = ALPHA + 3 * mcse(R_single)
        out["single"][k] = {"desc": spec["desc"], **res, "limit": lim, "pass": res["rejection_rate"] <= lim}
    for k, spec in FAMILY.items():
        res = simulate_family(spec["null_mask"], R_family, k, **spec["kw"])
        lim = ALPHA + 3 * mcse(R_family)
        out["family"][k] = {"desc": spec["desc"], **res, "limit": lim, "pass": res["fwer_null_baselines"] <= lim}
    out["all_pass"] = all(v["pass"] for v in out["single"].values()) and all(v["pass"] for v in out["family"].values())
    out["environment"] = {"python": sys.version.split()[0], "numpy": np.__version__,
                          "scipy": __import__("scipy").__version__, "platform": platform.platform()}
    out["runtime_seconds"] = round(time.time() - t0, 1)
    return out


def write(res: dict, quick: bool) -> None:
    sfx = "_quick" if quick else ""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"fa_type1{sfx}.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
    lines = [f"# F-A Type I error simulation{' (quick)' if quick else ''}", "",
             f"Procedure: {res['procedure']}. Criterion: {res['criterion']}.", "",
             f"**Overall: {'PASS' if res['all_pass'] else 'FAIL - stop; the owner decides on alternatives'}**", "",
             "| Configuration | R | Rejection rate | Limit | Design E[b-c] | Mean discordant | Result |",
             "|---|---|---|---|---|---|---|"]
    for k, v in res["single"].items():
        lines.append(f"| {k}: {v['desc']} | {v['R']} | {v['rejection_rate']:.4f} | {v['limit']:.4f} | "
                     f"{v['design_E_b_minus_c']:.3f} | {v['mean_discordant']:.1f} | {'pass' if v['pass'] else 'FAIL'} |")
    lines += ["", "| Family configuration | R | FWER over null baselines | Limit | Mean corr(b) | Result |",
              "|---|---|---|---|---|---|"]
    for k, v in res["family"].items():
        corr = "n/a" if v["mean_corr_b_between_null_baselines"] is None else f"{v['mean_corr_b_between_null_baselines']:.2f}"
        lines.append(f"| {k}: {v['desc']} | {v['R']} | {v['fwer_null_baselines']:.4f} | {v['limit']:.4f} | {corr} | "
                     f"{'pass' if v['pass'] else 'FAIL'} |")
    lines += ["", f"Environment: {res['environment']}; runtime {res['runtime_seconds']} s.",
              "This simulation checks error control under an assumed design and assumed outcome configurations. "
              "It says nothing about scanner accuracy."]
    (OUT / f"fa_type1{sfx}.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if any(a != "--quick" for a in args):
        print(__doc__)
        return 0 if set(args) <= {"-h", "--help", "--quick"} else 2
    quick = "--quick" in args
    res = run(400, 200) if quick else run(20_000, 10_000)
    write(res, quick)
    print(("PASS" if res["all_pass"] else "FAIL"), f"in {res['runtime_seconds']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
