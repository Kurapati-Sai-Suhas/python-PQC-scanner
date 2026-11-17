# Technical readiness report (final audit, 17 Nov 2026)

Scope: software, scanner, PQC correctness, data pipeline and research readiness of `pqscan` on branch `phase3-preparation`. The companion documents are `dataset_inventory.md` (data) and `metrics_and_logs_audit.md` (metrics, logs and the statistical audit). The test suite passing does not mean the research project is complete. This report keeps the two apart.

## 1. Readiness verdicts

| | Area | Verdict | Evidence | Blockers / limitations |
|---|---|---|---|---|
| A | Software implementation | **READY WITH LIMITATIONS** | 489 passed + 1 skipped. Reference 95 passed. Differential agreement with the independent reference. Fresh-venv install from `git archive` works. 7/7 demo outputs byte-identical. CBOM and SARIF schema-valid. 0 execution failures on 305 real library files. | Defects W3–W7 (Sec. 3). Licence undecided (W3). PROTOCOL_CONFIG unreachable (W4). Bounded, single-repository provenance by design. |
| B | Dataset | **NOT READY** for evaluation; the frames and manifests are ready | 13 repositories frozen with the 4/2/7 split verified; DV frames of 3,503 candidates; Dataset A 388 instances | 0 owner-final labels. Synthetic labels unvalidated (D2). PyCryptodome real data only in the sealed test split. |
| C | Scanner demonstration | **READY** | `final_project_demo.md`. Fresh-environment rebuild. Synthetic fixture (23 sites) plus two real installed libraries (1,227 sites). Outputs validated and committed. | The real-code demo is library-internal code. It shows behaviour, not accuracy. |
| D | Research benchmark | **NOT READY** | Sampler, ledger, packets, AI-review records, comparison and adjudication tooling are implemented and tested | Owner actions: V8 identity → specification review → pilot and synthetic loops → DV annotation (with the 14-day intra-rater gap) → F1 → test fetch and annotation → F2 |
| E | Statistical evaluation | **READY WITH LIMITATIONS** (procedures). The evaluation itself has not run. | H2 and F-A procedures implemented. Pre-F1 acceptance ACCEPTED on the unchanged pqscan tree. | No data to analyse. Calibration is under an assumed model and holds only for fixed repositories. |
| F | Academic presentation | **READY WITH LIMITATIONS** | Problem, design, architecture, PQC mapping with NIST sources, pre-registered protocol, calibration and live demo can all be presented | No experimental results. Every slide must say so, and none may show the circular pilot as a result. |
| G | Publication / research paper | **NOT READY** | — | The RQ is unanswered: no H1, H2 or F-A results. Single annotator with AI review only (no independent human validation). Licence decision. Novelty audit not done. |

## 2. PQC correctness audit

### 2.1 Primary sources

Text was extracted from the official PDFs, read on 17 Nov 2026:
- NIST IR 8547, *Transition to Post-Quantum Cryptography Standards*, final, October 2026 (CSRC lists it as Final, 10/27/2026; doi 10.6028/NIST.IR.8547);
- FIPS 203 (ML-KEM, August 2024);
- FIPS 204 (ML-DSA, August 2024);
- SP 800-227, *Recommendations for Key-Encapsulation Mechanisms*, final, September 2025.

