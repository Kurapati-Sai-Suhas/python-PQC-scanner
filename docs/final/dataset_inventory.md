# Dataset inventory and sufficiency (final audit, 17 Nov 2026)

Branch `phase3-preparation`. Every figure below was computed on 17 Nov 2026 from the files named in the "Source" column. Nothing was taken from a summary document without checking the underlying file.

**Rules followed:**
- Held-out test repositories: only `benchmark/real/manifest.json` was read (permitted metadata). No test repository was fetched, cloned, opened or scanned. `.cache/repos/` holds only the development and validation checkouts.
- Development/validation (DV) tool outputs in `runs/` are reported at execution level only. Annotation guide v1.1 Sec. 2 forbids the owner, who is the sole annotator, from seeing pqscan or baseline outputs for a repository before its final labels exist. Role, algorithm and recommendation distributions on DV repositories are therefore **withheld on purpose**.
- Synthetic data (Dataset A) and real data (Dataset B) are reported separately. They are never pooled.

## 1. Inventory

### 1.1 Real-world repositories (Dataset B, 13 repositories)

Source: `benchmark/real/manifest.json` (frozen 2026-11-13; amended 2026-11-14 to add bismuth before F1). Licences are the GitHub licence metadata recorded by the mechanical qualification (`docs/benchmark/candidate_verification.json`). They have not been manually reviewed.

| Split | Repository | Pinned commit (date) | Licence | Stars | .py files | Regex candidates | pyca imports | PyCryptodome imports | In a baseline's tuning corpus |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| development | paramiko/paramiko | 0e9ccb91 (2026-10-17) | LGPL-2.1 | 9,901 | 70 | 142 | 43 | 0 | yes |
| development | mpdavis/python-jose | 018b310d (2025-05-28) | MIT | 1,757 | 38 | 41 | 17 | 1 | yes |
| development | jpadilla/pyjwt | 16231abf (2026-10-14) | MIT | 5,722 | 26 | 205 | 40 | 0 | yes |
| development | lepture/authlib | f817ad8a (2026-11-12) | BSD-3-Clause | 5,456 | 389 | 255 | 85 | 1 | yes |
| validation | latchset/jwcrypto | 99162f6b (2026-11-11) | LGPL-3.0 | 480 | 13 | 154 | 28 | 0 | no |
| validation | ronf/asyncssh | f1d1c750 (2026-11-07) | EPL-2.0 | 1,767 | 147 | 95 | 41 | 0 | no |
| test (sealed) | MatthiasValvekens/pyHanko | 0b27455d (2026-11-11) | MIT | 799 | 272 | 298 | 67 | 0 | no |
| test (sealed) | keylime/keylime | 8df08745 (2026-10-06) | Apache-2.0 | 576 | 309 | 371 | 138 | 0 | no |
| test (sealed) | mitmproxy/mitmproxy | d05d6645 (2026-11-13) | MIT | 46,879 | 584 | 76 | 30 | 0 | no |
| test (sealed) | secdev/scapy | 0e2f6ba2 (2026-11-13) | GPL-2.0 | 12,689 | 413 | 230 | 106 | 0 | no |
| test (sealed) | saltstack/salt | 390d168f (2026-11-11) | Apache-2.0 | 15,754 | 3,228 | 322 | 117 | 14 | no |
| test (sealed) | openstack/barbican | cd590f1b (2026-10-30) | Apache-2.0 | 250 | 280 | 132 | 29 | 0 | no |
| test (sealed) | hclivess/bismuth | 328a6b9d (2026-10-18) | GPL-3.0 | 177 | 207 | 55 | 3 | 34 (19 public-key) | no |

**Split verification.** The protocol (v1.0.4 Sec. 2, V15) requires 13 repositories: 4 development, 2 validation and 7 test. The manifest has exactly 4 / 2 / 7. All four development repositories are in a baseline's tuning corpus. No validation or test repository is. This matches the rule that tuning-corpus repositories are excluded from the test split.

