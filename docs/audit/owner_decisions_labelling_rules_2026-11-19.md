# Owner decisions TA06, TA07, TA11, TA19: labelling rules (19 Nov 2026; revision v1.0.5-r5)

**Trigger:** the third AI review, Package A (`docs/review/spec_review_v1.0.5-r3/review_outputs/package_A_specification_review.md`), findings TA06, TA07, TA11, TA19 (major or minor).

**Timing:** decided **before any annotation**. No ledger exists and no label has been written, so every future label follows one rule.

**Owner approval (19 Nov 2026):** given in writing after the assistant showed the conflicting passages, the scanner behaviour and the consequences, including the TA07 rule-9 amendment and the regeneration of 5 demonstration outputs.

| ID | Decision (owner's words, condensed) | Implemented in |
|---|---|---|
| TA06 | Limit PROTOCOL_CONFIG examples to protocol objects of supported libraries; keep the role reserved until Module C supports it; `ssl.SSLContext` and similar calls are not eligible supported-library sites; disclose that Module C does not emit the role | Taxonomy role row; guide Sec. 4 row |
| TA07 | Assign SIGN or VERIFY only when the public/private status is established. An escaped signature-family key of unknown status is UNKNOWN and abstains, with `possible_roles` limited to SIGN, VERIFY, KEY_MATERIAL_ONLY. X25519/X448/DH → KEY_ESTABLISHMENT. Amend rule 9. Apply consistently in all four ablation arms. Never infer SIGN because the status is unknown. A conservative evidence requirement, not a demonstrated accuracy improvement | Taxonomy rules 9 (exception) and 10; guide Step D; `pqscan/roles/classifier.py` (`_direction_unknown`, both branches, all arms) |
| TA11 | `.encrypt(m)` is the operation site; `PKCS1_OAEP.new(key)` is a constructor, not a site; receiver typing and provenance follow the cipher object built from the key. Keep the existing scanner behaviour (verified). Add examples and tests | Guide Steps A and C (positive and negative examples); scanner unchanged |
| TA19 | `hybrid_component = true` only for KEY_ESTABLISHMENT, SIGN, VERIFY; schema validation rejects other combinations; no change to hybrid detection or combination requirements | Taxonomy rule 5; guide Step F; benchmark schema v1.2 (conditional rule); recommendation policy text (NO_ACTION_HYBRID row); AI-review prompt field line |

## Consequences (verified)

| Area | Effect |
|---|---|
| Existing labels | **None.** The pilot has 4 UNKNOWN labels (all RSA), 1 hybrid (KEY_ESTABLISHMENT) and 0 PROTOCOL_CONFIG. Dataset A has no single-purpose UNKNOWN and no hybrid. Both files are byte-identical to commit 1cdc2d7 (test) |
| Sampling, hypotheses, thresholds, estimands, statistical methods | **None** |
| Scanner outputs | Only escaped signature-family keys of unknown public/private status change. In the PyCryptodome 4.4.0 demonstration, exactly 5 findings change, from SIGN/T2/RECOMMEND to UNKNOWN/T1/ABSTAIN: `test_import_DSA.py` lines 368, 370, 383; `test_import_passphrase.py` line 175; `test_dss.py` line 1200 (all `DSA.import_key`). Every other finding is byte-identical, as are the cryptography outputs and the 7 demonstration outputs. Two of the five (`test_dss.py:1200`, `test_import_passphrase.py:175`) load public keys, so SIGN had the wrong direction there; the guidance class (SIG) was the same |
| Coverage effect (transparent) | PyCryptodome demonstration: RECOMMEND 210 → 205 (−5), ABSTAIN 573 → 578 (+5), SIG 124 → 119. A stricter evidence requirement; **no claim of improved accuracy** |
| AI-review prompt | Guide Secs. 3–4 are included verbatim, so the prompt content changes; its hash is recorded at F1 (item 9a) |

## Traceability

- **Archived pre-change texts:**
  - `docs/specification/archive/v1.0.5-r4/`: taxonomy, guide, recommendation policy, schema, classifier, AI-review prompt, and `test_owner_decisions_r3.py`;
  - copies added to `archive/v1.0.4`, `v1.0.5` and `v1.0.5-r3` where a review packet needs them; all four review packets reproduce.
- **Pre-r5 demonstration outputs:** `docs/final/demo/outputs/archive/pre-r5/`.
- **Tests:** `tests/test_labelling_rules_r5.py` (17 tests); `docs/paper/verify_evidence.py` E69.
- **Adoption record:** `docs/specification/adoption_record_v1.0.5-r5.json`.