| Policy v1.1 claim (`pqscan/policy/policy_v1_1.yaml`) | Source and location | Verdict |
|---|---|---|
| RSA, ECDSA and EdDSA signing: deprecated after 2030, disallowed after 2035 (template SIGN cites IR 8547 Table 2) | IR 8547 Sec. 4.1.1, **Table 2**: ECDSA and RSA ≥ 112-bit and EdDSA ≥ 128-bit, "Deprecated after 2030 / Disallowed after 2035". The text says NIST will deprecate all quantum-vulnerable signature algorithms after 2030. | **Supported** for all listed strengths. The draft limited deprecation to 112-bit; the final applies it to all strengths. |
| DH/ECDH/RSA key establishment: same timeline (template KEY_ESTABLISHMENT cites Table 4) | IR 8547 Sec. 4.1.2, **Table 4**: finite-field DH and MQV, EC DH and MQV, and RSA (SP 800-56B), ≥ 112-bit, deprecated after 2030 and disallowed after 2035. Harvest-now-decrypt-later may require earlier migration. | **Supported** |
| ML-KEM-768 as the default parameter set ("NIST IR 8547 default recommendation") | IR 8547 Sec. 4.1.2, after Table 5: NIST recommends ML-KEM-768 as the default parameter set | **Supported** |
| ML-DSA-65 by default; ML-DSA-44 only with an RBG ≥ 192 bits if category 2 is needed | IR 8547 Table 3 note: ML-DSA-44 drops to category 1 if the RBG has < 192 bits. FIPS 204 Sec. 3.6.1: RBG ≥ 192 bits for ML-DSA-65, ≥ 256 for ML-DSA-87; for ML-DSA-44, should be ≥ 192 and shall be ≥ 128. | **Supported**. "ML-DSA-65 by default" is the project's own choice; NIST names no signature default. |
| DSA: "no longer specified in FIPS 186-5 and not listed in IR 8547 Table 2" | IR 8547 Table 2 lists only ECDSA, EdDSA and RSA | **Supported** (Table 2). FIPS 186-5 itself was not re-read in this audit. |
| PK encryption/decryption: redesign as KEM + KDF + AEAD; not drop-in; call shape cannot be preserved | SP 800-227 **Sec. 5.2.1** "KEM-DEM Public-Key Encryption": encapsulate to get K, then encrypt the message with a symmetric scheme under K. **Sec. 4.3**: post-processing of the shared secret key. FIPS 203 Sec. 3.3: K-PKE is *not approved* as a stand-alone public-key encryption scheme. | **Supported**. The policy cites "SP 800-227 Secs. 2.1, 5.2"; the precise sections are 5.2.1 and 4.3 (W6). "AEAD" is a sound specialisation of SP 800-227's "symmetric-key encryption scheme". |
| Shared secret used directly or via an approved KDF (cites FIPS 203 Sec. 3.3) | FIPS 203 Sec. 3.3, "Approved usage of the shared secret key": use it directly, or derive keys per SP 800-108 / SP 800-56C | **Supported** |
| PQ/T hybrid via an approved combiner (cites SP 800-227 Sec. 4.6) is an acceptable transitional design | SP 800-227 Sec. 4.6 "Multi-Algorithm KEMs and PQ/T Hybrids", Sec. 4.6.2 "Approved Key Combiners". IR 8547 Sec. 3.2: hybrids are typically temporary measures. Sec. 4.1.2: a composite can be FIPS 140-validated if one input is approved. | **Supported** |
| VERIFY: legacy use means processing already-protected data; post-2035 status is set by SP 800-131A (to be revised) | IR 8547 Sec. 4 quotes the SP 800-131A definition of legacy use ("verify a digital signature" is an example) and states that NIST will revise SP 800-131A | **Supported** |

### 2.2 Required role handling

Checked in code (`roles:` map, engine and tier gate), by tests, and on 1,227 real-code sites.

| Required behaviour | pqscan | Evidence |
|---|---|---|
| SIGN / VERIFY → ML-DSA guidance | SIG class: ML-DSA (FIPS 204), SLH-DSA optional; never ML-KEM | `tests/test_policy.py::test_signatures_never_get_ml_kem`; `test_policy_nist_alignment.py` (new); real code: SIGN→SIG 94, VERIFY→SIG 32, no other class among recommended signature sites |
| Key establishment → ML-KEM-based redesign | KEM class: "ML-KEM-based key-establishment redesign … not a symmetric exchange(peer) call" | `test_key_establishment_and_encryption_never_get_ml_dsa` |
| PK encrypt/decrypt → KEM + AEAD redesign review, not drop-in | KEM_DEM class: "not a drop-in replacement"; templates say the call shape cannot be preserved | `test_public_key_encryption_is_a_redesign_not_a_drop_in`; real code: PK_DECRYPT→KEM_DEM 59, PK_ENCRYPT→KEM_DEM 27 |
| Key material only → inventory | INVENTORY (FLAG_NO_TARGET), no target algorithm | real code: 431 KEY_MATERIAL_ONLY → INVENTORY |
| Protocol configuration → protocol review | PROTOCOL_REVIEW class exists and is mapped | **Not reachable**: Module C never emits PROTOCOL_CONFIG (W4) |
| Unknown / ambiguous → abstain | UNKNOWN → ABSTAIN with possible roles. Tier below T2 → ABSTAIN. EC-or-DSA ambiguity → ABSTAIN. | real code: 202 UNKNOWN → ABSTAIN, 382 tier-gated abstentions; 0 recommendations at T0/T1 |
| Approved hybrid → no action now | NO_ACTION_HYBRID only if the PQ component is of the matching family in the same scope | `test_hybrid_review3.py`; `test_ml_kem_nearby_does_not_excuse_a_classical_signature` |
| Wrappers, aliases, indirect calls, bounded provenance | Module B: import-alias resolution, wrapper/class-method/cross-function/dict-dispatch tracing within one repository, bounded call depth | `test_semantic_*`, `test_roles.py`; Dataset A operators (not yet scored) |

