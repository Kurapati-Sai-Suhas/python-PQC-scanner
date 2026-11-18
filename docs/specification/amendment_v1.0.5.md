# Amendment record: protocol v1.0.4 → v1.0.5 (18 Nov 2026)

**Basis.** Owner approval, on 18 Nov 2026, of the pre-F1 decision register `docs/audit/owner_decision_register_v1.0.5.md`, which resolves the 21 findings of the isolated AI specification review of v1.0.4 (verification: `docs/audit/chatgpt_review_finding_verification.md`). Adopted **before any labelling and before any test-split access**.

**Superseded texts.** Kept byte-for-byte in `docs/specification/archive/v1.0.4/`; `scripts/adoption_record.py --check` verifies them against the unchanged `adoption_record_v1.0.4.json`. The new hashes are in `adoption_record_v1.0.5.json`.

**Not changed:** the wording of RQ1–RQ4 and H1–H4; every threshold (25%, 10%, 30%, 90%; 70/80/90% coverage points); the primary metrics and frozen scoring rules; the confirmatory families F-A and F-B and their tests; the baseline set; D7 and D15; τ = T2; the sampling unit, the candidate pool and the seeded orders (V6); the recommendation policy (text and YAML); the benchmark and meta schemas; the AI-review prompt template and the packet rule.

| Finding | Kind | Document and place | Change |
|---|---|---|---|
| F01 | correction | `role_taxonomy.md` v1.1 Sec. 1 | Eligible kinds are (a), (b) **or (c)**, matching the policy, guide, schema and scoring table |
| F02 | correction | guide v1.2 Step D | Consumer inheritance as in taxonomy rule 1 (private/public key) |
| F03 | new rule | guide v1.2 Step A; taxonomy rule 7 | Multi-call candidate statement rule; sampling unit unchanged |
| F04 | correction + clarification | plan v1.0.1 Sec. 2, 3, 6 | Weight denominator m_r; what the primary C_r estimate and S-F1 each describe; failures by stratum |
| F05 | added check | plan v1.0.1 Sec. 9 (assumption 3), Sec. 11.6; protocol Sec. 5.4 | F-A Type I error simulation; PASS |
| F06 | disclosure | protocol v1.0.5 Sec. 6, threats | Test-output blinding is a self-attestation, not independently enforced |
| F07 | new rule | guide v1.2 Sec. 6; protocol Sec. 3 | Forbidden-content gate before the AI review |
| F08 | stricter rule + limitation | guide v1.2 Step F; protocol threats | Hybrid needs a matching PQ family and actual combination; SLH-DSA prefix limitation |
| F09 | interpretation note | `scoring_policy.md` v1.0.1 Sec. 6 | What a primary CORRECT means; no rule changed |
| F10 | documentation | guide v1.2 Sec. 2 | Unresolved-field convention (already enforced by the meta schema) |
| F11 | documentation | protocol v1.0.5 Sec. 3; guide v1.2 Sec. 5 | Packet-first rule as implemented; ≥ 50 is an expected count |
| F12 | owner decision | `run_specification_pre_f1.{md,json}` (H-4) | H1b set |
| F13 | correction | `data_dictionary.md` v1.1 | Single-investigator records; n_exec denominators |
| F14 | added prerequisite | protocol v1.0.5 Stage F1 item 9 | External human review: mandatory, pending, not waived |
| F15 | correction | guide v1.2 Sec. 5 | Owner and AI example records with `label_kind` |
| F16 | packet + interpretation | review packet; run specification H-1 to H-6; protocol Sec. 5.2 | v1.0.3 in the packet; H1/H3/H4 interpretations recorded |
| F17 | wording | plan v1.0.1 Sec. 7.5, 8 | Bounds per comparison, not multiplicity-adjusted |
| F18 | documentation + code fix | protocol v1.0.5 Sec. 2; `pqscan/bench/frame_audit.py` | Seed, order and stopping rule stated; the stopping rule now requires every repository of the frame |
| F19 | definition | plan v1.0.1 Sec. 10 | c_DV defined |
| F20 | clarification | plan v1.0.1 Sec. 11.4; protocol Sec. 5.3 | F1 never after a failed calibration |
| F21 | correction | guide v1.2 Step D; taxonomy v1.1 | Escape takes precedence over KEY_MATERIAL_ONLY |
| Pilot exposure | owner decision | guide v1.2 Sec. 7; `pqscan/bench/loops.py` | Five guide-example pilot sites reported separately |

**Versions after this amendment:** protocol v1.0.5; annotation guide v1.2; analysis plan v1.0.1; role taxonomy v1.1; data dictionary v1.1; scoring policy v1.0.1; run specification (pre-F1).
