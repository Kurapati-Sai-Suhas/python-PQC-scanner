# Protocol v1.0.4 — revision 4 — PROPOSED, NOT ADOPTED

Prepared 14 Nov 2026 after revisions 1–3, which are preserved in the parent folder. Protocol v1.0.3 and annotation guide v1.0 remain in force. Nothing is committed, no production code was changed, and no test-split repository was accessed.

| File | Content |
|---|---|
| `R4_01_final_methodology_audit.md` | defects D1–D10 in revision 3; V1–V18 verdicts; overall verdict |
| `R4_02_h2_statistical_design.md` | estimand, hypotheses, categories, tests, Holm table, Type I and power summary |
| `R4_03_coverage_matching.md` | frozen coverage definition, matching rule, pairing argument, worked example |
| `R4_04_repository_inference.md` | purposive selection; claims about the 7 repositories vs. generalisation; required reporting |
| `R4_05_sampling_and_estimands.md` | primary population, analysis sets, denominators, reliability, frame audit, context |
| `R4_06_final_owner_decisions.md` | decisions requiring approval |
| `R4_07_evaluation_protocol_v1.0.4_rev4_PROPOSED.md` | protocol text |
| `R4_08_annotation_guide_v1.1_rev4_PROPOSED.md` | guide changes |
| `R4_09_changelog_rev4.md` | change log |
| `R4_10_readiness_checklist_rev4_PROPOSED.md` | readiness checklist |
| `scripts/` | `stats_v4.py`, `test_stats_v4.py` (27 tests), `sim_h2_v4.py`, `sim_fwer_v4.py`, `sim_matching_v4.py` |
| `results/` | `environment.txt`, `unit_tests.txt`, `h2_type1.csv`, `h2_power.csv`, `h2_tables.md`, `fwer.md`, `matching.md` |