**Open manifest conditions (recorded in the manifest itself):**
- fortra/impacket (57 PyCryptodome imports) was rejected only because its licence is NOASSERTION.
- ansible/ansible and aws/aws-encryption-sdk-python failed to clone and were not retried.

### 1.2 DV candidate frames (sampler v1.0.4 orders)

Source: `benchmark/candidates/{development,validation}/order_*.json` (format `pqscan-order/2`, protocol 1.0.4, seed 20261113). These are **candidate locations**: the over-approximated frame, not eligible sites. Eligibility exists only after owner labelling.

| Split | Repository | S1-app | S1-nonapp | S2 | Total candidates | Quota (eligible, primary set) | Non-app cap |
|---|---|---:|---:|---:|---:|---:|---:|
| development | paramiko | 204 | 206 | 165 | 575 | 25 | 8 |
| development | python-jose | 55 | 62 | 183 | 300 | 25 | 8 |
| development | pyjwt | 111 | 282 | 78 | 471 | 25 | 8 |
| development | authlib | 171 | 270 | 515 | 956 | 25 | 8 |
| validation | jwcrypto | 236 | 143 | 37 | 416 | 25 | 8 |
| validation | asyncssh | 143 | 117 | 525 | 785 | 25 | 8 |
| **DV total** | 6 repositories | **920** | **1,080** | **1,503** | **3,503** | 150 (+ 60 S2 in B0) | |

**Definitions (protocol Sec. 2):**
- S1 = files importing pyca or PyCryptodome. S1-app is scope class app; S1-nonapp is test, example or vendored.
- S2 = every other candidate.
- The pool is the union of the regex over-approximation, every baseline's findings and pqscan Module A, deduplicated by enclosing statement.
- Test-split candidate frames have not been built. They will be built only after F1.

**Labelled sites today: 0 owner-final labels in Dataset B.** `benchmark/annotation/` (git-ignored) holds no labels. `benchmark/ledger/` records no issuance.

### 1.3 Synthetic data (Dataset A)

Sources: `benchmark/synthetic/manifest.json`, `sites.jsonl` (388 records) and `validation_subset.csv`. Generator `pqscan/bench/synth.py` v1.0, seed 20261113.

| Field | Value |
|---|---|
| Purpose | Synthetic robustness and role benchmark (invariance operators, `loaded-key` evidence change) |
| Version | generator 1.0; manifest records the generator SHA-256 and per-instance file SHA-256 |
| Licence | project-generated code; the project licence is still undecided (README says none; pyproject says Apache-2.0; owner decision D6) |
| Size | 61 base cases (key 26, operation 22, negative 13) → 388 instances (kind: key 182, op 154, neg 52); 336 eligible, 52 ineligible |
| Split | by base case: synthetic-dev 31 base cases / 196 instances; synthetic-holdout 30 / 192 |
| Validation subset | 78 instances (20%, stratified by operator), locations only; **not yet labelled by the owner** (loop D2) |
| Language | Python 3 single-file idioms; only parsed, never imported or executed |
| Libraries | pyca 241, PyCryptodome 127, `unknown` 16 (negatives with no library), python-ecdsa 4 (out of scope, negatives) |
| Algorithms | RSA 169, EC 99, other 48 (PEM-loaded keys whose curve cannot be known, plus negatives), Ed25519 30, X25519 18, X448 12, Ed448 12. No finite-field DH, no DSA. |
| Ground-truth roles (by construction) | SIGN 140, NONE 52, KEY_MATERIAL_ONLY 42, KEY_ESTABLISHMENT 42, VERIFY 35, PK_DECRYPT 28, PK_ENCRYPT 28, UNKNOWN 21. PROTOCOL_CONFIG 0. |
| Roles by library | pyca has all 8 roles. PyCryptodome: SIGN 56, PK_ENCRYPT 14, PK_DECRYPT 14, KEY_MATERIAL_ONLY 14, VERIFY 14, NONE 8, UNKNOWN 7, KEY_ESTABLISHMENT 0. PyCryptodome has no ECDH API in scope, so this follows from the library. |
| Assessability | DETERMINATE 367, INDETERMINATE 21 |
| Key provenance | generated 200, parameter 66, n/a 52, loaded-PEM 48, attribute 22 |
| Evidence scope | cross-function 180, function 135, call 52, runtime-value 21 |
| Transformations | identity, alias-import, wrapper-function and class-method: 61 each; cross-function, dict-dispatch and loaded-key: 48 each |
| Code strata | all 388 are scope `app`; no test/example/vendored strata |
| PQ/T hybrids | 0 |
| Quality | Labels are by construction and depend on the generator being right. External/owner validation of the 78-instance subset has not happened. pqscan has **never been scored on Dataset A** (no result file exists). The holdout must not be scanned before F1. |

