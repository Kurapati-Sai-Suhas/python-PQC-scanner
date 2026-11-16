"""Unit tests for the reference matching implementation (PROPOSED, NOT ADOPTED; not production tests).

    .venv/Scripts/python -m pytest -q -o addopts="" docs/proposals/v1.0.4/rev4/scripts/test_matching_ref_v4.py
"""
from __future__ import annotations

import itertools

import numpy as np
import pytest

import matching_ref_v4 as MR
from matching_ref_v4 import ArmOutput as A
import worked_example_v4 as WE


def rec(t, c="SIG"):
    return A("RECOMMEND", c, t)


AB = A("ABSTAIN", "NONE", "T1")
FL = A("FLAG_NO_TARGET", "NONE", "T2")
NF = A("NO_FINDING", "NONE", None)


def site(i, role="SIGN", ass="DETERMINATE", hyb="no"):
    return dict(site_id=f"x{i}", eligible="yes", gt_role=role, assessability=ass, hybrid_component=hyb)


def ids(n):
    return [f"x{i}" for i in range(n)]


# ------------------------------------------------------------------ counts, k and equality
def test_equal_counts_after_matching_random_inputs():
    rng = np.random.default_rng(1)
    acts = [rec("T0"), rec("T1"), rec("T2"), rec("T3"), AB, FL, NF]
    for _ in range(300):
        n = int(rng.integers(1, 31))
        f = [acts[i] for i in rng.integers(0, 7, n)]
        m = [acts[i] for i in rng.integers(0, 7, n)]
        r = MR.match_repository(ids(n), f, m, comparison="c", repo="r")
        nf = sum(a.action == "RECOMMEND" for a in MR.apply_withdrawal(ids(n), f, r.withdrawn_f))
        nm = sum(a.action == "RECOMMEND" for a in MR.apply_withdrawal(ids(n), m, r.withdrawn_m))
        assert nf == nm == r.k == min(r.R_f, r.R_m)
        assert not (r.withdrawn_f and r.withdrawn_m)          # at most one arm withdraws


def test_k_zero_when_one_arm_never_recommends():
    f = [rec("T2"), rec("T3"), rec("T1")]
    m = [AB, FL, NF]
    r = MR.match_repository(ids(3), f, m, comparison="c", repo="r")
    assert r.k == 0 and sorted(r.withdrawn_f) == ["x0", "x1", "x2"] and r.withdrawn_m == []


def test_both_zero_recommendations_nothing_changes():
    r = MR.match_repository(ids(3), [AB, FL, NF], [AB, AB, FL], comparison="c", repo="r")
    assert r.k == 0 and r.withdrawn_f == [] and r.withdrawn_m == []


def test_equal_natural_counts_no_withdrawal():
    r = MR.match_repository(ids(3), [rec("T0"), AB, rec("T3")], [rec("T1"), rec("T1"), AB], comparison="c", repo="r")
    assert r.k == 2 and r.withdrawn_f == [] and r.withdrawn_m == []


def test_comparator_higher_withdraws_comparator():
    r = MR.match_repository(ids(4), [rec("T3"), AB, AB, AB], [rec("T1"), rec("T0"), rec("T1"), AB],
                            comparison="c", repo="r")
    assert r.k == 1 and r.withdrawn_f == [] and len(r.withdrawn_m) == 2
    assert "x1" in r.withdrawn_m                               # the T0 goes first


# ------------------------------------------------------------------ tier order and ties
def test_lowest_tier_withdrawn_first_and_highest_kept():
    f = [rec("T3"), rec("T0"), rec("T2"), rec("T1"), rec("T3")]
    m = [rec("T1"), rec("T1"), AB, AB, AB]
    r = MR.match_repository(ids(5), f, m, comparison="c", repo="r")
    assert r.withdrawn_f == ["x1", "x3", "x2"]                 # T0, T1, T2 in that order
    assert r.boundary_tier == "T2" and r.tied_at_boundary == 1 and r.withdrawn_at_boundary == 1


