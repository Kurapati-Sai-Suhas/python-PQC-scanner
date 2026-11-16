"""H2 inference and Experiment A (R4-19 items 10-12 and Batch 4; phase3_analysis_plan.md Sec. 7-9)."""
from __future__ import annotations

from fractions import Fraction

import numpy as np
import pytest
from scipy.stats import binomtest
from statsmodels.stats.multitest import multipletests

from pqscan.bench import fa as FA
from pqscan.bench import h2 as H
from pqscan.bench import matching as MT
from pqscan.bench.matching import Output as O
from pqscan.bench.stats import holm, mcnemar_exact_one_sided


def lab(i, role="SIGN", ass="DETERMINATE", stratum="S1-app"):
    return {"site_id": f"s{i}", "eligible": "yes", "gt_role": role, "assessability": ass, "hybrid_component": "no",
            "stratum": stratum}


def make_repo(name, rng, n=30, p_rec_f=0.7, p_rec_m=0.4, fail=0, ab_n=None):
    """A synthetic repository result (fixtures only; correctness is random)."""
    L, F, M = [], [], []
    for i in range(n):
        ind = rng.random() < 0.15
        L.append(lab(i, "UNKNOWN" if ind else "SIGN", "INDETERMINATE" if ind else "DETERMINATE",
                     "S1-nonapp" if i % 3 == 0 else "S1-app"))
        right = "SIG" if rng.random() < 0.85 else "KEM"
        F.append(O("RECOMMEND", right, ["T1", "T2", "T3"][rng.integers(0, 3)]) if rng.random() < p_rec_f else O("ABSTAIN", "NONE", "T1"))
        M.append(O("RECOMMEND", "SIG" if rng.random() < 0.8 else "KEM", ["T0", "T1"][rng.integers(0, 2)]) if rng.random() < p_rec_m else O("ABSTAIN", "NONE", "T0"))
    for i in range(fail):
        F[i], M[i] = O("EXECUTION_FAILURE"), O("EXECUTION_FAILURE")
    return MT.repository_result(L, F, M, comparison="H2-1", repo=name, seeds=())


@pytest.fixture(scope="module")
def seven():
    rng = np.random.default_rng(11)
    return [make_repo(f"r{i}", rng) for i in range(7)]


# ------------------------------------------------------------------ bootstrap mechanics
def test_withdraw_mask_exact_counts_and_lowest_tier_first():
    rng = np.random.default_rng(1)
    rec = rng.random((500, 20)) < 0.6
    tier = rng.integers(0, 4, (500, 20))
    keys = rng.random((500, 20))
    excess = np.array([rng.integers(0, r.sum() + 1) for r in rec])
    w = H._withdraw_mask(rec, tier, keys, excess)
    assert np.array_equal(w.sum(1), excess) and not np.any(w & ~rec)
    kept_min = np.where(rec & ~w, tier, 9).min(1)
    wd_max = np.where(w, tier, -1).max(1)
    assert np.all((wd_max <= kept_min) | (wd_max == -1))


def test_bootstrap_deterministic_identical_arms_and_p_formula(seven):
    arrays = [r["arrays"] for r in seven]
    a = H.bootstrap(arrays, B=500, seed=5)
    assert np.array_equal(a, H.bootstrap(arrays, B=500, seed=5))
    same = [(F, F) for F, _ in arrays]
    assert H.p_value(H.bootstrap(same, B=300, seed=1), 0.0) == 1.0
    d = np.array([-0.1, 0.0, 0.2, 0.3])
    assert H.p_value(d, 0.0) == pytest.approx(3 / 5)


def test_stratified_variant_keeps_stratum_counts():
    rng = np.random.default_rng(2)
    strata = np.array(["a"] * 20 + ["b"] * 10, dtype=object)
    idx = H._indices(rng, 30, 400, strata)
    assert np.all(np.isin(idx[:, :20], np.arange(20))) and np.all(np.isin(idx[:, 20:], np.arange(20, 30)))


def test_site_weighting_differs_with_unequal_n():
    rng = np.random.default_rng(3)
    reps = [make_repo("a", rng, n=30), make_repo("b", rng, n=10)]
    arrays = [r["arrays"] for r in reps]
    rb = H.bootstrap(arrays, B=400, seed=1)
    sw = H.bootstrap(arrays, B=400, seed=1, weighting="site")
    assert not np.allclose(rb, sw)


