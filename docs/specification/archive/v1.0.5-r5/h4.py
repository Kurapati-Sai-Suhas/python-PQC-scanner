"""H4 tool registry (owner decision G08, 19 Nov 2026; run specification H-6 `tool_inventory_G08`).

The frozen identifiers the H4 evaluation uses. Part 1 ("every baseline") is exactly the eight-member registered F-A
baseline set (owner decision G08, confirmed 19 Nov 2026 after third-review finding TB01). Inclusion is by F-A membership
only, not by evidence tier: B2-method-args is a T0 arm and is included because it is an F-A baseline. The proposed
analyser (Part 2) is the F-A system. The other five pqscan arms are reported separately and never enter Part 1. Tests tie
this module to the adapter registry, the arm list, the baseline manifest and the authoritative run-specification JSON.
"""
from __future__ import annotations

PROPOSED_ANALYSER = "pqscan:B4-full-T2"
PART1_BASELINES = ("pqcheck", "pqc-audit", "PostQuant", "qsafe", "QSA-regex", "pqblocks-scan",
                   "pqscan:B1-algorithm", "pqscan:B2-method-args")
DESCRIPTIVE_ONLY = ("pqscan:B1-dual",)
T0_COMPARATORS_SEPARATE = ("pqscan:B3-full-noabst", "pqscan:method-args-recv-T0", "pqscan:method-only-T0")
EXCLUDED = {"CBOMkit (sonar-cryptography)": "not run, owner decision D4 = A",
            "Mehl ESEM 2026 scanner": "results-only artefact; no scanner source"}
# The five pqscan arms that are not in Part 1 (reported separately; owner confirmation of G08, 19 Nov 2026).
REPORTED_SEPARATELY = (PROPOSED_ANALYSER,) + DESCRIPTIVE_ONLY + T0_COMPARATORS_SEPARATE
