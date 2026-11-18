"""Cross-document consistency of the adopted Phase 3 protocol (R4-19 item 16).

These tests read the adopted documents and fail if a rule required by the owner's approval (R4-18 as amended by
R4-21, edge-case rules A-D) is missing, if the constants disagree between documents, or if the withdrawn phrase
"H2 supported" is used as a claim.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROTO = (ROOT / "docs/specification/evaluation_protocol.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs/specification/phase3_analysis_plan.md").read_text(encoding="utf-8")
DEC = (ROOT / "docs/specification/phase3_decisions.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "docs/benchmark/annotation_guide.md").read_text(encoding="utf-8")
ADOPTED = {"protocol": PROTO, "plan": PLAN, "decisions": DEC, "guide": GUIDE}
FROZEN_H2 = ("H2: correct-per-eligible-site of the provenance-aware arm exceeds the method+argument arm by "
             "≥ 10 percentage points at equal coverage.")


def test_versions():
    assert PROTO.startswith("# Evaluation protocol (v1.0.5, pre-registered)")
    assert GUIDE.startswith("# Annotation guide for PyPQC-RoleBench (v1.2)")
    assert "v1.0.4 (2026-11-16" in PROTO and "v1.0.5 (2026-11-18" in PROTO
    assert (ROOT / "docs/specification/evaluation_protocol_v1.0.3.md").exists()
    assert (ROOT / "docs/benchmark/annotation_guide_v1.0.md").exists()
    arch = ROOT / "docs/specification/archive/v1.0.4"
    assert (arch / "evaluation_protocol.md").read_text(encoding="utf-8").startswith(
        "# Evaluation protocol (v1.0.4, pre-registered)")
    assert (arch / "annotation_guide.md").read_text(encoding="utf-8").startswith(
        "# Annotation guide for PyPQC-RoleBench (v1.1)")


# ------------------------------------------------------------------ v1.0.5 owner-approved corrections (18 Nov 2026)
TAX = (ROOT / "docs/specification/role_taxonomy.md").read_text(encoding="utf-8")
DICT = (ROOT / "docs/specification/data_dictionary.md").read_text(encoding="utf-8")
SCORING = (ROOT / "docs/specification/scoring_policy.md").read_text(encoding="utf-8")
EVERY_DOC = {**ADOPTED, "taxonomy": TAX, "dictionary": DICT, "scoring": SCORING}


@pytest.mark.parametrize("name", list(EVERY_DOC))
def test_f06_blinding_never_claimed_enforced(name):
    for line in EVERY_DOC[name].splitlines():
        low = line.lower()
        if "blinding" in low and re.search(r"independently enforced|enforced blinding|verified blinding", low):
            assert re.search(r"not independently enforced|never (as|claimed)|never .*independently enforced", low), line


def test_f14_human_review_is_a_pending_f1_prerequisite():
    f1 = PROTO[PROTO.index("**Stage F1:"):PROTO.index("**Between F1 and F2")]
    assert "external human review record (mandatory" in f1 and "**pending**" in f1 and "not waived" in f1
    pol = (ROOT / "docs/specification/recommendation_policy.md").read_text(encoding="utf-8")
    assert "| pending | Human reviewer outside the build team" in pol      # never marked completed


def test_f04_estimands_kept_apart():
    assert "w_r,h = m_r,h / m_r" in PLAN and "Σ_h (m_r,h / n_r) · Uniform" not in PLAN.split("v1.0 wrote")[0]
    assert "estimates δ_r^ev" in PLAN and "S-F1 (Sec. 6) is a separate sensitivity analysis over the sampled primary set" in PLAN
    assert "**the two coincide** for repository r if and only if no eligible site fails" in PLAN
    assert "**never** described as measuring the full design mixture when failures exist" in PLAN


def test_f01_f21_taxonomy_and_guide_agree():
    assert "when it is (a), (b) or (c) above" in TAX
    assert "storage within the analysed scope only" in TAX
    assert "An observed escape takes precedence over" in GUIDE


def test_f17_f19_f20_wording():
    assert PLAN.count("not multiplicity-adjusted") >= 2 and "not adjusted for multiplicity" in PLAN
    assert "**c_DV (v1.0.1, F19)**" in PLAN
    assert "F1 is not permitted after a failed calibration" in PLAN and "F1 is never permitted after a failed calibration" in PROTO


def test_f18_frame_audit_seed_matches_code():
    from pqscan.bench import frame_audit
    assert frame_audit.SEED == "20261113:frame" and "`20261113:frame|<repository>|<file>`" in PROTO


def test_f11_packet_first_rule_matches_code():
    from pqscan.bench import packets
    assert packets.PLANNED_CANDIDATES == {"DV": 468, "T": 630}
    assert round(packets.packet_first_rate("DV"), 4) == 0.1282 and packets.packet_first_rate("T") == 0.10
    assert "max(0.10, 60 / N_planned)" in PROTO and "12.8% for DV" in GUIDE


def test_f13_dictionary_has_no_two_annotator_fields():
    assert "annotator_1" not in DICT and "annotator_2" not in DICT and "labels/<annotator>" not in DICT
    assert "Coverage = (RECOMMEND) / n_exec" in DICT


def test_f15_guide_examples_carry_label_kind_and_schema_keys():
    import json as _json
    schema = _json.loads((ROOT / "docs/benchmark/meta_schema.json").read_text(encoding="utf-8"))
    sec5 = GUIDE[GUIDE.index("## 5. Record envelope"):GUIDE.index("**Type rules:**")]
    blocks = re.findall(r"```json\n(.*?)```", sec5, re.S)
    assert len(blocks) == 2
    for block, kind in zip(blocks, ("primary", "ai_review")):
        meta = block[block.index('"meta"'):]
        keys = set(re.findall(r'"([a-z_0-9]+)":', meta)) - {"meta", "ai", "interface_or_api", "model", "datetime_utc",
                                                            "prompt_sha256", "packet_sha256", "status"}
        assert f'"label_kind": "{kind}"' in meta
        assert set(schema["required"]) <= keys <= set(schema["properties"])


def test_frozen_hypotheses_preserved_verbatim():
    old = (ROOT / "docs/specification/evaluation_protocol_v1.0.3.md").read_text(encoding="utf-8")
    assert FROZEN_H2 in old and FROZEN_H2 in PROTO
    for h in ("H1a: ≥ 25% of eligible real sites require evidence beyond the method/algorithm name.",
              "H3: at coverage ≥ 70%, the harmful rate of the τ = T2 policy is lower than",
              "H4: at least one operator (predicted: `loaded-key`, `cross-function`) flips ≥ 30% of base cases"):
        assert h in old and h in PROTO


@pytest.mark.parametrize("name", list(ADOPTED))
def test_h2_supported_never_used_as_a_claim(name):
    for line in ADOPTED[name].splitlines():
        if "H2 supported" in line:
            assert re.search(r"never|not used|withdrawn", line, re.I), f"{name}: {line}"


def test_h2a_h2b_defined_and_separate():
    for doc in (PROTO, PLAN):
        assert "H2a" in doc and "H2b" in doc
    assert "two separate statements" in DEC or "two statements are always reported separately" in PROTO.lower()
    assert "exploratory" in PROTO and "not under family-wise error control" in PROTO


def test_design_mixture_estimand_recorded():
    assert "design mixture" in PROTO and "design mixture" in PLAN and "design mixture" in DEC
    assert "stratified simple random sample" in PROTO


def test_k_e_rules_present():
    for doc in (PROTO, PLAN):
        assert "K_e" in doc
    assert "| 0 | not assessable | not assessable | **does not exist** | undefined |" in PLAN
    assert "not assessable as pre-registered" in PLAN and "not assessable for the original seven-repository estimand" in PLAN
    assert "A. K_e = 0" in DEC and "B. 1 ≤ K_e ≤ 6" in DEC


def test_guard_definition_and_h2b_guard():
    assert "g < 1/10" in PLAN and "g = 1/10 exactly" in PLAN
    assert "for the direction tests (before Holm) **and** for the H2b margin criterion" in PLAN
    assert "also applies to the H2b margin criterion" in PROTO


def test_constants_agree():
    for doc in (PROTO, PLAN):
        assert "B = 10,000" in doc and "20261113" in doc and "B = 100,000" in doc
        assert "k_r ≥ 5" in doc and "1/5" in doc and "0.025" in doc
    assert "m = 3" in PROTO and "m = 3" in PLAN and "m = 3" in DEC


def test_fa_assumptions_and_reporting():
    for doc in (PROTO, PLAN):
        assert re.search(r"both[- ]ran", doc) and "S-F1" in doc and "S-F2" in doc
        assert "repository-balanced" in doc and "site-weighted" in doc
    assert "D. F-A" in DEC


def test_two_stratum_calibration_and_fallback():
    assert "Two-stratum calibration (mandatory)" in PLAN
    assert "repository-by-stratum bootstrap" in PLAN and "repository-by-stratum bootstrap" in PROTO


def test_guide_envelope_and_scope_rule():
    assert '"context_used": "packet_sufficient | extended"' in GUIDE
    assert "`vendored`: a directory `vendor`, `_vendor` or `third_party`" in GUIDE
    assert "conftest.py" in GUIDE and "conftest.py" in PROTO


def test_adoption_record_hashes_match():
    r = subprocess.run([sys.executable, str(ROOT / "scripts/adoption_record.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
