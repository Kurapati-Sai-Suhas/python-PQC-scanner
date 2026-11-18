"""H2 comparison arms and equal-coverage matching (R4-19 items 8-9; phase3_analysis_plan.md Sec. 1, 3-6)."""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pytest

from pqscan.baselines import simple
from pqscan.bench import matching as MT
from pqscan.bench.matching import MatchingError, Output as O
from pqscan.bench.run import judge_ours
from pqscan.policy import load_policy
from pqscan.roles import classify
from pqscan.semantic.evidence import analyze_source


# ------------------------------------------------------------------ item 8: T0 arms and shared evidence
SRC = (
    "from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec\n"
    "from cryptography.hazmat.primitives import hashes\n"
    "def sign(m):\n"
    "    k = rsa.generate_private_key(public_exponent=65537, key_size=3072)\n"
    "    return k.sign(m, padding.PKCS1v15(), hashes.SHA256())\n"
    "def kex(peer):\n"
    "    p = ec.generate_private_key(ec.SECP256R1())\n"
    "    return p.exchange(ec.ECDH(), peer)\n"
    "def unknown(key, m):\n"
    "    return key.sign(m, padding.PKCS1v15(), hashes.SHA256())\n")


def test_h2_comparisons_use_the_v18_arms():
    assert simple.H2_COMPARISONS == {"H2-1": ("B3-full-noabst", "B2-method-args"),
                                     "H2-3": ("B3-full-noabst", "method-args-recv-T0"),
                                     "H2-4": ("B3-full-noabst", "method-only-T0"),
                                     "H2-S": ("B4-full-T2", "B2-method-args")}
    assert set(simple.H2_ARMS) == {a for pair in simple.H2_COMPARISONS.values() for a in pair}
    assert simple.ARMS == ("B1-algorithm", "B1-dual", "B2-method-args", "B3-full-noabst", "B4-full-T2")  # unchanged


@pytest.mark.parametrize("arm,cls_arm", [("method-args-recv-T0", "method+args+recv"), ("method-only-T0", "method-only")])
def test_new_t0_arms_equal_classifier_plus_policy_at_t0(arm, cls_arm):
    pol = load_policy(tier_threshold="T0")
    for ev in analyze_source("m.py", SRC):
        if ev.site_kind not in ("operation", "key-material"):
            continue
        d = classify(ev, cls_arm)
        action, rec_class, tier, _ = simple.decide(ev, arm)
        assert tier == d.tier.value
        if d.role is None:
            assert action == "NO_FINDING"
            continue
        rec = pol.apply(d, ev.hybrid_apis, ev.hybrid_combined)
        assert action == rec.action and (action != "RECOMMEND" or rec_class == rec.family)


def test_all_h2_arms_share_one_parse_per_file(tmp_path, monkeypatch):
    import pqscan.bench.run as run
    (tmp_path / "r").mkdir()
    (tmp_path / "r" / "m.py").write_text(SRC, encoding="utf-8")
    calls = []
    real = run.analyze_source
    monkeypatch.setattr(run, "analyze_source", lambda *a, **k: calls.append(a[0]) or real(*a, **k))
    sites = [{"site_id": f"X{ln}", "repo": "r", "file": "m.py", "line_start": str(ln), "line_end": str(ln), "gt_role": "SIGN",
              "assessability": "DETERMINATE", "eligible": "yes", "hybrid_component": "no"} for ln in (4, 5, 8, 10)]
    rows = judge_ours(sites, tmp_path, arms=simple.H2_ARMS)
    assert calls == ["m.py"] and len(rows) == 4 * len(simple.H2_ARMS)


def test_parse_failure_is_concordant_across_h2_arms(tmp_path):
    (tmp_path / "r").mkdir()
    (tmp_path / "r" / "bad.py").write_text("from cryptography.hazmat.primitives.asymmetric import rsa\ndef f(:\n", encoding="utf-8")
    s = {"site_id": "X", "repo": "r", "file": "bad.py", "line_start": "1", "line_end": "2", "gt_role": "SIGN",
         "assessability": "DETERMINATE", "eligible": "yes", "hybrid_component": "no"}
    rows = judge_ours([s], tmp_path, arms=simple.H2_ARMS)
    assert {r["tool_action"] for r in rows} == {"EXECUTION_FAILURE"}


