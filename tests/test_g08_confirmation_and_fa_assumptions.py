"""Owner confirmation of G08 (19 Nov 2026, third-review finding TB01) and the F-A assumptions text (finding TA02).

H4 Part 1 is exactly the eight registered F-A baselines; inclusion is by F-A membership only; the other five pqscan
arms are reported separately. The F-A assumptions printed with every result follow analysis plan Sec. 9 (v1.0.5)."""
from __future__ import annotations

import json
from pathlib import Path

from pqscan.baselines.adapters import ADAPTERS
from pqscan.baselines.simple import ARMS, H2_ARMS
from pqscan.bench import fa, h4

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "docs/specification/run_specification_pre_f1.json").read_text(encoding="utf-8"))
MD = (ROOT / "docs/specification/run_specification_pre_f1.md").read_text(encoding="utf-8")
EIGHT = ("pqcheck", "pqc-audit", "PostQuant", "qsafe", "QSA-regex", "pqblocks-scan",
         "pqscan:B1-algorithm", "pqscan:B2-method-args")
FIVE = {"pqscan:B4-full-T2", "pqscan:B1-dual", "pqscan:B3-full-noabst", "pqscan:method-args-recv-T0",
        "pqscan:method-only-T0"}


def test_part1_is_exactly_the_eight_fa_baselines_everywhere():
    inv = SPEC["interpretations"]["H-6 (H4)"]["tool_inventory_G08"]
    assert h4.PART1_BASELINES == EIGHT
    assert tuple(inv["decision_set_part1"]) == EIGHT
    assert tuple(SPEC["families"]["F-A"]["baselines"]) == EIGHT
    assert "`, `".join(EIGHT) in MD                                  # Markdown lists the same eight, in order
    assert set(EIGHT[:6]) == set(ADAPTERS)                            # six registered external tools


def test_other_five_pqscan_arms_are_reported_separately_never_in_part1():
    arms = {f"pqscan:{a}" for a in set(ARMS) | set(H2_ARMS)}
    assert len(arms) == 7
    assert set(h4.REPORTED_SEPARATELY) == FIVE == arms - set(EIGHT)
    assert FIVE.isdisjoint(h4.PART1_BASELINES)
    roles = SPEC["interpretations"]["H-6 (H4)"]["tool_inventory_G08"]["pqscan_arm_roles"]
    assert all("not in Part 1" in roles[a] or "reported separately" in roles[a] for a in FIVE)
    assert "T0 arm" in roles["pqscan:B2-method-args"] and "F-A baseline set" in roles["pqscan:B2-method-args"]


def test_inclusion_criterion_and_h1b_difference_recorded_without_changing_h1b():
    inv = SPEC["interpretations"]["H-6 (H4)"]["tool_inventory_G08"]
    assert "Membership in the registered F-A baseline set" in inv["part1_inclusion_criterion"]
    assert "Not based on evidence tier" in inv["part1_inclusion_criterion"]
    assert "H1b set is unchanged" in inv["h1b_versus_h4_sets"]
    assert "**H1b set (F12, H-4):** `pqcheck`, `pqc-audit`, `PostQuant`, `qsafe`, `QSA-regex`, `pqblocks-scan`." in MD
    assert any(d["id"] == "OD-2026-11-19-G08C" and d["by"] == "owner" for d in SPEC["decisions"])
    rec = (ROOT / "docs/audit/owner_decision_g08_confirmation_2026-11-19.md").read_text(encoding="utf-8")
    assert all(x in rec for x in EIGHT)


def test_fa_assumptions_follow_the_v105_plan():
    a = fa.ASSUMPTIONS
    assert "v1.0.5" in a and "not independent" in a and "simulated configurations only" in a
    assert "pairs are independent" not in a.replace("not independent", "")
    plan = (ROOT / "docs/specification/phase3_analysis_plan.md").read_text(encoding="utf-8")
    assert "so the sampled pairs are not independent" in plan