The scanner never claims that ML-KEM replaces every RSA use. It never asserts security equivalence, and it introduces no non-NIST algorithms.

## 3. Defects and weaknesses, ranked by severity

| # | Severity | Finding | Status |
|---|---|---|---|
| W1 | **High (integrity)** | `scripts/fetch_pinned.py --include-test` would fetch the sealed test repositories with no check that F1 exists. Only the flag protected the held-out split. | **Fixed** in 196399b: refuses unless `docs/freeze/pretest_freeze.json` **and** the tag `phase3-pretest-freeze` exist; 5 tests |
| W2 | Medium | `scripts/phase3_acceptance.py --help` (any argument) started a run and rewrote the committed acceptance report's provenance fields from the checkpoint cache | **Fixed** in 5d78a06: only `--quick` is accepted; report restored; 4 tests |
| W3 | Medium (owner decision D6) | The licence is inconsistent: README says "none chosen", pyproject declares Apache-2.0. setuptools also warns that `project.license` as a TOML table is deprecated. | **Open, owner decision.** Not changed: choosing a licence is the owner's call. |
| W4 | Medium (coverage) | Role PROTOCOL_CONFIG / class PROTOCOL_REVIEW exist in the taxonomy and policy, but Module C never emits PROTOCOL_CONFIG. Protocol-configuration sites (TLS/SSH algorithm lists) are not detected. | Open. Report as a limitation. Adding detection is a feature change (P2) and must be decided before F1. |
| W5 | Low | An operation with an unresolved receiver gets the method-implied role (e.g. `.encrypt()` → PK_ENCRYPT) even on symmetric objects (PyCryptodome `Cipher/*`, `fernet.py:203`). The action is always ABSTAIN at T0, so no wrong advice is given, but site counts are inflated and the displayed role can mislead. | Open (P1, presentation only). It does not affect H2: abstentions are judged as abstentions. |
| W6 | Low (citation precision) | The policy cites "SP 800-227 Secs. 2.1, 5.2". The precise sections are 5.2.1 (KEM-DEM) and 4.3 (post-processing). | Open. The policy and recommendation documents are frozen and hashed in the adoption record; record for the owner, and correct only through the documented pre-F1 correction route. |
| W7 | Low (docs) | The README status still said Phase 3 had not started and did not mention the completed Phase 3 engineering or the final audit | **Fixed** (README status updated) |
| W8 | Info | pqblocks-scan aborts its whole run on one unparsable file | Measured failure profile; handled and reported by the protocol |
| W9 | Info | DV runs were made on 14 Nov, before the T0 arms existed in the analysis | Re-run at D6, as planned |

No defect was found in role inference, the policy engine, matching, bootstrap, guard, gate, Holm, K/K_e handling or failure handling.

## 4. Data-pipeline readiness

- **Ready:**
  - frozen manifests (13 repositories, verified split);
  - sampler v1.0.4 with byte-identical order regeneration;
  - hash-chained ledger;
  - strict label validation;
  - packet builder with forbidden-content check;
  - AI-review record handling that refuses incomplete answers;
  - adjudication;
  - reliability statistics;
  - frame audit;
  - batch runner with failure profiles and a determinism digest.
- **Guards:**
  - annotation tooling refuses phase T without the freeze record;
  - `fetch_pinned.py` now refuses the test split without the freeze record and tag;
  - labels are git-ignored;
  - only hashes are versioned.
- **Not ready:** any labelled data (owner work).

## 5. What can and cannot be claimed today

- **Can:** a working, tested and reproducible static scanner. It does role-aware, abstaining, NIST-aligned migration guidance for pyca and PyCryptodome RSA/EC/Ed/X use and emits valid CBOM and SARIF. It comes with a pre-registered, differentially verified and calibrated evaluation pipeline.
- **Cannot:**
  - any accuracy or correctness figure;
  - any hypothesis outcome;
  - superiority over baselines;
  - generalisation beyond the seven fixed test repositories;
  - independent human validation.