# ------------------------------------------------------------------ item 9: matching
def lab(i, role="SIGN", ass="DETERMINATE", hyb="no", stratum="S1-app"):
    return {"site_id": f"s{i}", "eligible": "yes", "gt_role": role, "assessability": ass, "hybrid_component": hyb,
            "stratum": stratum}


def rec(t, c="SIG"):
    return O("RECOMMEND", c, t)


AB, FL, NF, EF = O("ABSTAIN", "NONE", "T1"), O("FLAG_NO_TARGET", "NONE", "T2"), O("NO_FINDING"), O("EXECUTION_FAILURE")

# the 12-site worked example of R4-03b (hand-calculated there)
EX_LABELS = [lab(1), lab(2), lab(3, "KEY_ESTABLISHMENT"), lab(4, "VERIFY"), lab(5), lab(6, "UNKNOWN", "INDETERMINATE"),
             lab(7, "PK_ENCRYPT"), lab(8), lab(9), lab(10, "UNKNOWN", "INDETERMINATE"), lab(11, "KEY_MATERIAL_ONLY"),
             lab(12, "VERIFY")]
EX_F = [rec("T3"), rec("T3"), rec("T2", "KEM"), rec("T2", "KEM"), rec("T2"), O("ABSTAIN", "NONE", "T2"), rec("T3", "KEM"),
        rec("T2"), O("ABSTAIN", "NONE", "T1"), rec("T1"), O("FLAG_NO_TARGET", "NONE", "T2"), O("ABSTAIN", "NONE", "T2")]
EX_M = [rec("T1"), AB, rec("T1"), AB, rec("T0"), AB, AB, rec("T1"), O("ABSTAIN", "NONE", "T0"), AB, AB, rec("T1")]


def test_worked_example_anchor_values():
    r = MT.repository_result(EX_LABELS, EX_F, EX_M, comparison="H2-1", repo="example")
    assert (r["R_f"], r["R_m"], r["k"]) == (8, 5, 5)
    assert r["delta_ta"] == pytest.approx(1.5 / 12)                    # exact tie-average (R4-03b Sec. 7)
    assert r["seeded"]["delta"] == pytest.approx(1 / 12) and r["seeded"]["withdraw_f"] == ["s10", "s3", "s5"]
    assert (r["seeded"]["b"], r["seeded"]["c"]) == (3, 2)
    assert r["delta_rankfree"] == pytest.approx((6.125 - 6) / 12)      # R4-03b Sec. 9
    assert r["delta_nat"] == pytest.approx(2 / 12)
    assert r["prec_matched_f"] == pytest.approx(4.5 / 5) and r["prec_matched_m"] == pytest.approx(4 / 5)
    assert sum(r["seed_deltas"]) / 100 == pytest.approx(np.mean(r["seed_deltas"]))
    assert set(np.round(r["seed_deltas"], 6)) <= {round(1 / 12, 6), round(2 / 12, 6)}
    assert r["boundary_tier"] == "T2" and (r["boundary_size"], r["boundary_withdrawn"]) == (4, 2)
    dec = r["decomposition"]
    assert sum(a - b for a, b in dec.values()) == pytest.approx(r["delta_ta"] * 12)


def test_equal_counts_after_matching_and_only_recommend_withdrawn():
    rng = np.random.default_rng(1)
    acts = [rec("T0"), rec("T1"), rec("T2"), rec("T3"), AB, FL, NF]
    for _ in range(200):
        n = int(rng.integers(1, 25))
        ids = [f"s{i}" for i in range(n)]
        f = [acts[i] for i in rng.integers(0, 7, n)]
        m = [acts[i] for i in rng.integers(0, 7, n)]
        mt = MT.match(ids, f, m, comparison="c", repo="r")
        kept_f = sum(o.action == "RECOMMEND" and s not in mt.withdraw_f for s, o in zip(ids, f))
        kept_m = sum(o.action == "RECOMMEND" and s not in mt.withdraw_m for s, o in zip(ids, m))
        assert kept_f == kept_m == mt.k and not (mt.withdraw_f and mt.withdraw_m)
        assert all(o.action == "RECOMMEND" for s, o in zip(ids, f) if s in mt.withdraw_f)
        assert sum(mt.prob_f.values()) == pytest.approx(len(mt.withdraw_f))
        assert sum(mt.prob_m.values()) == pytest.approx(len(mt.withdraw_m))


