# Owner decisions: pre-F1 analysis decisions (revision v1.0.5-r6, 19 Nov 2026)

**Source:** the owner's instruction of 19 Nov 2026: "Proceed with the 13 pre-F1 recommendations as revision r6, with one important exception requiring historical verification before acceptance". The options and recommendations are in `docs/audit/pre_f1_analysis_decisions_briefing.md` (commit `aaedf96`).

All decisions were taken **before F1**. No primary label existed, and the test split was unopened. No hypothesis, threshold, test, family, sampling rule or label outcome changed.

| ID | Decision (as recommended in the briefing) | Where recorded |
|---|---|---|
| TA03 | H3 keeps the per-site harmful rate (as frozen). The always-recommend half is always printed with both coverages and the per-recommendation risk. | run spec H-5 `always_recommend_reporting_TA03`; `pqscan/bench/h3.py` |
| TA04 | H4 Part 1 uses the per-tool quantifier. "One operator for all eight" is reported descriptively. | run spec H-6 `operator_quantifier_TA04`; `pqscan/bench/h4_analysis.py` |
| TA05 | H4 Part 1 uses all pairs. Part 2 (pqscan invariance) uses the 30 synthetic-holdout base cases as primary, with all pairs also reported. | run spec H-6 `population_TA05`; `pqscan/bench/h4_analysis.py` |
| TA08 | H1a numerator: eligible primary-set test sites with `obvious_from_name = false`, UNKNOWN/INDETERMINATE included. Denominator: all eligible primary-set test sites. `evidence_needed` categories and an INDETERMINATE-excluded sensitivity are reported. | run spec H-2; `pqscan/bench/h1.py` |
| TA09 | The κ rule refers to the owner's intra-rater κ(gt_role). Owner–AI and AI repeat-run κ are reported but never decisive. | protocol (κ rule) |
| TA10 | `docs/specification/api_coverage.md` is added to the F1 item-2 hash list and the adoption record. | protocol F1 list; `scripts/f1_readiness.py`; `scripts/adoption_record.py` |
| TA17 | The Experiment E driver asserts exactly seven test repositories. `h2.py` (calibration closure) is unchanged. | run spec `pre_f1_analysis_decisions_r6`; `pqscan/bench/experiment_e.py` |
| TA22 | Unresolved-site bounding is extended to F-A and H1 as reported sensitivities. Primary results are unchanged. | protocol Sec. 5.6; `pqscan/bench/experiment_e.py` |
| TA28 | H3 bootstrap: within-repository site resampling, recomputed K_r(c), frozen SHA-256 order, mean over the 100 frozen withholding orders, percentile CI, `default_rng(20261113)`. | run spec H-5 `bootstrap_procedure_TA28`; `pqscan/bench/h3.py` |
| W6 | The SP 800-227 citation is corrected from "Secs. 2.1, 5.2" to Secs. 5.2.1 and 4.3. Template text only; no mapping change. Affected outputs are regenerated. | `pqscan/policy/policy_v1_1.yaml`; `recommendation_policy.md` |
| N1 | PyCryptodome ML-KEM, ML-DSA and hybrid modules are recorded as a disclosed scope limitation. | protocol threats |
| D14 | The Mehl exclusion reason is corrected (repository-level labels; no per-site migration recommendation). The tool stays excluded from F-A, H1b and H4. | run spec; `h4.py`; `fa.py`; `benchmark/baselines_manifest.json` |
| **TA01** | **Conditional approval:** accept the fixed-repository scope **only if** history shows S16 was outside the criterion before its result was observed. **Outcome: not established** (`docs/audit/ta01_s16_historical_verification.md`). S16 is not excluded; criterion 2 is not met; **F1 is blocked** pending a further owner decision. | run spec `pre_f1_analysis_decisions_r6.TA01_s16`; protocol changelog |

Pre-change texts are archived in `docs/specification/archive/v1.0.5-r5/`. The adoption record is `docs/specification/adoption_record_v1.0.5-r6.json`.