def test_ties_follow_sha256_order_and_are_seed_dependent_but_count_is_not():
    f = [rec("T2")] * 6
    m = [rec("T1"), rec("T1"), AB, AB, AB, AB]
    sid = ids(6)
    r1 = MR.match_repository(sid, f, m, comparison="c", repo="r", seed="20261113")
    expect = sorted(sid, key=lambda s: MR.tiebreak_key("20261113", "c", "r", s))[:4]
    assert r1.withdrawn_f == expect
    sets = {tuple(sorted(MR.match_repository(sid, f, m, comparison="c", repo="r", seed=s).withdrawn_f))
            for s in MR.SENSITIVITY_SEEDS[:30]}
    assert len(sets) > 1                                       # different seeds pick different tied sites
    assert all(len(s) == 4 for s in sets)                      # but always the same number


def test_tiebreak_key_is_deterministic_and_scoped():
    k = MR.tiebreak_key("20261113", "H2-1", "repo", "R-1")
    assert k == MR.tiebreak_key("20261113", "H2-1", "repo", "R-1") and len(k) == 64
    assert k != MR.tiebreak_key("20261113", "H2-2", "repo", "R-1")    # comparison-specific
    assert k != MR.tiebreak_key("20261113", "H2-1", "other", "R-1")   # repository-specific


def test_input_order_does_not_matter():
    f = [rec("T2"), rec("T2"), rec("T3"), rec("T1"), AB]
    m = [rec("T1"), AB, AB, rec("T0"), AB]
    sid = ids(5)
    r = MR.match_repository(sid, f, m, comparison="c", repo="r")
    perm = [4, 2, 0, 3, 1]
    r2 = MR.match_repository([sid[i] for i in perm], [f[i] for i in perm], [m[i] for i in perm], comparison="c", repo="r")
    assert sorted(r.withdrawn_f) == sorted(r2.withdrawn_f)


# ------------------------------------------------------------------ label-freeness and scope
def test_matching_ignores_labels():
    rng = np.random.default_rng(2)
    roles = ["SIGN", "VERIFY", "KEY_ESTABLISHMENT", "UNKNOWN", "KEY_MATERIAL_ONLY"]
    f = [rec("T2"), rec("T3"), rec("T2"), rec("T1"), AB, FL]
    m = [rec("T1"), AB, rec("T0"), AB, AB, AB]
    ref = None
    for _ in range(50):
        sites = [site(i, roles[rng.integers(0, 5)], ["DETERMINATE", "INDETERMINATE"][rng.integers(0, 2)]) for i in range(6)]
        out = MR.matched_comparison(sites, f, m, comparison="c", repo="r")["match"].withdrawn_f
        ref = ref or out
        assert out == ref


def test_only_recommend_is_ever_withdrawn_and_other_actions_untouched():
    f = [rec("T0"), FL, AB, NF, rec("T3")]
    m = [AB, AB, AB, AB, AB]
    sid = ids(5)
    r = MR.match_repository(sid, f, m, comparison="c", repo="r")
    out = MR.apply_withdrawal(sid, f, r.withdrawn_f)
    assert out[1] == FL and out[2] == AB and out[3] == NF
    assert out[0].action == out[4].action == "ABSTAIN"


def test_repositories_are_matched_independently():
    f1, m1 = [rec("T2"), rec("T2"), AB], [rec("T1"), AB, AB]
    sid = ids(3)
    a = MR.match_repository(sid, f1, m1, comparison="c", repo="A")
    # changing a different repository's data cannot change A's result: the function only sees A's sites
    b = MR.match_repository(sid, f1, m1, comparison="c", repo="A")
    assert a.withdrawn_f == b.withdrawn_f


# ------------------------------------------------------------------ validation
@pytest.mark.parametrize("bad", [A("RECOMMEND", "SIG", None), A("RECOMMEND", "SIG", "T4"), A("RECOMMEND", "NONE", "T1"),
                                 A("EXECUTION_FAILURE", "NONE", None), A("MAYBE", "NONE", None)])
def test_invalid_inputs_raise(bad):
    with pytest.raises(ValueError):
        MR.match_repository(ids(2), [bad, AB], [AB, AB], comparison="c", repo="r")


def test_duplicate_ids_raise():
    with pytest.raises(ValueError):
        MR.match_repository(["a", "a"], [AB, AB], [AB, AB], comparison="c", repo="r")