def test_lowest_tier_first_and_hash_ties_and_seed_changes_identity_not_count():
    ids = ["a", "b", "c", "d", "e"]
    f = [rec("T3"), rec("T0"), rec("T2"), rec("T1"), rec("T3")]
    m = [rec("T1"), rec("T1"), AB, AB, AB]
    assert MT.match(ids, f, m, comparison="c", repo="r").withdraw_f == ["b", "d", "c"]
    f2 = [rec("T2")] * 6
    ids6 = [f"x{i}" for i in range(6)]
    m2 = [rec("T1")] * 2 + [AB] * 4
    first = MT.match(ids6, f2, m2, comparison="c", repo="r").withdraw_f
    assert first == sorted(ids6, key=lambda s: MT.tie_key(MT.PRIMARY_SEED, "c", "r", s))[:4]
    others = {tuple(sorted(MT.match(ids6, f2, m2, comparison="c", repo="r", seed=s).withdraw_f)) for s in MT.SENSITIVITY_SEEDS[:30]}
    assert len(others) > 1 and all(len(o) == 4 for o in others)


def test_k_zero_and_comparator_withdrawal():
    mt = MT.match(["a", "b"], [rec("T2"), rec("T3")], [AB, FL], comparison="c", repo="r")
    assert mt.k == 0 and sorted(mt.withdraw_f) == ["a", "b"]
    mt = MT.match(["a", "b", "c"], [rec("T3"), AB, AB], [rec("T1"), rec("T0"), rec("T1")], comparison="c", repo="r")
    assert mt.k == 1 and mt.withdraw_f == [] and "b" in mt.withdraw_m


@pytest.mark.parametrize("bad", [O("RECOMMEND", "SIG", None), O("RECOMMEND", "SIG", "T7"), O("RECOMMEND", "NONE", "T1"),
                                 O("MAYBE"), EF])
def test_matching_validation(bad):
    with pytest.raises(MatchingError):
        MT.match(["a", "b"], [bad, AB], [AB, AB], comparison="c", repo="r")
    with pytest.raises(MatchingError):
        MT.match(["a", "a"], [AB, AB], [AB, AB], comparison="c", repo="r")


def _brute(labels, f, m, ranking):
    """Independent check: average the matched difference over every withdrawal order the rule permits."""
    ids = [l["site_id"] for l in labels]
    rf = [i for i, o in enumerate(f) if o.action == "RECOMMEND"]
    rm = [i for i, o in enumerate(m) if o.action == "RECOMMEND"]
    k = min(len(rf), len(rm))
    arm, recs = (f, rf) if len(rf) > k else (m, rm)
    e = len(recs) - k
    vals = []
    for perm in itertools.permutations(recs):
        if ranking and any(MT.TIER_INDEX[arm[perm[i]].tier] > MT.TIER_INDEX[arm[perm[i + 1]].tier] for i in range(len(perm) - 1)):
            continue
        wd = set(perm[:e])
        a2 = [MT.WITHDRAWN if i in wd else o for i, o in enumerate(arm)]
        ff, mm = (a2, m) if arm is f else (f, a2)
        vals.append((sum(MT.correct(l, o) for l, o in zip(labels, ff)) - sum(MT.correct(l, o) for l, o in zip(labels, mm))) / len(ids))
    return float(np.mean(vals))


def test_tie_average_equals_brute_force_over_all_permitted_orders():
    rng = np.random.default_rng(7)
    roles = [("SIGN", "DETERMINATE"), ("KEY_ESTABLISHMENT", "DETERMINATE"), ("UNKNOWN", "INDETERMINATE"),
             ("KEY_MATERIAL_ONLY", "DETERMINATE")]
    acts = [rec("T0"), rec("T1"), rec("T2"), rec("T3"), rec("T2", "KEM"), AB, FL]
    for _ in range(40):
        n = int(rng.integers(3, 8))
        L = [lab(i, *roles[rng.integers(0, 4)]) for i in range(n)]
        f = [acts[i] for i in rng.integers(0, 7, n)]
        m = [acts[i] for i in rng.integers(0, 7, n)]
        r = MT.repository_result(L, f, m, comparison="c", repo="r", seeds=())
        if r["R_f"] == r["R_m"]:
            assert r["delta_ta"] == pytest.approx(r["delta_nat"])
            continue
        assert r["delta_ta"] == pytest.approx(_brute(L, f, m, True))
        assert r["delta_rankfree"] == pytest.approx(_brute(L, f, m, False))


