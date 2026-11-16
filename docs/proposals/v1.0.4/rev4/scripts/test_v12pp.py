"""Tests for the V12'' additions (R4-11..R4-16). PROPOSED, NOT ADOPTED; not production tests.

    .venv/Scripts/python -m pytest -q -o addopts="" docs/proposals/v1.0.4/rev4/scripts/test_v12pp.py
"""
from __future__ import annotations

import itertools
from fractions import Fraction

import numpy as np
import pytest

import matching_ref_v4 as MR
import stats_v4 as S
from matching_ref_v4 import ArmOutput as A
import worked_example_v4 as WE


def rec(t, c="SIG"):
    return A("RECOMMEND", c, t)


AB, FL, NF, EF = A("ABSTAIN", "NONE", "T1"), A("FLAG_NO_TARGET", "NONE", "T2"), A("NO_FINDING"), A("EXECUTION_FAILURE")
ROLES = [("SIGN", "DETERMINATE"), ("KEY_ESTABLISHMENT", "DETERMINATE"), ("UNKNOWN", "INDETERMINATE"),
         ("KEY_MATERIAL_ONLY", "DETERMINATE")]
ACTS = [rec("T0"), rec("T1"), rec("T2"), rec("T3"), rec("T2", "KEM"), AB, FL, NF]


def site(i, role="SIGN", ass="DETERMINATE", hyb="no"):
    return dict(site_id=f"x{i}", eligible="yes", gt_role=role, assessability=ass, hybrid_component=hyb)


def rand_repo(rng, n):
    sites = [site(i, *ROLES[rng.integers(0, 4)]) for i in range(n)]
    f = [ACTS[i] for i in rng.integers(0, len(ACTS), n)]
    m = [ACTS[i] for i in rng.integers(0, len(ACTS), n)]
    return sites, f, m


# ------------------------------------------------------------------ exact tie-averaging
def test_tie_average_batch_equals_reference_on_resamples():
    rng = np.random.default_rng(11)
    for _ in range(60):
        n = int(rng.integers(3, 20))
        sites, f, m = rand_repo(rng, n)
        F, M = MR.site_arrays(sites, f), MR.site_arrays(sites, m)
        idx = rng.integers(0, n, (5, n))
        got = MR.tie_average_batch(F, M, idx)[0]
        for row, ix in zip(got, idx):
            # rebuild the resample with unique ids and compare with the per-site reference
            rs = [dict(sites[j], site_id=f"r{q}") for q, j in enumerate(ix)]
            ref = MR.tie_average_delta(rs, [f[j] for j in ix], [m[j] for j in ix], comparison="c", repo="r")
            assert row == pytest.approx(ref)


@pytest.mark.parametrize("ranking", [True, False])
def test_tie_average_equals_brute_force_over_all_orders(ranking):
    rng = np.random.default_rng(12)
    for _ in range(40):
        n = int(rng.integers(3, 9))
        sites, f, m = rand_repo(rng, n)
        ids = [s["site_id"] for s in sites]
        rf = [i for i, a in enumerate(f) if a.action == "RECOMMEND"]
        rm = [i for i, a in enumerate(m) if a.action == "RECOMMEND"]
        k = min(len(rf), len(rm))
        arm, recs, other = (f, rf, m) if len(rf) > k else (m, rm, f)
        e = len(recs) - k
        vals = []
        for perm in itertools.permutations(recs):        # every withdrawal order consistent with the rule
            if ranking and any(MR.TIER_RANK[arm[perm[i]].tier] > MR.TIER_RANK[arm[perm[i + 1]].tier] for i in range(len(perm) - 1)):
                continue
            wd = [ids[i] for i in perm[:e]]
            a2 = MR.apply_withdrawal(ids, arm, wd)
            x = sum(MR.is_correct(s, a) for s, a in zip(sites, a2 if arm is f else f))
            y = sum(MR.is_correct(s, a) for s, a in zip(sites, a2 if arm is m else m))
            vals.append((x - y) / n)
        ta = MR.tie_average_delta(sites, f, m, comparison="c", repo="r", order="tier" if ranking else "hash")
        assert np.mean(vals) == pytest.approx(ta)


def test_ranking_free_hash_order_ignores_tiers():
    f = [rec("T3"), rec("T0"), rec("T3"), rec("T0")]
    m = [rec("T1"), AB, AB, AB]
    ids = [f"x{i}" for i in range(4)]
    r = MR.match_repository(ids, f, m, comparison="c", repo="r", order="hash")
    expect = sorted(ids, key=lambda s: MR.tiebreak_key(MR.PRIMARY_SEED, "c", "r", s))[:3]
    assert r.withdrawn_f == expect


