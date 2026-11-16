"""Reliability statistics, frame audit and report generators (R4-19 items 13-15). Fixtures only."""
from __future__ import annotations

import math

import numpy as np
import pytest
from statsmodels.stats.inter_rater import cohens_kappa as sm_kappa

from pqscan.bench import frame_audit as FAU
from pqscan.bench import h2 as H
from pqscan.bench import matching as MT
from pqscan.bench import reliability as RL
from pqscan.bench import reporting as RP
from pqscan.bench.matching import Output as O


# ------------------------------------------------------------------ intra-rater sample
def _cands(N, repos=("a", "b", "c", "d", "e", "f")):
    return [{"candidate_id": f"C-{i:012x}", "repo": repos[i % len(repos)], "eligible": ((i // len(repos)) % 3 != 0)}
            for i in range(N)]


def test_intra_sample_size_allocation_and_balance():
    s = RL.intra_sample(_cands(600), "DV")
    assert s["N"] == 600 and s["n"] == max(50, math.ceil(60)) == 60
    assert all(v >= 3 for v in s["allocation"].values()) and sum(s["allocation"].values()) == 60
    for r in "abcdef":
        got = [c for c in s["sample"] if c["repo"] == r]
        e = sum(c["eligible"] for c in got)
        assert abs(e - (len(got) - e)) <= 1                       # half eligible, half ineligible
    assert s == RL.intra_sample(list(reversed(_cands(600))), "DV")  # deterministic
    assert RL.intra_sample(_cands(600), "T")["sample"] != s["sample"]  # phase-specific seed


def test_intra_sample_minimum_50_and_excludes_annotator_added():
    c = _cands(300) + [{"candidate_id": "A-000000000001", "repo": "a", "eligible": True, "annotator_added": True}]
    s = RL.intra_sample(c, "DV")
    assert s["n"] == 50 and all(not x.get("annotator_added") for x in s["sample"])
    assert RL.intra_sample(_cands(30), "DV")["n"] == 30         # N < 50: everything


def test_gap_rule():
    with pytest.raises(ValueError, match="wait until"):
        RL.check_gap(["2026-12-01T10:00:00Z", "2026-12-05T09:00:00Z"], "2026-12-18T23:59:00Z")
    RL.check_gap(["2026-12-01T10:00:00Z", "2026-12-05T09:00:00Z"], "2026-12-19T09:00:00Z")


def test_ai_repeat_sample():
    ids = [f"C-{i:012x}" for i in range(500)]
    s = RL.ai_repeat_sample(ids, "DV")
    assert len(s) == 50 and s == RL.ai_repeat_sample(list(reversed(ids)), "DV")
    assert len(RL.ai_repeat_sample(ids[:100], "T")) == 30


# ------------------------------------------------------------------ agreement statistics
def test_kappa_matches_statsmodels_and_specific_agreement():
    rng = np.random.default_rng(1)
    cats = ["SIGN", "VERIFY", "KEY_ESTABLISHMENT", "UNKNOWN"]
    a = [cats[i] for i in rng.integers(0, 4, 120)]
    b = [x if rng.random() < 0.8 else cats[rng.integers(0, 4)] for x in a]
    res = RL.field_agreement(a, b, ["r"] * 120, B=300)
    keys = sorted(res["confusion"])
    table = np.array([[res["confusion"][i][j] for j in keys] for i in keys])
    assert res["kappa"] == pytest.approx(sm_kappa(table).kappa)
    assert res["raw_agreement"] == pytest.approx(np.trace(table) / 120)
    c = keys[0]
    assert res["specific_agreement"][c] == pytest.approx(2 * table[0, 0] / (table[0].sum() + table[:, 0].sum()))
    lo, hi = res["kappa_ci95"]
    assert lo <= res["kappa"] <= hi


def _env(cid, role, ai_status=None, repo="r"):
    meta = {"candidate_id": cid}
    if ai_status:
        meta["ai"] = {"status": ai_status}
    return {"site": {"site_id": cid, "repo": repo, "eligible": True, "gt_role": role, "assessability": "DETERMINATE",
                     "possible_roles": [], "hybrid_component": False, "obvious_from_name": False,
                     "evidence_needed": "none", "key_provenance": "generated"}, "meta": meta}


def test_agreement_report_rule_and_insufficient_context():
    first = [_env(f"C-{i:012x}", "SIGN" if i % 2 else "VERIFY") for i in range(60)]
    second = [_env(f"C-{i:012x}", ["SIGN", "VERIFY", "UNKNOWN"][i % 3], "ok" if i else "insufficient_context") for i in range(60)]
    rep = RL.agreement_report(first, second, phase="DV", kind="owner-AI", B=200)
    assert rep["pairs"] == 59 and rep["excluded_insufficient_context"] == 1 and rep["rule"] is None
    intra = RL.agreement_report(first, [_env(f"C-{i:012x}", ["SIGN", "VERIFY", "UNKNOWN"][i % 3]) for i in range(60)],
                                phase="T", kind="intra-rater", B=200)
    assert intra["fields"]["gt_role"]["kappa"] < 0.60 and "exploratory" in intra["rule"]


# ------------------------------------------------------------------ frame audit
def test_frame_audit_worklist_stop_membership_and_share(tmp_path):
    for r in ("x", "y"):
        d = tmp_path / r
        d.mkdir()
        for i in range(3):
            (d / f"m{i}.py").write_text("from cryptography.hazmat.primitives.asymmetric import rsa\n"
                                        "k = rsa.generate_private_key(\n    public_exponent=65537, key_size=2048)\n"
                                        "s = k.sign(b'', None, None)\n", encoding="utf-8")
        (d / "plain.py").write_text("x = 1\n", encoding="utf-8")
    frames = {r: FAU.frame_files(tmp_path / r) for r in ("x", "y")}
    assert all(len(v) == 3 and "plain.py" not in v for v in frames.values())
    wl = FAU.worklist(frames)
    assert [r for r, _ in wl[:4]] == ["x", "y", "x", "y"] and wl == FAU.worklist(frames) and len(FAU.frame_hash(frames)) == 64
    audited = [{"repo": r, "file": f, "eligible_lines": [3, 5]} for r, f in wl]          # line 3 is inside the line-2 statement
    assert not FAU.stop_reached(audited) and FAU.stop_reached(audited * 6)
    pools = {"x": {(f, 2) for f in frames["x"]}, "y": set()}
    per = FAU.membership(audited, pools, {"x": tmp_path / "x", "y": tmp_path / "y"})
    assert per[0]["sites"][0]["statement"] == 2
    ms = FAU.missed_share(per, B=300)
    assert ms["eligible"] == 12 and ms["missed"] == 3 + 3 + 3 and ms["ci95"][0] <= ms["share"] <= ms["ci95"][1]


# ------------------------------------------------------------------ reporting
def _repo(name, rng):
    L, F, M = [], [], []
    for i in range(30):
        L.append({"site_id": f"s{i}", "eligible": True, "gt_role": "SIGN", "assessability": "DETERMINATE",
                  "hybrid_component": "no", "stratum": "S1-app" if i % 3 else "S1-nonapp"})
        F.append(O("RECOMMEND", "SIG", "T2") if rng.random() < 0.7 else O("ABSTAIN", "NONE", "T1"))
        M.append(O("RECOMMEND", "SIG", "T1") if rng.random() < 0.4 else O("ABSTAIN", "NONE", "T0"))
    return MT.repository_result(L, F, M, comparison="H2-1", repo=name, seeds=MT.SENSITIVITY_SEEDS[:5])


def test_report_generators_and_wording_rules():
    rng = np.random.default_rng(2)
    reps = [_repo(f"r{i}", rng) for i in range(7)]
    t = RP.repository_table(reps)
    assert t.count("\n") > 10 and "stratum allocation" in t
    fam = H.run_family({c: reps for c in H.CONFIRMATORY}, B=500)
    table = RP.h2_table(fam)
    assert "K = 7; K_e = 7" in table and "H2 supported" not in table
    s = RP.abstract_sentence(fam["H2-1"])
    assert "Results describe these repositories only." in s and "exploratory" in s
    with pytest.raises(ValueError):
        RP.check_wording("so H2 supported")
    with pytest.raises(ValueError):
        RP.check_wording("better recommendation accuracy")


def test_label_variants_and_analysis_sets():
    finals = [{"site": {"site_id": "a", "eligible": True, "gt_role": "SIGN", "assessability": "DETERMINATE", "hybrid_component": False},
               "meta": {"candidate_id": "a", "stratum": "S1-app", "unresolved": ["gt_role"]}},
              {"site": {"site_id": "b", "eligible": True, "gt_role": "VERIFY", "assessability": "DETERMINATE", "hybrid_component": False},
               "meta": {"candidate_id": "b", "stratum": "S2"}},
              {"site": {"site_id": "c", "eligible": False, "gt_role": "NONE", "assessability": "DETERMINATE", "hybrid_component": False},
               "meta": {"candidate_id": "c", "stratum": "S1-app", "annotator_added": True}}]
    ai = [{"site": {"site_id": "a", "gt_role": "PK_DECRYPT", "eligible": True, "assessability": "DETERMINATE", "hybrid_component": False}},
          {"site": {"site_id": "b", "gt_role": "VERIFY", "eligible": True, "assessability": "DETERMINATE", "hybrid_component": False}}]
    v = RP.label_variants(finals, ai)
    assert v["unresolved_ai"][0]["gt_role"] == "PK_DECRYPT" and v["unresolved_owner"][0]["gt_role"] == "SIGN"
    assert v["unresolved_indeterminate"][0]["assessability"] == "INDETERMINATE"
    assert [x["site_id"] for x in v["consensus"]] == ["b"]
    t = RP.analysis_set_tables(finals, {"qsafe": {"a", "c", "zzz"}})
    assert t["S2"] == {"labelled": 1, "eligible": 1} and t["annotator_added"]["count"] == 1
    assert t["false_positives"]["qsafe"] == {"findings_on_annotated": 2, "on_ineligible": 1}