### 1.4 Pilot (development, circular)

Sources: `docs/pilot/h1_pilot_sites.csv`, `docs/pilot/pilot_manifest.json`, `docs/dev/pilot_harness/judgments.csv` (341 judgment rows = 31 sites × 11 methods).

- 31 sites from paramiko and python-jose, both development repositories; 30 of them are eligible.
- Labels were created during Phases 1–2, and Module B was debugged against these sites. All pilot figures are **circular development checks, not results** (Phase 2 report Sec. 5; README).

### 1.5 Demonstration data (not a benchmark)

| Dataset | Source | Purpose | Size | Licence |
|---|---|---|---|---|
| `docs/demo/demo_repo/` | written for the lecturer demo | synthetic demonstration fixture | 7 files, 23 sites reported | project |
| Installed `cryptography` 47.0.0 (pyca) | the project venv's `site-packages/cryptography`, `.py` files only | real-code demonstration (`docs/final/demo/`) | 77 `.py` files | Apache-2.0 OR BSD-3-Clause |
| Installed `pycryptodome` 4.4.0 | the project venv's `site-packages/Crypto`, `.py` files only | real-code demonstration (`docs/final/demo/`) | 228 `.py` files | BSD-2-Clause AND Unlicense AND MIT |

Neither installed library is one of the 13 benchmark repositories, the pilot, or any baseline's corpus. They were already installed as pqscan's own dependencies, so nothing was downloaded. pyjwt is also installed in the venv, but it is a development repository and was excluded. The demonstration is library-internal code, which is not the application code the research question targets.

### 1.6 Baseline tools

Source: `benchmark/baselines_manifest.json`; `runs/*/batch_summary.json` → `not_run`.
- **Pinned, runnable baselines:** pqcheck, pqc-audit, PostQuant, qsafe, QSA-regex and pqblocks-scan.
- **pqscan arms:** full, method+args+recv, method+args and method-only.
- **Not run:**
  - CBOMkit (sonar-cryptography), by owner decision D4 = A: it is an inventory tool and does not support PyCryptodome;
  - the Mehl ESEM 2026 scanner: its Zenodo record has results only, no source.

## 2. Sufficiency against the research question

