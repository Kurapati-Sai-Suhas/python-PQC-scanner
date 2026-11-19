"""H3 analysis (run specification H-5; owner decisions TA03 and TA28, revision v1.0.5-r6). Pre-specified
secondary/descriptive analysis; no confirmatory claim. Pre-F1 code; never run on the test split before F2.

New module by design: pqscan/bench/stats.py (risk_coverage, aurc) belongs to the E30 calibration closure and is not
modified. Arms: the tau = T2 policy (pqscan:B4-full-T2) and always-recommend (pqscan:B3-full-noabst).

Per coverage point c in {7/10, 4/5, 9/10}:
* K_r(c) = ceil(c * n_r) (exact fractions).
* T2 withdrawal: if R_r^T2 >= K_r(c), withdraw R_r^T2 - K_r(c) recommendations, tier ascending (T2 before T3), then
  ascending SHA-256 of '20261113|H3-T2|<repo>|<site_id>'; a withdrawn recommendation is judged ABSTAIN (never
  harmful). Nested in c.
* Random withholding: seeds 20261113:withhold:001..100; order = ascending SHA-256 of '<s>|H3-withhold|<repo>|<site_id>'
  over B3-full-noabst's recommended sites; the first K_r(c) keep their recommendation.
* Estimability C1: every repository n_r > 0, R_r^T2 >= K_r(c) and R_r^AR >= K_r(c).
* HR(c) = sum_r H_r(c) / sum_r n_r; HR_AR at natural coverage; HR_rand(c) = mean over the 100 seeds.
* Decision C2: point holds iff HR_T2(c) < HR_AR and HR_T2(c) < HR_rand(c), strictly; MET only if all three points
  are estimable and hold; NOT ASSESSABLE if any point is not estimable.
* TA03: the always-recommend half is coverage-confounded; it is always printed with both coverages and each arm's
  per-recommendation risk (harmful / recommended).
* TA28: within-repository site bootstrap of HR_T2(c) - HR_rand(c), 1,000 resamples, numpy default_rng(20261113);
  K_r(c) recomputed from the resampled n_r; frozen orders (copies of a duplicated site ordered by copy index; copies
  share their outcome, so the tie-break cannot change a harmful count); percentile 95% CI over estimable resamples.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction
from typing import Mapping, Sequence

import numpy as np

T2_ARM = "pqscan:B4-full-T2"
AR_ARM = "pqscan:B3-full-noabst"
POINTS = (Fraction(7, 10), Fraction(4, 5), Fraction(9, 10))
SEED = 20261113
WITHHOLD_SEEDS = tuple(f"20261113:withhold:{i:03d}" for i in range(1, 101))
B_BOOT = 1_000
TIER_ORDER = {"T2": 0, "T3": 1}


def _h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _harmful(row: Mapping) -> bool:
    return row["judgment"] == "INCORRECT" and bool(row.get("harm_category"))


def sites_from_rows(rows: Sequence[Mapping]) -> dict[str, list[dict]]:
    """Common evaluable set: eligible sites on which both arms ran (arm-level failures are reported by the caller)."""
    by = {}
    for r in rows:
        if r["method"] in (T2_ARM, AR_ARM) and str(r["eligible"]).lower() in ("true", "yes"):
            by.setdefault((r["repo"], r["site_id"]), {})[r["method"]] = r
    out: dict[str, list[dict]] = {}
    for (repo, sid), d in sorted(by.items()):
        if len(d) < 2 or any(x["judgment"] == "EXECUTION_FAILURE" for x in d.values()):
            continue
        t2, ar = d[T2_ARM], d[AR_ARM]
        out.setdefault(repo, []).append({
            "site_id": sid, "t2_rec": t2["tool_action"] == "RECOMMEND", "t2_tier": t2.get("tier") or "",
            "t2_harm": _harmful(t2), "ar_rec": ar["tool_action"] == "RECOMMEND", "ar_harm": _harmful(ar)})
    return out


class _Repo:
    """Frozen per-repository arrays; ranks encode the frozen SHA-256 orders."""

    def __init__(self, repo: str, sites: Sequence[Mapping]):
        self.repo, self.n = repo, len(sites)
        self.t2_rec = np.array([s["t2_rec"] for s in sites], bool)
        self.t2_harm = np.array([s["t2_harm"] for s in sites], np.int64)
        self.ar_rec = np.array([s["ar_rec"] for s in sites], bool)
        self.ar_harm = np.array([s["ar_harm"] for s in sites], np.int64)
        for s in sites:
            if s["t2_rec"] and s["t2_tier"] not in TIER_ORDER:
                raise ValueError(f"{repo}/{s['site_id']}: T2 recommendation without tier T2/T3")
        k = [(TIER_ORDER.get(s["t2_tier"], 9), _h(f"20261113|H3-T2|{repo}|{s['site_id']}")) for s in sites]
        self.t2_rank = np.empty(self.n, np.int64)
        self.t2_rank[sorted(range(self.n), key=k.__getitem__)] = np.arange(self.n)
        self.seed_rank = np.empty((len(WITHHOLD_SEEDS), self.n), np.int64)
        for i, sd in enumerate(WITHHOLD_SEEDS):
            hk = [_h(f"{sd}|H3-withhold|{repo}|{s['site_id']}") for s in sites]
            self.seed_rank[i, sorted(range(self.n), key=hk.__getitem__)] = np.arange(self.n)

    def at(self, c: Fraction, idx: np.ndarray | None = None) -> dict:
        """Counts at coverage c for the (possibly resampled) site index vector idx."""
        idx = np.arange(self.n) if idx is None else idx
        n = len(idx)
        K = -(-c.numerator * n // c.denominator)
        t2 = idx[self.t2_rec[idx]]
        ar = idx[self.ar_rec[idx]]
        ok = n > 0 and len(t2) >= K and len(ar) >= K
        res = {"n": n, "K": K, "R_T2": len(t2), "R_AR": len(ar), "estimable": ok,
               "H_AR": int(self.ar_harm[ar].sum())}
        if not ok:
            return res
        # withdraw the lowest-ranked R - K; keep the K highest (stable over copies)
        keep_t2 = t2[np.argsort(self.t2_rank[t2], kind="stable")[len(t2) - K:]]
        res["H_T2"] = int(self.t2_harm[keep_t2].sum())
        order = np.argsort(self.seed_rank[:, ar], axis=1, kind="stable")[:, :K]
        res["H_rand"] = self.ar_harm[ar][order].sum(axis=1)          # one count per seed
        return res


def _pool(parts: Sequence[dict]) -> dict:
    N = sum(p["n"] for p in parts)
    if N == 0 or not all(p["n"] > 0 for p in parts):
        return {"estimable": False, "reason": "a repository has n_r = 0"}
    out = {"estimable": all(p["estimable"] for p in parts), "N": N,
           "HR_AR": sum(p["H_AR"] for p in parts) / N}
    if out["estimable"]:
        out["HR_T2"] = sum(p["H_T2"] for p in parts) / N
        per_seed = sum(p["H_rand"] for p in parts) / N
        out["HR_rand"] = float(per_seed.mean())
        out["_per_seed"] = per_seed
    return out


def analyse(sites_by_repo: Mapping[str, Sequence[Mapping]], *, B: int = B_BOOT, seed: int = SEED) -> dict:
    repos = [_Repo(r, sites_by_repo[r]) for r in sorted(sites_by_repo)]
    N = sum(r.n for r in repos)
    R_ar = sum(int(r.ar_rec.sum()) for r in repos)
    H_ar = sum(int(r.ar_harm[r.ar_rec].sum()) for r in repos)
    rng = np.random.default_rng(seed)
    boot_idx = [[rng.integers(0, r.n, r.n) if r.n else np.array([], np.int64) for r in repos] for _ in range(B)]
    points = {}
    for c in POINTS:
        parts = [r.at(c) for r in repos]
        pooled = _pool(parts)
        pt = {"coverage": str(c), "estimable": pooled["estimable"],
              "per_repository": {r.repo: {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                                          for k, v in p.items() if k != "H_rand"}
                                 | ({"HR_rand_mean": float(p["H_rand"].mean()) / p["n"]} if "H_rand" in p else {})
                                 for r, p in zip(repos, parts)}}
        if pooled["estimable"]:
            ps = pooled.pop("_per_seed")
            sumK = sum(p["K"] for p in parts)
            pt.update({
                "HR_T2": pooled["HR_T2"], "HR_AR_natural": pooled["HR_AR"], "HR_rand": pooled["HR_rand"],
                "rand_distribution": {"min": float(ps.min()), "p2.5": float(np.percentile(ps, 2.5)),
                                      "median": float(np.median(ps)), "p97.5": float(np.percentile(ps, 97.5)),
                                      "max": float(ps.max()), "sd": float(ps.std(ddof=1))},
                # TA03: the always-recommend half is coverage-confounded; print coverages and per-recommendation risk
                "always_recommend_reporting_TA03": {
                    "label": "natural-coverage comparison (coverage-confounded); not matched",
                    "coverage_T2_at_c": sumK / N, "coverage_AR_natural": R_ar / N,
                    "per_recommendation_risk_T2_at_c": pooled["HR_T2"] * N / sumK if sumK else None,
                    "per_recommendation_risk_AR": H_ar / R_ar if R_ar else None},
                "holds_vs_AR": pooled["HR_T2"] < pooled["HR_AR"],
                "holds_vs_rand": pooled["HR_T2"] < pooled["HR_rand"]})
            pt["point_holds"] = pt["holds_vs_AR"] and pt["holds_vs_rand"]
            diffs, not_est = [], 0
            for idxs in boot_idx:
                bp = _pool([r.at(c, ix) for r, ix in zip(repos, idxs)])
                if bp["estimable"]:
                    diffs.append(bp["HR_T2"] - bp["HR_rand"])
                else:
                    not_est += 1
            pt["bootstrap_TA28"] = {"B": B, "seed": seed, "not_estimable_resamples": not_est,
                                    "ci95_HR_T2_minus_HR_rand": ([float(np.percentile(diffs, 2.5)),
                                                                  float(np.percentile(diffs, 97.5))] if diffs else None)}
        points[str(c)] = pt
    if not all(points[str(c)]["estimable"] for c in POINTS):
        status = "NOT ASSESSABLE"
    else:
        status = "MET" if all(points[str(c)]["point_holds"] for c in POINTS) else "NOT MET"
    return {"hypothesis": "H3 (secondary, descriptive)", "status": status, "repositories": len(repos),
            "natural_coverage_AR": (R_ar / N) if N else None, "points": points}
