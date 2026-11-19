"""H4 tool registry (owner decision G08, 19 Nov 2026; run specification H-6 `tool_inventory_G08`).

The frozen identifiers the H4 evaluation uses. Part 1 ("every baseline") is the registered F-A baseline set; the
proposed analyser (Part 2) is the F-A system. Other runnable pqscan arms are reported separately. Tests tie this module
to the adapter registry, the arm list, the baseline manifest and the authoritative run-specification JSON.
"""
from __future__ import annotations

PROPOSED_ANALYSER = "pqscan:B4-full-T2"
PART1_BASELINES = ("pqcheck", "pqc-audit", "PostQuant", "qsafe", "QSA-regex", "pqblocks-scan",
                   "pqscan:B1-algorithm", "pqscan:B2-method-args")
DESCRIPTIVE_ONLY = ("pqscan:B1-dual",)
T0_COMPARATORS_SEPARATE = ("pqscan:B3-full-noabst", "pqscan:method-args-recv-T0", "pqscan:method-only-T0")
EXCLUDED = {"CBOMkit (sonar-cryptography)": "not run, owner decision D4 = A",
            "Mehl ESEM 2026 scanner": "results-only artefact; no scanner source"}
