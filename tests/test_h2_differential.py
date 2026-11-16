"""Differential verification: production H2 code vs the independent reference implementation (R4-19 item 17;
phase3_analysis_plan.md Sec. 11.1).

The reference (`docs/proposals/v1.0.4/rev4/scripts/matching_ref_v4.py`, written during the proposal stage and kept
unchanged) and the production modules (`pqscan/bench/matching.py`, `pqscan/bench/h2.py`, written from the adopted
plan) must agree exactly on the worked examples, the pilot tables, 1,000 random property cases and the bootstrap
distributions.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

from pqscan.bench import h2 as H
from pqscan.bench import matching as MT
from pqscan.bench.stats import holm

REF_DIR = Path(__file__).resolve().parents[1] / "docs" / "proposals" / "v1.0.4" / "rev4" / "scripts"
sys.path.insert(0, str(REF_DIR))
import matching_ref_v4 as REF  # noqa: E402
import worked_example_v12pp as WE12  # noqa: E402

ROLES = [("SIGN", "DETERMINATE"), ("VERIFY", "DETERMINATE"), ("KEY_ESTABLISHMENT", "DETERMINATE"),
         ("UNKNOWN", "INDETERMINATE"), ("KEY_MATERIAL_ONLY", "DETERMINATE"), ("PK_ENCRYPT", "DETERMINATE")]
ACTS = [("RECOMMEND", "SIG", "T0"), ("RECOMMEND", "SIG", "T1"), ("RECOMMEND", "SIG", "T2"), ("RECOMMEND", "KEM", "T2"),
        ("RECOMMEND", "SIG", "T3"), ("RECOMMEND", "KEM", "T3"), ("ABSTAIN", "NONE", "T1"), ("FLAG_NO_TARGET", "NONE", "T2"),
        ("NO_FINDING", "NONE", None)]


def to_ref(a):
    return REF.ArmOutput(a.action, a.rec_class, a.tier)


def to_prod(a):
    return MT.Output(a.action, a.rec_class, a.tier)


def random_case(rng, n=None, hybrid=True):
    n = n or int(rng.integers(1, 31))
    labels = []
    for i in range(n):
        role, ass = ROLES[rng.integers(0, len(ROLES))]
        labels.append({"site_id": f"s{i}", "eligible": "yes", "gt_role": role, "assessability": ass,
                       "hybrid_component": "yes" if (hybrid and rng.random() < 0.05) else "no"})
    f = [MT.Output(*ACTS[i]) for i in rng.integers(0, len(ACTS), n)]
    m = [MT.Output(*ACTS[i]) for i in rng.integers(0, len(ACTS), n)]
    return labels, f, m


def ref_arrays(labels, outs):
    return REF.site_arrays(labels, [to_ref(o) for o in outs])


# ------------------------------------------------------------------ 1,000 random property cases
def test_1000_random_cases_identical():
    rng = np.random.default_rng(20261116)
    for case in range(1000):
        labels, f, m = random_case(rng)
        ids = [l["site_id"] for l in labels]
        ref_m = REF.match_repository(ids, [to_ref(a) for a in f], [to_ref(a) for a in m], comparison="H2-1", repo=f"r{case}")
        pro_m = MT.match(ids, f, m, comparison="H2-1", repo=f"r{case}")
        assert (ref_m.k, ref_m.R_f, ref_m.R_m) == (pro_m.k, pro_m.R_f, pro_m.R_m)
        assert ref_m.withdrawn_f == pro_m.withdraw_f and ref_m.withdrawn_m == pro_m.withdraw_m
        ref_free = REF.match_repository(ids, [to_ref(a) for a in f], [to_ref(a) for a in m], comparison="H2-1",
                                        repo=f"r{case}", order="hash")
        pro_free = MT.match(ids, f, m, comparison="H2-1", repo=f"r{case}", ranking=False)
        assert ref_free.withdrawn_f == pro_free.withdraw_f and ref_free.withdrawn_m == pro_free.withdraw_m
        pr = MT.repository_result(labels, f, m, comparison="H2-1", repo=f"r{case}", seeds=())
        rf, rmm = [to_ref(a) for a in f], [to_ref(a) for a in m]
        assert pr["delta_ta"] == pytest.approx(REF.tie_average_delta(labels, rf, rmm, comparison="H2-1", repo=f"r{case}"), abs=1e-12)
        assert pr["delta_rankfree"] == pytest.approx(REF.tie_average_delta(labels, rf, rmm, comparison="H2-1", repo=f"r{case}",
                                                                           order="hash"), abs=1e-12)
        ref_c = REF.matched_comparison(labels, rf, rmm, comparison="H2-1", repo=f"r{case}")
        assert pr["seeded"]["delta"] == pytest.approx(ref_c["delta"], abs=1e-12)
        assert (pr["seeded"]["b"], pr["seeded"]["c"]) == (ref_c["b"], ref_c["c"])
        for p_arr, r_arr in zip(pr["arrays"][0] + pr["arrays"][1], ref_arrays(labels, f) + ref_arrays(labels, m)):
            assert np.array_equal(p_arr, r_arr)
        if pr["k"]:
            (cf, kf), (cm, km) = REF.matched_precision_ta(ref_arrays(labels, f), ref_arrays(labels, m))
            assert pr["prec_matched_f"] == pytest.approx(cf / kf) and pr["prec_matched_m"] == pytest.approx(cm / km)


def test_random_guard_gate_and_holm_identical():
    rng = np.random.default_rng(7)
    for _ in range(1000):
        K = 7
        n = rng.integers(1, 31, K)
        Rf = [int(rng.integers(0, x + 1)) for x in n]
        Rm = [int(rng.integers(0, x + 1)) for x in n]
        k = [min(a, b) for a, b in zip(Rf, Rm)]
        res = [{"repo": f"r{i}", "R_f": Rf[i], "R_m": Rm[i], "n_common": int(n[i]), "k": k[i]} for i in range(K)]
        g_ref = REF.coverage_gap(Rf, Rm, [int(x) for x in n])
        assert H.coverage_gap(res) == g_ref and H.guard_active(g_ref) == REF.guard_active(g_ref)
        gate_ref = REF.feasibility(k, [int(x) for x in n])
        gate_pro = H.gate(res)
        assert gate_pro["passes"] == gate_ref["passes"] and gate_pro["c_pool"] == gate_ref["pooled_matched_coverage"]
        assert gate_pro["n_feasible"] == gate_ref["n_feasible"]
        p = list(rng.random(3) * 0.05)
        assert holm(p) == pytest.approx(REF.holm(p))
        assert H.guarded(p[0], g_ref) == pytest.approx(REF.guarded_p(p[0], g_ref))


# ------------------------------------------------------------------ bootstrap distributions
@pytest.mark.parametrize("seed", [20261113, 1, 99])
def test_bootstrap_distribution_identical_to_reference(seed):
    rng = np.random.default_rng(seed)
    repos = []
    for _ in range(7):
        labels, f, m = random_case(rng, n=30)
        repos.append((ref_arrays(labels, f), ref_arrays(labels, m)))
    _, ref_dist = REF.bootstrap_pvalue(repos, B=4000, seed=seed, chunk=2000, return_dist=True)
    pro = H.bootstrap(repos, B=4000, seed=seed, chunk=2000)
    assert np.allclose(pro, ref_dist, atol=1e-12)
    assert H.p_value(pro, 0.0) == pytest.approx(REF.bootstrap_pvalue(repos, B=4000, seed=seed, chunk=2000))


# ------------------------------------------------------------------ worked examples and pilot
def test_three_repository_worked_example_identical():
    for name, sites, f, m in WE12.REPOS:
        ref = REF.evaluate_repository(sites, f, m, comparison="H2-1", repo=name)
        pro = MT.repository_result(sites, [to_prod(a) for a in f], [to_prod(a) for a in m], comparison="H2-1", repo=name)
        assert pro["n_common"] == ref["n_common"] and pro["n_eligible"] == ref["n_eligible"]
        assert (pro["k"], pro["R_f"], pro["R_m"]) == (ref["k"], ref["R_f"], ref["R_m"])
        assert pro["delta_ta"] == pytest.approx(ref["delta_ta"]) and pro["delta_rankfree"] == pytest.approx(ref["delta_ta_rankfree"])
        assert pro["seeded"]["delta"] == pytest.approx(ref["delta_seed"]) and pro["seed_deltas"] == pytest.approx(ref["delta_seeds"])
        assert pro["delta_sf1"] == pytest.approx(ref["delta_failures_not_correct"])
        assert pro["delta_sf2"] == pytest.approx(ref["delta_failure_bounds"])
        assert (pro["both_rec"], pro["f_only_rec"], pro["m_only_rec"]) == (ref["both_rec"], ref["f_only_rec"], ref["m_only_rec"])
    expected = {"example": 1.5 / 12, "B": 0.0, "C": 1 / 6}                      # R4-03b / worked_example_v12pp.md
    for name, sites, f, m in WE12.REPOS:
        r = MT.repository_result(sites, [to_prod(a) for a in f], [to_prod(a) for a in m], comparison="H2-1", repo=name, seeds=())
        assert r["delta_ta"] == pytest.approx(expected[name])


def test_pilot_tables_identical():
    import csv
    root = Path(__file__).resolve().parents[1]
    rows = list(csv.DictReader((root / "docs/dev/pilot_harness/judgments.csv").open(encoding="utf-8")))
    rp = {x["site_id"]: x for x in csv.DictReader((root / "docs/dev/roles_on_pilot.csv").open(encoding="utf-8"))}
    sites = [x for x in rows if x["method"] == "pqscan:B3-full-noabst" and x["eligible"] == "yes"]
    labels = [{"site_id": x["site_id"], "eligible": "yes", "gt_role": x["gt_role"], "assessability": x["assessability"],
               "hybrid_component": x["hybrid_component"]} for x in sites]
    arms = {a: [WE12.derive(rp[x["site_id"]][f"{a}:role"], rp[x["site_id"]][f"{a}:tier"], x["hybrid_component"] == "yes") for x in sites]
            for a in ("full", "method+args", "method+args+recv", "method-only")}
    expected = {"paramiko": 2 / 17, "python-jose": 0.0}                          # results/pilot_v12pp.md (development, circular)
    for comp, other in (("H2-1", "method+args"), ("H2-3", "method+args+recv"), ("H2-4", "method-only")):
        for repo in ("paramiko", "python-jose"):
            ix = [i for i, x in enumerate(sites) if x["repo"] == repo]
            L = [labels[i] for i in ix]
            ref = REF.evaluate_repository(L, [arms["full"][i] for i in ix], [arms[other][i] for i in ix], comparison=comp, repo=repo)
            pro = MT.repository_result(L, [to_prod(arms["full"][i]) for i in ix], [to_prod(arms[other][i]) for i in ix],
                                       comparison=comp, repo=repo, seeds=())
            assert pro["delta_ta"] == pytest.approx(ref["delta_ta"]) == pytest.approx(expected[repo])
            assert (pro["k"], pro["R_f"], pro["R_m"]) == (ref["k"], ref["R_f"], ref["R_m"])