# ------------------------------------------------------------------ guard, gate, K_e
@pytest.mark.parametrize("pairs,g,active", [
    ([(3, 3, 30)], Fraction(0), True), ([(2, 5, 30)], Fraction(-1, 10), True), ([(5, 3, 30)], Fraction(1, 15), True),
    ([(9, 6, 30)], Fraction(1, 10), False), ([(10, 6, 30)], Fraction(2, 15), False),
    ([(21, 0, 30), (0, 15, 30)], Fraction(1, 10), False)])
def test_guard_boundaries(pairs, g, active):
    res = [{"R_f": a, "R_m": b, "n_common": n} for a, b, n in pairs]
    assert H.coverage_gap(res) == g and H.guard_active(g) is active


def test_guard_uses_estimable_repositories_only_and_is_undefined_at_k_e_0():
    res = [{"R_f": 9, "R_m": 6, "n_common": 30}, {"R_f": 0, "R_m": 0, "n_common": 0}]
    assert H.coverage_gap(res) == Fraction(1, 10)
    assert H.coverage_gap([{"R_f": 0, "R_m": 0, "n_common": 0}]) is None
    with pytest.raises(ValueError):
        H.guard_active(None)


def test_guarded_p_before_holm():
    assert H.guarded(0.004, Fraction(0)) == pytest.approx(0.008) and H.guarded(0.7, Fraction(-1)) == 1.0
    assert H.guarded(0.004, Fraction(1, 10)) == 0.004


def test_gate_cases():
    mk = lambda ks: [{"repo": f"r{i}", "k": k, "n_common": 30} for i, k in enumerate(ks)]
    assert H.gate(mk([9, 9, 9, 9, 6, 0, 0]))["passes"]                 # 42/210 = 1/5 exactly, 5 feasible
    assert not H.gate(mk([6, 6, 6, 6, 6, 0, 0]))["passes"]             # 30/210 < 1/5
    assert not H.gate(mk([20, 20, 20, 20, 4, 4, 4]))["passes"]         # 4 feasible
    g = H.gate(mk([9, 9, 9, 9, 6, 0, 0]) + [{"repo": "x", "k": 0, "n_common": 0}])
    assert g["c_pool"] == Fraction(42, 210) and "x" not in g["feasible"]


@pytest.mark.parametrize("K_e,expect", [(7, "assessable"), (6, "not assessable as pre-registered"),
                                        (1, "not assessable as pre-registered"), (0, "not assessable (no estimable repository)")])
def test_assessability_by_k_e(K_e, expect):
    assert H.assessability(7, K_e) == expect


# ------------------------------------------------------------------ family F-B
def _family(seven, drop=0):
    rng = np.random.default_rng(4)
    results = {c: list(seven) for c in H.CONFIRMATORY}
    if drop:
        for c in results:
            results[c] = results[c][:7 - drop] + [make_repo(f"z{i}", rng, fail=30) for i in range(drop)]
    return H.run_family(results, B=1_000, seed=7)


def test_family_full_assessable_statements_and_holm(seven):
    res = _family(seven)
    p = [res[c]["p_guarded"] for c in H.CONFIRMATORY]
    assert [res[c]["p_holm"] for c in H.CONFIRMATORY] == pytest.approx(list(multipletests(p, method="holm")[1]))
    for c in H.CONFIRMATORY:
        r = res[c]
        assert r["K"] == 7 and r["K_e"] == 7 and r["assessability"] == "assessable"
        assert r["claimable"] == (r["holm_rejected"] and r["gate"]["passes"])
        assert "H2 supported" not in r["statement"]
    assert res["H2-1"]["h2b"].startswith("H2b (exploratory, pre-specified; not under family-wise error control)")
    assert "p_margin_guarded" in res["H2-1"]


def test_rule_b_partial_estimability(seven):
    res = _family(seven, drop=1)
    for c in H.CONFIRMATORY:
        r = res[c]
        assert r["K_e"] == 6 and r["statement"].endswith("not assessable as pre-registered")
        assert r["claimable"] is False and r["delta"] is not None              # estimable average still reported
        assert r["non_estimable"] and r["non_estimable"][0]["n_eligible"] == 30
    assert res["H2-1"]["h2b"].endswith("not assessable")