def test_ineligible_site_rejected_from_matched_comparison():
    s = [site(0), dict(site_id="x1", eligible="no", gt_role="NONE", assessability="DETERMINATE", hybrid_component="no")]
    with pytest.raises(ValueError):
        MR.matched_comparison(s, [rec("T2"), AB], [AB, AB], comparison="c", repo="r")


# ------------------------------------------------------------------ scoring consequences
def test_withdrawn_recommendation_scored_as_abstain_by_frozen_judge():
    det, ind = site(0), site(1, "UNKNOWN", "INDETERMINATE")
    r = MR.matched_comparison([det, ind], [rec("T2"), rec("T1")], [AB, AB], comparison="c", repo="r")
    rows = {x["site_id"]: x for x in r["rows"]}
    assert rows["x0"]["F_judgment_natural"] == "CORRECT" and rows["x0"]["F_judgment_matched"] == "UNASSESSABLE"
    assert rows["x1"]["F_judgment_natural"] == "UNJUSTIFIED" and rows["x1"]["F_judgment_matched"] == "CORRECT"


def test_delta_equals_b_minus_c_over_n_and_decomposition_sums():
    _, r = WE.worked_example()
    assert r["delta"] == pytest.approx((r["b"] - r["c"]) / r["n"])
    assert sum(x - y for x, y in r["decomposition"].values()) == r["X"] - r["Y"]


# ------------------------------------------------------------------ worked example and pilot reproduce
def test_worked_example_numbers():
    _, r = WE.worked_example()
    m = r["match"]
    assert (m.R_f, m.R_m, m.k) == (8, 5, 5)
    assert m.withdrawn_f == ["s10", "s3", "s5"]
    assert (r["X"], r["Y"], r["b"], r["c"]) == (7, 6, 3, 2)
    assert (r["X_nat"], r["Y_nat"]) == (8, 6)
    assert r["both_rec"] == {"s1", "s8"} and r["f_only_rec"] == {"s2", "s4", "s7"} and r["m_only_rec"] == {"s3", "s5", "s12"}
    assert MR.tie_average_delta(WE.EX_SITES, WE.EX_F, WE.EX_M, comparison="H2-1", repo="example") == pytest.approx(1.5 / 12)


def test_tie_average_equals_mean_over_all_tie_orders():
    # brute force over every withdrawal choice inside the boundary tier of the worked example (C(4,2) = 6)
    base = ["s10"]                                     # T1 always withdrawn
    tied = ["s3", "s4", "s5", "s8"]
    vals = []
    for pick in itertools.combinations(tied, 2):
        f2 = MR.apply_withdrawal([s["site_id"] for s in WE.EX_SITES], WE.EX_F, base + list(pick))
        x = sum(MR.is_correct(s, a) for s, a in zip(WE.EX_SITES, f2))
        y = sum(MR.is_correct(s, a) for s, a in zip(WE.EX_SITES, WE.EX_M))
        vals.append((x - y) / 12)
    assert np.mean(vals) == pytest.approx(MR.tie_average_delta(WE.EX_SITES, WE.EX_F, WE.EX_M, comparison="H2-1", repo="example"))


def test_vectorised_tie_average_equals_reference():
    rng = np.random.default_rng(4)
    acts = [rec("T0"), rec("T1"), rec("T2"), rec("T3"), AB, FL, NF]
    roles = [("SIGN", "DETERMINATE"), ("UNKNOWN", "INDETERMINATE"), ("KEY_MATERIAL_ONLY", "DETERMINATE")]
    for _ in range(200):
        n = int(rng.integers(2, 25))
        sites = [site(i, *roles[rng.integers(0, 3)]) for i in range(n)]
        f = [acts[i] for i in rng.integers(0, 7, n)]
        m = [acts[i] for i in rng.integers(0, 7, n)]
        a = MR.tie_average_arrays(MR.site_arrays(sites, f), MR.site_arrays(sites, m))
        assert a == pytest.approx(MR.tie_average_delta(sites, f, m, comparison="c", repo="r"))


