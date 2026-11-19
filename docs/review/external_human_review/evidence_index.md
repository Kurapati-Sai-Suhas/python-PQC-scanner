# Evidence index for the external human review

Commit for review: `1cdc2d7` (tag or newer commit to be noted by the reviewer). Protocol revision **1.0.5-r4**, annotation guide 1.2-r3, analysis plan 1.0.1-r3, taxonomy 1.1-r3, data dictionary 1.1-r3, benchmark schema 1.1.

## A. Adopted specification documents (normative; SHA-256 from `docs/specification/adoption_record_v1.0.5-r4.json`, LF-normalised)

Check: `python scripts/adoption_record.py --check` exits 0 if every file below is unchanged.

| Document | SHA-256 |
|---|---|
| `docs/specification/evaluation_protocol.md` | `71171fe35083ca98c500a2e005a43b7c7991894e7282cccbea5afbff21fe33c1` |
| `docs/specification/phase3_analysis_plan.md` | `7c0fc7b72afef5964faf817653c79ddf48a536b42cb68e13885ea747dd93691b` |
| `docs/specification/phase3_decisions.md` | `d0f37c137b1d9b47502a3e71f8ce3881bf9efbca1d317ec231ae520f0c029b93` |
| `docs/benchmark/annotation_guide.md` | `73faebf7f6a5568de971b29eabb01c98bac5607b10edc805fc7feb5a31af0f3b` |
| `docs/specification/scoring_policy.md` | `5916efe74761fea2d437e34cad2be60df96a32c4655ae45e68fb8b211103b4df` |
| `docs/specification/data_dictionary.md` | `5759de353adb0701789c4daf9baccab8590860a03ddf597f20e88e4e14c603ff` |
| `docs/specification/role_taxonomy.md` | `59b798bbfe4dc71dc929072392dce79d805364d7f334b6ac0c89475daf840f64` |
| `docs/specification/recommendation_policy.md` | `4e89ac6cdbce6e0dc5bace2b58e3651240d09e2778f9759d11658d87b57d67ce` |
| `docs/benchmark/benchmark_schema.json` | `52b1c0f5ccad3828282aa1a56253e36fe082def6e24cef06db40c4853ae1e32b` |
| `docs/specification/evaluation_protocol_v1.0.3.md` | `0bca5103293afeef8705b03cc1e6231ecbcf9b3e7a4aabe4b2a4d257a9e3edcc` |
| `docs/benchmark/annotation_guide_v1.0.md` | `b5ee8145fd42e1c3f153df76ec4d956f0b148ddd980d3d4073b8e329c6e072cf` |
| `docs/benchmark/meta_schema.json` | `71b36e5e347386dc7bfb6eeef76e012fff0b3bb05e54784f23a1fb62b8681f58` |
| `docs/benchmark/ai_review_prompt_v1.md` | `9c7d183406019c7dae708f9b89dae3fea8dc6969bfb666a8df6865fa76570b38` |
| `pqscan/bench/packets.py` | `3aa9ea54e5b3ed44d4348179870447376145845fa0317621e8465ff249922301` |
| `docs/specification/run_specification_pre_f1.md` | `663809b9f47d73c0f0abbab15ec194ea976533e584e9fbce5d3c7ec2e3ccb263` |
| `docs/specification/run_specification_pre_f1.json` | `eee2f35f7826b1d079050f6d715d318e67d125b05a50788b0afbd3078c99eb1a` |
| `docs/specification/amendment_v1.0.5.md` | `87c8a6ebdb0230a73944d770ebd83f9d4c3a8e51c8c8d0103f29e86edbfd4904` |
| `pqscan/policy/policy_v1_1.yaml` | `907a8156d8857f9d649733371299c30a04cfe43d2a37a332ea0854a5b64e469d` |
| `pqscan/bench/h4.py` | `3438feff074decf9c934f178023ca1a4dfed41aca4f3ad1f21f2ea33a9ce618f` |

## B. Supporting evidence (read as context; not normative)

| Path | What it is |
|---|---|
| `docs/review/spec_review_v1.0.5-r3/review_outputs/third_ai_review_report.md` | Third AI review: combined report, closure matrix, open owner decisions |
| `docs/review/spec_review_v1.0.5-r3/review_outputs/package_A_specification_review.md` | Third AI review, Package A (verbatim) |
| `docs/review/spec_review_v1.0.5-r3/review_outputs/package_B_closure_audit.md` | Third AI review, Package B (verbatim) |
| `docs/audit/owner_decisions_g02_g03_g08_g10.md` | Owner decisions G02/G03/G08/G10 and the G01–G11 closure matrix |
| `docs/audit/owner_decision_g08_confirmation_2026-11-19.md` | G08 confirmation (H4 Part 1 = eight F-A baselines) |
| `docs/audit/owner_decision_register_v1.0.5.md` | First-review decisions F01–F21 |
| `docs/implementation/acceptance/statistical_acceptance.md` | Statistical calibration (planning model) |
| `docs/implementation/acceptance/fa_type1.md` | F-A Type I simulation |
| `docs/implementation/acceptance/g10_calibration.md` | G10 heterogeneous-gap calibration |
| `docs/audit/standards_verification_2026-11-19.md` | Standards status check |
| `docs/final/demo/RUN_LOG.md` | Clean-environment reproduction log |
| `pqscan/` | Implementation (tests in tests/; 742 pass, 1 skipped at the commit below) |

## C. Not to be opened by the reviewer

`benchmark/restricted/`, `docs/pilot/` (labels), `benchmark/synthetic/sites.jsonl` and `cases/` (answers), any test-split repository. The review is of the specification, not of labels or results; no results exist.