def test_rule_a_no_estimable_repository():
    rng = np.random.default_rng(5)
    empty = [make_repo(f"z{i}", rng, fail=30) for i in range(7)]
    res = H.run_family({c: empty for c in H.CONFIRMATORY}, B=200)
    for c in H.CONFIRMATORY:
        r = res[c]
        assert r["K_e"] == 0 and r["delta"] is None and r["g"] is None and r["p"] is None
        assert "not assessable" in r["statement"]


def test_monte_carlo_rule():
    assert H.mc_rerun_needed(0.0085, 0.025 / 3, 10_000)
    assert not H.mc_rerun_needed(0.02, 0.025 / 3, 10_000)


def test_statements_never_say_h2_supported():
    base = {"assessability": "assessable", "gate": {"passes": True}, "claimable": True}
    assert H.statement("H2-1", base) == "H2a (confirmatory): supported"
    assert H.statement("H2-1", base | {"gate": {"passes": False}}).endswith("not assessable at equal coverage (matched coverage too low)")
    assert H.statement("H2-3", base | {"claimable": False}) == "H2-3 (confirmatory): not supported"


def test_repository_level_exploratory():
    out = H.repository_level([0.1, 0.2, 0.05, 0.3, 0.1, 0.15, 0.2])
    assert out["sign_flip_p"] == pytest.approx(1 / 128) and len(out["leave_one_out"]) == 7
    assert 0 < out["t_one_sided_p"] < 0.01


# ------------------------------------------------------------------ F-A
def test_one_sided_mcnemar_matches_binomtest():
    for b, c in ((10, 3), (3, 10), (0, 0), (7, 7), (20, 5)):
        ref = 1.0 if b + c == 0 else binomtest(b, b + c, 0.5, alternative="greater").pvalue
        assert mcnemar_exact_one_sided(b, c) == pytest.approx(ref)


def _fa_rows():
    rng = np.random.default_rng(8)
    rows = []
    for r in range(7):
        for i in range(30):
            sid = f"r{r}s{i}"
            rows.append({"site_id": sid, "repo": f"r{r}", "method": FA.SYSTEM,
                         "judgment": "CORRECT" if rng.random() < 0.7 else "UNASSESSABLE"})
            for j, p in (("pqcheck", 0.4), ("qsafe", 0.65)):
                jd = "EXECUTION_FAILURE" if (j == "pqcheck" and i < 2) else ("CORRECT" if rng.random() < p else "INCORRECT")
                rows.append({"site_id": sid, "repo": f"r{r}", "method": j, "judgment": jd})
    return rows


def test_fa_family():
    out = FA.run_fa(_fa_rows(), ["pqcheck", "qsafe", "CBOMkit", "Mehl", "absent-tool"])
    assert "fixed" in out["assumptions"] and "both-ran" in out["assumptions"]
    assert set(out["not_scored"]) == {"CBOMkit", "Mehl", "absent-tool"}
    pq, qs = out["comparisons"]["pqcheck"], out["comparisons"]["qsafe"]
    assert pq["n_both_ran"] == 210 - 14 and pq["both_ran_per_repo"]["r0"] == 28 and pq["failures"]["baseline"] == 14
    assert qs["n_both_ran"] == 210
    assert [pq["p_holm"], qs["p_holm"]] == pytest.approx(holm([pq["p_one_sided"], qs["p_one_sided"]]))
    assert pq["delta_site"] == pytest.approx((pq["b"] - pq["c"]) / pq["n_both_ran"])
    assert pq["ci95_site"][0] <= pq["delta_site"] <= pq["ci95_site"][1]
    lo, hi = pq["delta_sf2"]
    assert lo <= pq["delta_sf1"] <= hi and pq["delta_repo_balanced"] is not None


def test_fa_requires_same_sites():
    rows = _fa_rows()
    with pytest.raises(ValueError):
        FA.run_fa([r for r in rows if not (r["method"] == "qsafe" and r["site_id"] == "r0s0")], ["qsafe"])