def test_labels_never_affect_matching():
    rng = np.random.default_rng(3)
    f = [rec("T2"), rec("T3"), rec("T2"), rec("T1"), AB, FL]
    m = [rec("T1"), AB, rec("T0"), AB, AB, AB]
    ref = None
    for _ in range(30):
        L = [lab(i, ["SIGN", "VERIFY", "UNKNOWN"][rng.integers(0, 3)], ["DETERMINATE", "INDETERMINATE"][rng.integers(0, 2)])
             for i in range(6)]
        rr = MT.repository_result(L, f, m, comparison="c", repo="r", seeds=())["matching_record"]
        ref = ref or rr
        assert rr == ref                                   # identical label-free record and hash


# ------------------------------------------------------------------ execution failures (item 12 part)
def test_failure_partition_concordance_and_sensitivities():
    L = [lab(i) for i in range(6)]
    f = [rec("T2"), rec("T3"), EF, EF, AB, rec("T2")]
    m = [rec("T1"), AB, EF, EF, AB, AB]
    r = MT.repository_result(L, f, m, comparison="c", repo="r", seeds=())
    assert r["n_eligible"] == 6 and r["n_common"] == 4 and r["partition"]["neither"] == 2
    assert r["delta_sf1"] == pytest.approx(r["delta_ta"] * 4 / 6)            # concordant failures: rescaling only
    lo, hi = r["delta_sf2"]
    assert lo <= r["delta_sf1"] <= hi
    with pytest.raises(MatchingError, match="discordant"):
        MT.repository_result(L, [EF] + f[1:], m, comparison="c", repo="r", seeds=())
    r2 = MT.repository_result(L, [EF] + f[1:], m, comparison="c", repo="r", seeds=(), require_concordant=False)
    assert r2["partition"]["m_only"] == 1


def test_failures_reported_by_stratum_and_two_estimands_kept_apart():
    """F04 (plan v1.0.1): m_r,h of the sampled primary set and c_r,h of the common evaluable set are both reported,
    failures are partitioned by stratum, and with concordant failures S-F1 = (n_r/m_r) x primary, so the two coincide
    only when nothing failed."""
    L = [lab(0), lab(1), lab(2, stratum="S1-nonapp"), lab(3, stratum="S1-nonapp"), lab(4), lab(5, stratum="S1-nonapp")]
    f = [rec("T2"), rec("T3"), EF, rec("T2"), AB, EF]
    m = [rec("T1"), AB, EF, AB, AB, EF]
    r = MT.repository_result(L, f, m, comparison="c", repo="r", seeds=())
    assert r["strata_drawn"] == {"S1-app": 3, "S1-nonapp": 3}
    assert r["strata"] == {"S1-app": 3, "S1-nonapp": 1}
    assert r["failures_by_stratum"]["neither"] == {"S1-app": 0, "S1-nonapp": 2}
    assert r["failures_by_stratum"]["f_only"] == r["failures_by_stratum"]["m_only"] == {"S1-app": 0, "S1-nonapp": 0}
    assert r["n_eligible"] == 6 and r["n_common"] == 4
    assert r["delta_sf1"] == pytest.approx(r["delta_ta"] * r["n_common"] / r["n_eligible"])
    if r["delta_ta"] != 0:
        assert r["delta_sf1"] != pytest.approx(r["delta_ta"])            # never identical when failures exist
    clean = MT.repository_result(L, [rec("T2")] * 6, [AB] * 6, comparison="c", repo="r", seeds=())
    assert clean["n_common"] == clean["n_eligible"] and clean["delta_sf1"] == pytest.approx(clean["delta_ta"])


def test_repository_without_common_sites_is_reported_not_dropped():
    r = MT.repository_result([lab(0), lab(1)], [EF, EF], [EF, EF], comparison="c", repo="r", seeds=())
    assert r["n_common"] == 0 and r["delta_ta"] is None and r["estimable"] is False and r["n_eligible"] == 2


def test_ineligible_site_rejected():
    bad = dict(lab(0), eligible="no", gt_role="NONE")
    with pytest.raises(MatchingError):
        MT.repository_result([bad], [AB], [AB], comparison="c", repo="r", seeds=())