def test_worked_example_tie_average_and_ranking_free():
    assert MR.tie_average_delta(WE.EX_SITES, WE.EX_F, WE.EX_M, comparison="H2-1", repo="example") == pytest.approx(1.5 / 12)
    rf = MR.tie_average_delta(WE.EX_SITES, WE.EX_F, WE.EX_M, comparison="H2-1", repo="example", order="hash")
    # F has 8 RECs, withdraws 3 at random: each kept with p 5/8. Correct-if-kept: s1 s2 s3 s5 s7 s8 (6); s10 correct if
    # withdrawn; others fixed (s6, s11 correct). E[F] = 6*5/8 + 3/8 + 2 = 6.125; M = 6
    assert rf == pytest.approx((6.125 - 6) / 12)


# ------------------------------------------------------------------ bootstrap of the tie-averaged estimate
def _repos():
    F, M = MR.site_arrays(WE.EX_SITES, WE.EX_F), MR.site_arrays(WE.EX_SITES, WE.EX_M)
    return [(F, M)] * 3


def test_bootstrap_ta_deterministic_and_has_no_tie_randomness():
    assert MR.bootstrap_ta(_repos(), B=1000, seed=3) == MR.bootstrap_ta(_repos(), B=1000, seed=3)


def test_bootstrap_ta_identical_arms_p_one():
    F = MR.site_arrays(WE.EX_SITES, WE.EX_F)
    assert MR.bootstrap_ta([(F, F)], B=300, seed=1) == 1.0


def test_bootstrap_ta_distribution_matches_reference_resamples():
    F, M = MR.site_arrays(WE.EX_SITES, WE.EX_F), MR.site_arrays(WE.EX_SITES, WE.EX_M)
    rng = np.random.default_rng(MR.BOOTSTRAP_SEED)
    idx = rng.integers(0, 12, size=(20, 12))
    p, dist = MR.bootstrap_ta([(F, M)], B=20, seed=MR.BOOTSTRAP_SEED, chunk=20, return_dist=True)
    for row, ix in zip(dist, idx):
        rs = [dict(WE.EX_SITES[j], site_id=f"r{q}") for q, j in enumerate(ix)]
        ref = MR.tie_average_delta(rs, [WE.EX_F[j] for j in ix], [WE.EX_M[j] for j in ix], comparison="c", repo="r")
        assert row == pytest.approx(ref)


# ------------------------------------------------------------------ pooled weighting
def test_repository_and_site_weighting_differ_with_unequal_denominators():
    v, n = [0.10, -0.05, 0.00], [30, 10, 20]
    assert MR.pooled(v, n, "repository") == pytest.approx(0.05 / 3)
    assert MR.pooled(v, n, "site") == pytest.approx((3.0 - 0.5) / 60)
    assert MR.pooled(v, [30, 30, 30], "repository") == pytest.approx(MR.pooled(v, [30, 30, 30], "site"))


# ------------------------------------------------------------------ coverage-gap guard
@pytest.mark.parametrize("R_f,R_m,n,g,active", [
    ([3], [3], [30], Fraction(0), True),                     # zero gap
    ([2], [5], [30], Fraction(-1, 10), True),                # negative gap (comparator covers more)
    ([5], [3], [30], Fraction(1, 15), True),                 # 0 < g < 0.10
    ([9], [6], [30], Fraction(1, 10), False),                # g = 0.10 exactly: not active
    ([10], [6], [30], Fraction(2, 15), False),               # g > 0.10
    ([21, 0], [0, 15], [30, 30], Fraction(1, 10), False),    # repository-balanced: (0.7 - 0.5) / 2 = 0.10 exactly
    ([20, 10], [10, 10], [25, 20], Fraction(1, 5), False),   # unequal denominators: (0.4 + 0) / 2 = 0.20
])
def test_guard_boundaries(R_f, R_m, n, g, active):
    got = MR.coverage_gap(R_f, R_m, n)
    assert got == g and MR.guard_active(got) is active


def test_guard_is_exact_just_below_the_boundary():
    g = MR.coverage_gap([20, 0], [0, 15], [30, 30])    # (2/3 - 1/2)/2 = 1/12 < 1/10
    assert g == Fraction(1, 12) and MR.guard_active(g)


def test_guarded_p_doubles_and_caps():
    assert MR.guarded_p(0.004, Fraction(0)) == pytest.approx(0.008)
    assert MR.guarded_p(0.7, Fraction(-1, 3)) == 1.0
    assert MR.guarded_p(0.004, Fraction(1, 10)) == 0.004


def test_guard_rejects_bad_inputs():
    with pytest.raises(ValueError):
        MR.coverage_gap([1], [1, 2], [3])
    with pytest.raises(ValueError):
        MR.coverage_gap([1], [1], [0])


