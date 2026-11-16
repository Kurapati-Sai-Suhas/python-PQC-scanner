# Protocol v1.0.4 — revision 3 (PROPOSED, not adopted)

Prepared 14 Nov 2026, after revisions 1 and 2 (which are kept unchanged in the parent folder). Frozen protocol v1.0.3 and annotation guide v1.0 remain in force. Nothing here is committed, no production code changed, and no test-split repository was accessed.

| File | Content |
|---|---|
| `R3_01_statistical_methodology.md` | H2 estimands, options A and B, clustering, recommended decision rule, power, the "at equal coverage" defect |
| `R3_02_reconciliation.md` | 13 repositories, quotas, analysis sets, S2, sampler mismatches M1–M14, denominators |
| `R3_03_reliability_and_review.md` | intra-rater, owner–AI and AI repeat-run statistics; ChatGPT procedure; context packets |
| `R3_04_frame_audit.md` | descriptive frame audit |
| `R3_05_scope_classification.md` | scope rule, precedence, development/validation evidence, cap implications |
| `R3_06_workload.md` | low / expected / high owner workload (assumed) |
| `R3_07_evaluation_protocol_v1.0.4_rev3_PROPOSED.md` | full proposed protocol text |
| `R3_08_changelog_rev3.md` | revision 2 → 3 changes and corrections |
| `R3_09_annotation_guide_v1.1_rev3_PROPOSED.md` | proposed guide |
| `R3_10_owner_decisions_rev3.md` | V1–V17: audit and approval list |
| `R3_11_readiness_checklist_rev3_PROPOSED.md` | readiness checklist |
| `scripts/` | `stats_rev3.py` (methods), `test_stats_rev3.py` (13 tests), `power_rev3.py`, `power_by_n_rev3.py`, `scope_rev3.py`, `workload_rev3.py` |
| `results/` | `power_rev3.{csv,md}`, `power_by_n_rev3.md`, `scope_rev3.txt`, `workload_rev3.md` (simulated or assumed; not results) |

Reproduce from the project root:

```bash
.venv/Scripts/python -m pytest -q -o addopts="" docs/proposals/v1.0.4/rev3/scripts/test_stats_rev3.py
.venv/Scripts/python docs/proposals/v1.0.4/rev3/scripts/power_rev3.py
.venv/Scripts/python docs/proposals/v1.0.4/rev3/scripts/power_by_n_rev3.py
.venv/Scripts/python docs/proposals/v1.0.4/rev3/scripts/scope_rev3.py .
.venv/Scripts/python docs/proposals/v1.0.4/rev3/scripts/workload_rev3.py
```

The scripts import `stats_rev3` as a sibling module; Python adds a script's own folder to its import path, so the commands above work from the project root (verified 14 Nov 2026).
