# Pre-F1 correction log (18 Nov 2026)

Execution record of `pre_f1_correction_plan.md` under the owner-approved register `owner_decision_register_v1.0.5.md`. Branch `phase3-preparation`; `main` untouched.

## What was done

| Finding | Change | Evidence and tests |
|---|---|---|
| F03 | `pqscan/bench/multicall.py` (lists supported calls of a statement by name, source only); issued to-do entries carry `multi_call`; guide v1.2 Step A rule; taxonomy rule 7 pointer. Pool and orders unchanged (pinned to `d051cc1` by a test). | `scripts/f03_multicall_census.py` (reads only `order_*.json` and DV source; never `pool_sources_*`) → `docs/audit/evidence/f03_multicall_pool.json`: **8 of 3,503** pool candidates (S1-app 4, S1-nonapp 4, S2 0). `tests/test_f03_multicall.py` |
| F04 | `matching.repository_result` reports `strata_drawn` (m_r,h), `strata` (c_r,h) and `failures_by_stratum`. Plan v1.0.1 Sec. 2, 3, 6: denominator m_r; the primary C_r estimate describes commonly evaluable sites; S-F1 separately describes the sampled primary set; never claimed identical when failures exist. | Pre-change: the existing test already confirmed S-F1 = (n/m)·δ̃ under concordant failures. New: `test_failures_reported_by_stratum_and_two_estimands_kept_apart`. |
| F05 | `scripts/fa_type1_simulation.py` (imports `stats.py` read-only). Configurations placed **on** the null boundary; a first draft left three configurations up to one discordant pair inside the null, which would have understated Type I error, and was corrected before the full run. | **PASS**: single max 0.0089 (limit 0.0283, R = 20,000); family FWER max 0.0047 (limit 0.0297, R = 10,000). The test is conservative in every configuration (a power cost). `tests/test_fa_type1_simulation.py`; register E63. |
| F06, F14 | Protocol v1.0.5: self-attestation wording; external human review a mandatory, pending F1 prerequisite; threats; paper threats. | `test_protocol_consistency` (F06, F14) |
| F07 | `annotate.py` prompt gate with `--warnings-decision`; ledger note with the decision file hash; excluded candidates reported by `ai`. | `tests/test_forbidden_gate.py` (8 tests) |
| F08 | Guide v1.2 Step F; protocol threats (SLH-DSA prefix gap). The worked example `kex_mlkem.py:112` meets the stricter rule (SHA-256(K_PQ ‖ K_CL), lines 139–141 and 193–194). | consistency read |
| F09 | Scoring policy v1.0.1 interpretation note; paper metric definition. | — |
| F10 | Guide v1.2 Sec. 2. **No code needed:** `meta_schema.json` already requires `unresolved_reason` (the audit's earlier statement that it did not was wrong). | existing `test_annotation_integrity` |
| F11 | Protocol and guide state the implemented rate max(10%, 60/N). | `test_f11_packet_first_rule_matches_code` |
| F12, F16, H-1–H-6 | Run specification (JSON + Markdown): interpretations with C1–C3; H1b set; eligible-only sensitivity paragraph identical in the run specification (both forms) and the register. | `tests/test_run_specification.py` |
| F13 | Data dictionary v1.1. | `test_f13_…` |
| F15 | Guide v1.2 Sec. 5 owner and AI examples. | `test_f15_…` (keys checked against `meta_schema.json`) |
| F17, F19, F20 | Plan v1.0.1 wording; c_DV definition; F1 never after a failed calibration. | `test_f17_f19_f20_wording` |
| F18 | Protocol v1.0.5 seed/order/stop rule. **Code defect found and fixed:** `frame_audit.stop_reached` checked only repositories already visited; it now requires every repository of the frame. | `test_reliability_reporting`; `test_f18_…` |
| F01, F21 | Taxonomy v1.1; guide v1.2 Step D. | `test_f01_f21_…` |
| Pilot exposure | `loops.GUIDE_EXPOSED_PILOT`; the reference report tags and counts the subset separately. | `tests/test_pilot_exposure.py` |
| Records | v1.0.4 texts archived byte-for-byte (`docs/specification/archive/v1.0.4/`); `adoption_record_v1.0.5.json`; `scripts/adoption_record.py --check` verifies both records; `amendment_v1.0.5.md`. | `test_adoption_record_hashes_match` |
| Review packets | The first-review (v1.0.4) packet stays frozen and still reproduces (archive copies; run specification read from git at `547ce08`). Second-review package `docs/review/spec_review_v1.0.5/` (8 parts, 21 documents). | `tests/test_spec_review_packet.py` |
| Paper | Manuscript wording for v1.0.5, F04, F05, F06, F09, F12, F14; register rows E63–E65. | `verify_evidence.py` |
| E01 | Prepared as `docs/audit/pending/e01_identity_committed.patch` while the identity file was uncommitted; until then `verify_evidence.py` honestly reported 1 failure (E01.ai_identity_absent). **Update 18 Nov 2026:** with the owner's separate approval, the identity file was committed unchanged and the patch applied in commit `77f7600` (E01.ai_identity_valid and E01.ai_identity_committed). | `verify_evidence.py`: 96 values, 0 failed checks |

## Unchanged (verified)

The nine files of the E30 calibration closure (`scripts/calibration_closure.py`: all three checks pass); scanner modules (`detect`, `semantic`, `roles`, `policy`, `export`, `pipeline`, `cli`, `models`, `baselines`); `policy_v1_1.yaml`; the recommendation policy; the benchmark and meta schemas; the candidate orders; every threshold, hypothesis and family.

## Still open

- External human review (mandatory before F1; pending).
- The second isolated AI specification review (package ready; needs the owner).
- Pilot, synthetic and DV annotation; F1, F2, E (each needs approval).