# ------------------------------------------------------------------ feasibility gate
def test_gate_cases():
    n = [30] * 7
    few = MR.feasibility([6, 6, 6, 6, 6, 0, 0], n)                                  # 5 feasible but 30/210 < 0.20
    assert not few["passes"] and few["n_feasible"] == 5
    pass_case = MR.feasibility([9, 9, 9, 9, 6, 0, 0], n)                             # 42/210 = 0.20 exactly, 5 feasible
    assert pass_case["pooled_matched_coverage"] == Fraction(1, 5) and pass_case["passes"]
    four = MR.feasibility([20, 20, 20, 20, 4, 4, 4], n)                              # coverage high, only 4 feasible
    assert not four["passes"] and four["n_feasible"] == 4
    low = MR.feasibility([6, 6, 6, 6, 6, 6, 5], n)                                   # 41/210 < 0.20
    assert not low["passes"] and low["n_feasible"] == 7


# ------------------------------------------------------------------ Holm
def test_holm_matches_stats_v4():
    rng = np.random.default_rng(5)
    for _ in range(200):
        p = list(rng.random(3) * 0.05)
        assert MR.holm(p) == pytest.approx(list(S.holm_adjust(np.array(p))))


# ------------------------------------------------------------------ execution failures
def test_execution_partition_and_common_set():
    sites = [site(i) for i in range(5)]
    f = [rec("T2"), EF, rec("T3"), EF, AB]
    m = [rec("T1"), EF, EF, AB, AB]
    part = MR.execution_partition([s["site_id"] for s in sites], f, m)
    assert part == {"both": ["x0", "x4"], "f_only": ["x2"], "m_only": ["x3"], "neither": ["x1"]}
    rep = MR.evaluate_repository(sites, f, m, comparison="c", repo="r")
    assert rep["n_eligible"] == 5 and rep["n_common"] == 2
    assert rep["exec_fail_f"] == 2 and rep["exec_fail_m"] == 2
    # S-F1: x2 (only F ran) is scored for F (CORRECT SIG on SIGN), x3 (only M ran) for M (UNASSESSABLE)
    assert rep["delta_failures_not_correct"] == pytest.approx((rep["delta_ta"] * 2 + 1 - 0) / 5)
    lo, hi = rep["delta_failure_bounds"]
    assert lo <= rep["delta_failures_not_correct"] <= hi


def test_concordant_failures_rescale_only():
    sites = [site(i) for i in range(6)]
    f = [rec("T2"), rec("T3"), EF, EF, AB, rec("T2")]
    m = [rec("T1"), AB, EF, EF, AB, AB]
    rep = MR.evaluate_repository(sites, f, m, comparison="c", repo="r")
    assert rep["partition"]["f_only"] == rep["partition"]["m_only"] == 0
    assert rep["delta_failures_not_correct"] == pytest.approx(rep["delta_ta"] * 4 / 6)


def test_repository_with_no_common_site_is_reported_not_dropped():
    sites = [site(0), site(1)]
    rep = MR.evaluate_repository(sites, [EF, EF], [EF, AB], comparison="c", repo="r")
    assert rep["n_common"] == 0 and rep["delta_ta"] is None and rep["n_eligible"] == 2


def test_evaluate_repository_report_fields():
    rep = MR.evaluate_repository(WE.EX_SITES, WE.EX_F, WE.EX_M, comparison="H2-1", repo="example")
    for key in ("n_eligible", "n_common", "R_f", "R_m", "k", "cov_f", "cov_m", "both_rec", "f_only_rec", "m_only_rec",
                "withdrawn_f", "correct_f", "incorrect_f", "delta_ta", "prec_f_nat", "prec_f_matched",
                "exec_fail_f", "n_indeterminate_common", "delta_ta_rankfree", "delta_seeds"):
        assert key in rep
    assert (rep["R_f"], rep["R_m"], rep["k"]) == (8, 5, 5)
    assert rep["prec_f_nat"] == (6, 8) and rep["prec_m_nat"] == (4, 5)
    assert rep["prec_f_matched"] == (4, 5) and rep["prec_m_matched"] == (4, 5)
    assert rep["n_indeterminate_common"] == 2
    assert len(rep["delta_seeds"]) == 100


def test_matched_precision_tie_average_worked_example():
    F, M = MR.site_arrays(WE.EX_SITES, WE.EX_F), MR.site_arrays(WE.EX_SITES, WE.EX_M)
    (cf, kf), (cm, km) = MR.matched_precision_ta(F, M)
    # F keeps s1, s2, s7 (T3, all correct) and 2 of the 4 tied T2 (s3, s5, s8 correct; s4 wrong): 3 + 2 x 3/4 = 4.5
    assert (kf, km) == (5, 5) and cf == pytest.approx(4.5) and cm == pytest.approx(4.0)