**R4-03 audit (added after the owner's review of R4-03; also PROPOSED, NOT ADOPTED):**

| File | Content |
|---|---|
| `R4_03_final_matching_audit.md` | audit of V12′; verdict APPROVE WITH MODIFICATION; exact V12″ text; affected sections |
| `R4_03_coverage_matching.md` | updated R4-03 (the reviewed version is in `superseded/R4_03_coverage_matching_as_reviewed.md`) |
| `R4_03a_matching_implementation_spec.md` | matching, scoring, estimators, bootstrap, guard, gate, seeds, outputs, required tests |
| `R4_03b_worked_example.md` | 12-site example calculated by hand |
| `R4_03c_bootstrap_calibration_report.md` | calibration of the re-matching bootstrap |
| `scripts/matching_ref_v4.py` | reference implementation (not production) |
| `scripts/test_matching_ref_v4.py` | 29 unit tests |
| `scripts/worked_example_v4.py` | writes `results/scoring_table_v4.md`, `worked_example_v4.md`, `pilot_matching_v4.md` |
| `scripts/calib_matching_v4.py` | writes `results/calib_matching.md` and `calib_matching.csv`, `calib_power.csv`, `calib_ties.csv`, `calib_bcheck.csv` |
| `scripts/calib_nearkink_v4.py` | writes `results/calib_nearkink.md` and `.csv` |
| `results/unit_tests_matching.txt` | `56 passed` (27 + 29) |

## Environment (`results/environment.txt`)

Python 3.12.10, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, Windows 11.

## Reproduction (from the project root)

| Command | Runtime | Expected output |
|---|---|---|
| `.venv/Scripts/python -m pytest -q -o addopts="" docs/proposals/v1.0.4/rev4/scripts/test_stats_v4.py` | about 4 s | `27 passed` |
| `.venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/sim_h2_v4.py` | about 80 s | `wrote 96 Type I rows and 66 power rows`; deterministic CSVs (seeds 20261113 + cell index) |
| `.venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/sim_fwer_v4.py` | — | `fwer.md`, all FWER ≤ 0.025 |
| `.venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/sim_matching_v4.py` | — | `matching.md`: variance ratio 0.486; score-test rejection 0.0025; worked example |
| `.venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/sim_matching_v4.py --bootstrap` | about 3.5 min | appends `P(lower 97.5% bound > delta_true) = 0.0145` |
| `.venv/Scripts/python -m pytest -q -o addopts="" docs/proposals/v1.0.4/rev4/scripts/test_matching_ref_v4.py docs/proposals/v1.0.4/rev4/scripts/test_stats_v4.py` | about 5 s | `56 passed` |
| `.venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/worked_example_v4.py` | seconds | three markdown files; deterministic (re-run gives identical SHA-256) |
| `.venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/calib_matching_v4.py` | about 28 min (16 processes) | `calib_matching.md`; S04 percentile 0.0417 at a; S00 0.0170. `--quick` writes `*_quick` files only |
| `.venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/calib_nearkink_v4.py` | about 4.5 min | `calib_nearkink.md`; guarded worst 0.0203 at a. `--quick` writes `*_quick` files only |

**Independent cross-checks inside the tests:**
- Tango's closed-form restricted MLE against `scipy.optimize`;
- exact McNemar against `scipy.stats.binomtest`;
- t and Wilcoxon against scipy;
- Holm against `statsmodels.multipletests`;
- sign-flip against a brute-force loop.

**Limitations:** every simulation uses assumed generative models (see each script's docstring). The figures are planning estimates, not results.

**Final V12″ audit (15 Nov 2026; PROPOSED, NOT ADOPTED).** Earlier versions of the R4-03 files are in `superseded/`.

| File | Content |
|---|---|
| `R4_11_v12pp_final_audit.md` | final V12″ audit; verdict APPROVE WITH MODIFICATION; exact V12″ (final) text |
| `R4_12_execution_failure_spec.md` | execution-failure handling (common evaluable set, partition, S-F1/S-F2) |
| `R4_13_calibration_report_v12pp.md` | complete-procedure calibration: 18 + 8 scenarios, power, Holm family |
| `R4_14_metric_table.md` | primary and secondary metrics; per-repository report fields |
| `R4_15_owner_decisions_v12pp.md` | decisions replacing or amending R4-06 rows for H2 |
| `R4_16_protocol_consistency_matrix.md` | cross-document check (26 rows) |
| `scripts/test_v12pp.py` | 26 tests; with the earlier suites, `results/unit_tests_v12pp.txt`: 82 passed |
| `scripts/calib_v12pp.py` | `results/calib_v12pp.md` / `.csv` (about 35 min, 16 processes; `--quick` writes `*_quick`) |
| `scripts/sim_family_v12pp.py` | `results/family_v12pp.md` (about 14 min; `--quick`) |
| `scripts/worked_example_v12pp.py` | `results/worked_example_v12pp.md`, `results/pilot_v12pp.md` (seconds) |

**Consolidated approval package (15 Nov 2026; PROPOSED, NOT ADOPTED).** Start here.

| File | Content |
|---|---|
| `R4_17_consolidated_final_audit.md` | consolidated audit: H2a/H2b wording and the "H2 supported" rule, verified procedure, testing sequence, latest calibration, hypothesis table, verdict |
| `R4_18_final_decision_matrix.md` | **the single list of decisions to approve** (replaces the R3-10, R4-06 and R4-15 tables) |
| `R4_19_engineering_handoff.md` | production items 1–17 with inputs, outputs and acceptance tests |
| `R4_20_readiness_checklist_final.md` | final readiness checklist and the 12-step sequence to the final report |

**Pre-implementation consistency addendum (16 Nov 2026; PROPOSED, NOT ADOPTED).** `R4_21_preimplementation_consistency_audit.md`: design-mixture estimand and bootstrap, the n_r = 0 rule, separate H2a/H2b statements, F-A assumptions; R4-18 amendments; verdict READY WITH SMALL CORRECTIONS.
