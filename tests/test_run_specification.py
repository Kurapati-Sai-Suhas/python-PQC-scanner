"""The pre-F1 run specification (docs/specification/run_specification_pre_f1.json) must agree with the code it names.

Guards owner decisions D7 and D15 (18 Nov 2026): F-A has <= 8 members including exactly one algorithm-name mapping
(B1-algorithm, with the implemented ALG_RULE), B1-dual stays outside every confirmatory family, F-B is the adopted
H2-1/H2-3/H2-4 set, and nothing not-run is listed as a baseline. Changing any of these silently fails this test.
"""
import json
from pathlib import Path

from pqscan.baselines.adapters import ADAPTERS
from pqscan.baselines.simple import ALG_RULE, ARMS, H2_COMPARISONS
from pqscan.bench.fa import NOT_SCORED, SYSTEM

SPEC = json.loads((Path(__file__).resolve().parents[1] / "docs/specification/run_specification_pre_f1.json")
                  .read_text(encoding="utf-8"))
FA = SPEC["families"]["F-A"]


def test_fa_system_is_the_proposed_system():
    assert FA["system"] == SYSTEM == "pqscan:B4-full-T2"


def test_fa_members_exist_and_respect_the_protocol_limit():
    known = set(ADAPTERS) | {f"pqscan:{a}" for a in ARMS}
    assert set(FA["baselines"]) <= known
    assert len(FA["baselines"]) == len(set(FA["baselines"])) <= FA["max_members_protocol"] == 8
    assert not any(k in b.lower() for b in FA["baselines"] for k in NOT_SCORED)


def test_d15_single_algorithm_name_mapping():
    algorithm_maps = [b for b in FA["baselines"] if b.startswith("pqscan:B1")]
    assert algorithm_maps == ["pqscan:B1-algorithm"]
    assert "pqscan:B1-dual" in SPEC["descriptive_only"]
    assert FA["algorithm_name_mapping"]["mapping_as_implemented"] == ALG_RULE      # mapping unchanged
    assert FA["algorithm_name_mapping"]["unresolved_algorithm"] == "DUAL"


def test_fa_is_natural_coverage_and_fb_is_the_adopted_family():
    assert FA["coverage"].startswith("natural coverage")
    fb = SPEC["families"]["F-B"]["comparisons"]
    assert {k: tuple(v) for k, v in fb.items()} == {k: H2_COMPARISONS[k] for k in ("H2-1", "H2-3", "H2-4")}
    assert all("B1-dual" not in m for pair in fb.values() for m in pair)


def test_decisions_recorded():
    ids = {d["id"]: d for d in SPEC["decisions"]}
    assert {"D7", "D15"} <= set(ids) and all(ids[i]["by"] == "owner" for i in ("D7", "D15"))


# ------------------------------------------------------------------ owner decision register of 18 Nov 2026 (v1.0.5)
ROOT = Path(__file__).resolve().parents[1]
MD = (ROOT / "docs/specification/run_specification_pre_f1.md").read_text(encoding="utf-8")
REGISTER = ROOT / "docs/audit/owner_decision_register_v1.0.5.md"


def test_h1b_set_is_the_six_external_tools_inside_fa():
    h = SPEC["h1b"]
    assert h["set"] == ["pqcheck", "pqc-audit", "PostQuant", "qsafe", "QSA-regex", "pqblocks-scan"]
    assert set(h["set"]) <= set(FA["baselines"]) and not any(t.startswith("pqscan:") for t in h["set"])
    assert h["reported_separately"] == ["pqscan:B1-algorithm", "pqscan:B2-method-args"]
    assert {"CBOMkit (sonar-cryptography)", "Mehl ESEM 2026 scanner", "pqscan:B1-dual"} == set(h["excluded"])


def test_interpretations_recorded_and_thresholds_unchanged():
    it = SPEC["interpretations"]
    assert {"H-1", "H-2", "H-3", "H-4", "H-5 (H3)", "H-6 (H4)"} == set(it)
    assert ">= 0.25" in it["H-2"] and ">= 0.10" in it["H-2"]
    assert it["H-5 (H3)"]["coverage_points"] == ["7/10", "4/5", "9/10"]
    assert ">= 0.30" in it["H-6 (H4)"]["decision"] and ">= 0.90" in it["H-6 (H4)"]["decision"]
    assert "20261113:withhold:001 ... 20261113:withhold:100" in it["H-5 (H3)"]["random_withholding"]
    assert "NOT ASSESSABLE" in it["H-5 (H3)"]["decision_C2"] and "all seven repositories" in it["H-5 (H3)"]["estimability_C1"]
    assert "still abstains on UNKNOWN roles" in it["H-5 (H3)"]["arms"]["always_recommend"]
    assert "eligible and ineligible cases included" in it["H-6 (H4)"]["denominator_C3"]
    assert any(d["id"] == "PF-REG-2026-11-18" and d["by"] == "owner" for d in SPEC["decisions"])


def test_eligible_only_sensitivity_wording_identical_everywhere():
    s = SPEC["interpretations"]["H-6 (H4)"]["eligible_only_sensitivity"]
    assert s.startswith("Eligible-only recommendation-flip sensitivity (H4; secondary; reported separately).")
    assert "never substituted for them in the primary H4 decision" in s
    assert s in MD
    assert s in REGISTER.read_text(encoding="utf-8")
    assert s not in SPEC["interpretations"]["H-6 (H4)"]["decision"]          # never part of the decision rule
