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