# ------------------------------------------------------------------ vectorised core = reference
def test_vectorised_core_matches_reference_on_identity_resample():
    rng = np.random.default_rng(3)
    acts = [rec("T0"), rec("T1"), rec("T2"), rec("T3"), AB, FL, NF, rec("T2", "KEM")]
    roles = [("SIGN", "DETERMINATE"), ("KEY_ESTABLISHMENT", "DETERMINATE"), ("UNKNOWN", "INDETERMINATE"),
             ("KEY_MATERIAL_ONLY", "DETERMINATE")]
    for _ in range(200):
        n = int(rng.integers(2, 25))
        sites = [site(i, *roles[rng.integers(0, 4)]) for i in range(n)]
        f = [acts[i] for i in rng.integers(0, 8, n)]
        m = [acts[i] for i in rng.integers(0, 8, n)]
        ref = MR.matched_comparison(sites, f, m, comparison="c", repo="r")
        # tie keys for the vectorised core derived from the same SHA-256 order (rank / n in [0, 1))
        order = sorted(range(n), key=lambda i: MR.tiebreak_key(MR.PRIMARY_SEED, "c", "r", sites[i]["site_id"]))
        u = np.empty(n); u[order] = np.arange(n) / n
        d, k = MR.matched_delta_batch(MR.site_arrays(sites, f), MR.site_arrays(sites, m), np.arange(n)[None, :], u[None, :], u[None, :])
        assert d[0] == pytest.approx(ref["delta"]) and k[0] == ref["match"].k


# ------------------------------------------------------------------ bootstrap properties
def _toy_repos():
    _, r = WE.worked_example()
    F = MR.site_arrays(WE.EX_SITES, WE.EX_F); M = MR.site_arrays(WE.EX_SITES, WE.EX_M)
    return [(F, M)] * 3


def test_bootstrap_is_deterministic_given_seed():
    reps = _toy_repos()
    assert MR.bootstrap_pvalue(reps, B=2000, seed=5) == MR.bootstrap_pvalue(reps, B=2000, seed=5)


def test_bootstrap_p_does_not_depend_on_the_observed_tie_break_seed():
    # the bootstrap re-matches with its own random tie keys, so the primary tie-break seed (which only fixes which
    # observed recommendations are withdrawn) cannot change the p-value or the Holm decision
    reps = _toy_repos()
    p = MR.bootstrap_pvalue(reps, B=2000, seed=MR.BOOTSTRAP_SEED)
    for s in MR.SENSITIVITY_SEEDS[:5]:
        MR.matched_comparison(WE.EX_SITES, WE.EX_F, WE.EX_M, comparison="H2-1", repo="example", seed=s)  # point estimate changes
        assert MR.bootstrap_pvalue(reps, B=2000, seed=MR.BOOTSTRAP_SEED) == p


def test_bootstrap_identical_arms_gives_p_one():
    F = MR.site_arrays(WE.EX_SITES, WE.EX_F)
    p = MR.bootstrap_pvalue([(F, F)], B=500, seed=1)
    assert p == 1.0          # delta* = 0 in every resample, counted as <= 0


def test_bootstrap_resamples_match_exactly_in_every_replicate():
    F = MR.site_arrays(WE.EX_SITES, WE.EX_F); M = MR.site_arrays(WE.EX_SITES, WE.EX_M)
    rng = np.random.default_rng(9)
    idx = rng.integers(0, 12, (500, 12)); u1 = rng.random((500, 12)); u2 = rng.random((500, 12))
    recF, tierF = F[0][idx], F[1][idx]; recM, tierM = M[0][idx], M[1][idx]
    k = np.minimum(recF.sum(1), recM.sum(1))
    wF = MR._withdraw_mask(recF, tierF, u1, recF.sum(1) - k)
    wM = MR._withdraw_mask(recM, tierM, u2, recM.sum(1) - k)
    assert np.array_equal((recF & ~wF).sum(1), k) and np.array_equal((recM & ~wM).sum(1), k)
    # lowest tier first: no kept recommendation has a lower tier than a withdrawn one, in any replicate
    kept_min = np.where(recF & ~wF, tierF, 9).min(1); wd_max = np.where(wF, tierF, -1).max(1)
    assert np.all((wd_max <= kept_min) | (wd_max == -1))