**Research question:** "Does bounded key-provenance-aware cryptographic role inference improve the correctness of post-quantum migration recommendations at comparable coverage for Python cryptographic call sites, compared with algorithm-family and method/argument-based baselines?"

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Sufficient to show the software works? | **Yes.** | 489 production tests passed, 1 skipped (unit, end-to-end, synthetic parsing; final count at a640c15, `docs/paper/evidence/test_log_a640c15.txt`). All 60 DV tool runs completed (Sec. 1 of the metrics audit). The demo fixture and two real installed libraries were scanned in a fresh environment, and the CBOMs validated against CycloneDX 1.6. |
| 2 | Sufficient to test detection across the represented libraries? | **pyca: yes, at execution level. PyCryptodome: no, on real code.** Detection *recall* cannot be measured anywhere yet. | Six DV repositories have 254 pyca imports between them but only 2 PyCryptodome imports. Real PyCryptodome use is in the sealed test split (salt 14, bismuth 34). Synthetic has 127 PyCryptodome instances. Recall needs labelled eligible sites, and none exist. |
| 3 | Sufficient to evaluate role inference? | **Not yet.** The design is sufficient (360 planned primary-set eligible sites); the data is not. | 0 owner-final labels. Synthetic labels are by construction and not yet validated (loop D2). The pilot is circular. |
| 4 | Sufficient to evaluate key-provenance inference? | **Synthetic only, and only after D2.** No real-world provenance labels exist. | The synthetic data covers 5 provenance classes and 4 evidence scopes. `key_provenance` and `evidence_needed` are label fields to be filled during annotation. |
| 5 | Sufficient to compare recommendation correctness? | **Not yet.** The comparison (H2-1/3/4, F-A) is fully implemented and calibrated, but needs Phase T labels after F1. | Protocol Sec. 5; acceptance ACCEPTED. 0 test labels; F1 has not happened. |
| 6 | Sufficient for the statistical hypotheses? | **Calibrated in design only.** Whether the real data supports H2 depends on the feasibility gate (≥ 5 of 7 repositories feasible) and on K_e, which are unknown until Phase T. | `statistical_acceptance.md`: FWER ≤ 0.0125 and per-cell sizes within nominal + 3 MC-SE *under the planning model*. S16 (random repositories) gives 0.0415, so inference is conditional on the 7 fixed repositories. |
| 7 | What is missing? | Finite-field DH and DSA sites; PQ/T hybrids, except one paramiko idiom; cross-module (multi-file) flows; PROTOCOL_CONFIG sites (Module C never emits this role); python-ecdsa, pyOpenSSL, M2Crypto, PyNaCl and `rsa` (out of scope by design); real PyCryptodome in DV; non-application strata in Dataset A. | Sec. 1.1–1.3; `grep PROTOCOL_CONFIG pqscan/roles` finds nothing. |
| 8 | What can be claimed now? | pqscan statically detects RSA/EC/Ed/X usage in pyca and PyCryptodome. It assigns a role and evidence tier and maps roles to NIST-aligned targets or abstains. It emits schema-valid CycloneDX 1.6, SARIF and JSON, deterministically, in a fresh environment. The evaluation pipeline is implemented, differentially verified against an independent reference, and calibrated under the archived planning model. | Metrics audit; readiness report. |
| 9 | What cannot be claimed? | Any precision, recall, F1, accuracy or recommendation-correctness figure; any H1, H2 or F-A outcome; superiority over baselines; generalisation beyond the 7 test repositories; independent human validation (there is one annotator plus an AI review); PyCryptodome real-world performance; anything about Dataset A beyond its construction. | Rules 3, 6, 11 and 12 of the request; protocol Sec. 7. |

## 3. The three most consequential weaknesses

1. **No ground truth on real code yet.** There are 0 owner-final labels, and synthetic labels are unvalidated. Every correctness claim in the research question waits for annotation, which is the owner's work and is gated by V8, the specification review and the 14-day intra-rater gap. More data would not fix this; labelling the frozen frame does.
2. **Inference is conditional on 7 fixed test repositories.** The calibration is valid for those repositories (S00–S15, S17) but not for new repositories (S16: 0.0415 at a nominal 0.025). Any result must be worded as "on these seven repositories", as the protocol already requires. The one targeted mitigation is honest wording, not more repositories, because adding repositories after adoption would be a protocol change.
3. **PyCryptodome and pattern coverage gap before the test split.** PyCryptodome appears essentially only in the sealed test split (salt and bismuth). Role inference for PyCryptodome is therefore developed and validated only on synthetic idioms, so a PyCryptodome-specific failure would first appear in the test results. The proportionate response is:
   - validate the 127 synthetic PyCryptodome instances in loop D2 before F1;
   - report PyCryptodome results separately.

   No new data collection is needed for this. Finite-field DH, DSA, hybrids and PROTOCOL_CONFIG are similarly thin and must be listed as out-of-frame limitations.
