# Evidence register for the IEEE manuscript

Created 17 Nov 2026 at commit a640c15, on branch `phase3-preparation`. Every important claim in `ieee_manuscript_draft.md` must appear here. A summary document is never the only evidence for a number.

**Verification:**
- `.venv/Scripts/python docs/paper/verify_evidence.py --write` recomputes every E-id below from raw files and fails on any mismatch. Last run: **101 values, 0 failed checks** (19 Nov 2026, on `main` after the branch consolidation: E01 now verifies the preserved baseline tags and the fast-forward; `docs/audit/branch_consolidation.md`).
- Test counts come from `evidence/test_log_a640c15.txt`.

**Evidence classes:**
- **IMPL**: implementation fact;
- **SYN**: synthetic data fact (labels by construction);
- **DEMO**: demonstration observation on unlabelled code;
- **CAL**: statistical calibration under the assumed planning model;
- **REAL**: real experimental result on labelled sites. **No REAL evidence exists.**
- **META**: dataset or repository metadata.

**Safe in manuscript:**
- **Yes**: may be stated as worded.
- **Yes (qualified)**: only with the stated qualifier.
- **No**: must not appear as evidence.

## 0. Reconciliation of the production test count

| Commit | Production suite | Explanation |
|---|---|---|
| a89743a (engineering close-out) | 475 passed, 1 skipped | close-out claim; reproduced at a640c15 by excluding the 3 test files added on 17 Nov: **475 passed, 1 skipped** |
| 196399b | 485 passed, 1 skipped | +10 tests (fetch guard 5, NIST alignment 5). This intermediate figure appeared in `dataset_inventory.md`, now corrected. |
| a640c15 | 489 passed, 1 skipped | +4 acceptance-CLI tests. Verified count for the paper package and the one-day audit (`docs/audit/test_log_db5b2a6.txt`). |
| **18 Nov, D15 run specification** | **494 passed, 1 skipped** | +5 tests in `tests/test_run_specification.py` (owner decisions D7/D15 guarded against the code). Current count. |

The skipped test is `tests/test_pipeline_export.py:118`: symlink creation is not permitted on this Windows system. The archived reference suite has **82 passed** (rev4, the close-out figure); with the 13 rev3 tests, the folder total is **95 passed**. Differential tests: **7 passed**. `scripts/adoption_record.py --check`: exit 0. Source: `evidence/test_log_a640c15.txt`.

## 1. Register

| Id | Claim | Exact value | Source file | Verification | Class | Safe in manuscript |
|---|---|---|---|---|---|---|
| T1 | Production test suite | 489 passed, 1 skipped | `evidence/test_log_a640c15.txt` | `pytest -o addopts="" -q` at a640c15 | IMPL | Yes |
| T2 | Differential agreement with an independent reference implementation | 7 tests pass; identical outputs on 1,000 random matching cases, 1,000 guard/gate/Holm cases, bootstrap distributions at 3 seeds, worked example and pilot tables | `tests/test_h2_differential.py`; reference `docs/proposals/v1.0.4/rev4/scripts/matching_ref_v4.py` | `pytest tests/test_h2_differential.py` | IMPL | Yes |
| T3 | Reference (planning) implementation tests | 82 passed (rev4) | test log | `pytest docs/proposals/v1.0.4/rev4` | IMPL | Yes (as internal verification) |
| E01 | Original `main` baseline preserved; `main` consolidated by fast-forward (owner decision, 19 Nov 2026); no F1 freeze; AI-review identity recorded by the owner and valid; no labels | baseline `81f561e` pinned by the annotated tags `pre-consolidation-main-81f561e` and `phase2-complete`; `main` contains the baseline and the approved head `9cc87d5` with no merge commits (`docs/audit/branch_consolidation.md`); no freeze tag or record; identity file committed unchanged and passing `load_identity` (values not reproduced here); 0 label files | git; file system | `verify_evidence.py` E01.* | IMPL | Yes (status statement) |
| E10 | Dataset B: 13 repositories, 4 development / 2 validation / 7 test, frozen 2026-11-13 | as stated | `benchmark/real/manifest.json` | E10.split | META | Yes |
| E10b | No test repository is in a baseline's tuning corpus | 0 of 7 | same | E10.tuning_corpus_in_test | META | Yes |
| E10c | PyCryptodome imports: 2 across the 6 DV repositories; test: salt 14, bismuth 34 | as stated | same | E10.pycryptodome_* | META | Yes (metadata only; no test-source content) |
| E11 | Quotas 30 / 25 / 25 eligible sites per repository; 360 planned primary-set eligible sites | as stated | protocol v1.0.4 Sec. 2; `pqscan/bench/candidates.py` `QUOTAS` | E11.* | IMPL | Yes ("planned", not achieved) |
| E12 | DV candidate frames: 3,503 candidate **locations** (S1-app 920, S1-nonapp 1,080, S2 1,503) in 6 orders | as stated | `benchmark/candidates/*/order_*.json` | E12.* | META | Yes (qualified: candidates, not eligible sites) |
| E13 | Dataset A: 61 base cases, 388 instances (key 182, op 154, negative 52), 336 eligible; split 31/30 base cases (196/192 instances); 78-instance validation subset; 0 hybrids | as stated | `benchmark/synthetic/{sites.jsonl,manifest.json,validation_subset.csv}` | E13.* | SYN | Yes (qualified: labels by construction, not yet validated) |
| E13b | Dataset A role distribution | SIGN 140, NONE 52, KMO 42, KEY_ESTABLISHMENT 42, VERIFY 35, PK_DECRYPT 28, PK_ENCRYPT 28, UNKNOWN 21 | same | E13.roles | SYN | Yes (qualified) |
| E14 | Pilot: 31 sites (30 eligible) from paramiko and python-jose | as stated | `docs/pilot/h1_pilot_sites.csv` | E14.* | META | Yes as a description. **Pilot outcome figures: No** (circular). |
| E20 | DV execution: 60/60 tool runs completed (40 development, 20 validation), 0 timeouts, 6,830 file-runs processed | as stated | `runs/*/run1/batch_summary.json` (git-ignored, local) | E20.* | IMPL | Yes (qualified: execution only; outputs withheld for blinding; must be re-run at D6) |
| E30 | Pre-F1 statistical acceptance: ACCEPTED; code aa9d6b0; the 9 files the calibration loads (import-traced; `scripts/calibration_closure.py`) are byte-identical at HEAD; the driver script changed after aa9d6b0 only in argument handling (5d78a06); B = 1,000 | as stated | `docs/implementation/acceptance/statistical_acceptance.{json,md}` | E30.*; re-aggregation from 132 cached checkpoints reproduced every value on 17 Nov | CAL | Yes (qualified: under the assumed planning model) |
| E31 | Type I error, worst over 17 fixed-repository scenarios: 0.0061 / 0.0093 / 0.0191 at α/3, α/2, α (α = 0.025); near-kink worst 0.0092 / 0.0125 / 0.0213 | as stated | same (generated report) | E31.* | CAL | Yes (qualified) |
| E31b | Random-repository scenario S16: 0.0415 at α = 0.025 | as stated | same | E31.S16_a | CAL | Yes. Must be stated as the reason generalisation is not claimed. |
| E32 | Family-wise error (Holm, m = 3), worst of 8 configurations: 0.0125 | as stated | same | E32 | CAL | Yes (qualified) |
| E33 | Two-stratum calibration, unstratified bootstrap worst: 0.0025 / 0.0040 / 0.0114; unstratified variant stays in force | as stated | same | E33.* | CAL | Yes (qualified) |
| E40 | Policy v1.1 role→class map and default threshold T2 | SIGN, VERIFY→SIG; KEY_ESTABLISHMENT→KEM; PK_ENCRYPT, PK_DECRYPT→KEM_DEM; KMO→INVENTORY; PROTOCOL_CONFIG→PROTOCOL_REVIEW; UNKNOWN→ABSTAIN | `pqscan/policy/policy_v1_1.yaml` | E40.*; `tests/test_policy*.py` | IMPL | Yes |
| E41 | Module C never emits PROTOCOL_CONFIG | true | `pqscan/roles/` source | E41 | IMPL | Yes. Must be stated as a limitation. |
| E42 | NIST facts used by the policy | see Sec. 2 | NIST PDFs | text extraction, 17 Nov | IMPL / standards | Yes, with exact citation |
| E50 | Lecturer-demo fixture: 23 sites (RECOMMEND 20, ABSTAIN 2, FLAG_NO_TARGET 1) | as stated | `docs/demo/outputs/02_scan.json` | E50.* | DEMO | Yes (qualified: synthetic fixture written for the demo) |
| E51 | Real-code demo, pyca cryptography 47.0.0: 77 files, 0 failures, 13 sites (RECOMMEND 2 SIG, ABSTAIN 11), 1 excluded, 3 Semgrep-only, 2 semantic-only | as stated | `docs/final/demo/outputs/real/cryptography-47.0.0_scan.json` | E51.* | DEMO | Yes (qualified: library-internal, unlabelled, volume not accuracy) |
| E51b | Real-code demo, PyCryptodome 4.4.0: 228 files, 0 failures, 1,214 sites (RECOMMEND 210: SIG 124, KEM_DEM 86; FLAG_NO_TARGET/INVENTORY 431; ABSTAIN 573), 729 excluded, 35 Semgrep-only | as stated | `.../pycryptodome-4.4.0_scan.json.gz` | E51.* | DEMO | Yes (qualified, as E51; most sites are in self-test files) |
| E52 | Policy consistency on 1,227 real-code sites: 0 non-abstaining sites with a class different from the role's class; 0 abstentions without role UNKNOWN or tier < T2; 0 recommendations at T0/T1 | as stated | same | E52.* | DEMO | Yes (qualified: consistency, not correctness) |
| E53 | Schema validity: 3 CBOMs (CycloneDX 1.6 strict) and 3 SARIF files (2.1.0) valid | 6/6 | `docs/final/demo/outputs/validation.txt` | `validate_outputs.py`; E53 | DEMO / IMPL | Yes |
| E54 | Reproducibility: two fresh venvs from `git archive`; lecturer-demo outputs 7/7 byte-identical to the committed files; real-code outputs 8/8 identical across runs; CBOM byte-identical across runs | as stated | `docs/final/demo/RUN_LOG.md`, `outputs/transcript.txt` | `run_final_demo.sh` prints IDENTICAL/DIFFERENT | IMPL | Yes |
| E55 | DV run determinism: pqscan arms 16/16 byte-identical; 24/24 parsed baseline findings identical (run1 vs run2) | as stated | `runs/development/run{1,2}` | `findings_digest` (audit, 17 Nov) | IMPL | Yes (qualified: execution level) |
| E63 | F-A Type I error simulation (pre-F1; owner decision F05): PASS. 6 single configurations (R = 20,000): max rejection rate 0.0089; 4 family configurations, 8 baselines under Holm (R = 10,000): max FWER over null baselines 0.0047; nominal 0.025 | as stated | `docs/implementation/acceptance/fa_type1.{json,md}`; `scripts/fa_type1_simulation.py` | E63.* | CAL | Yes (qualified: simulated configurations only; says nothing about scanner accuracy) |
| E64 | Multi-call candidate statements in the DV pool (F03): 8 of 3,503 candidates (all S1); source-only census, never tool attribution | as stated | `docs/audit/evidence/f03_multicall_pool.json`; `scripts/f03_multicall_census.py` | E64.* | IMPL | Yes |
| E65 | Protocol v1.0.5 adopted 18 Nov 2026 (owner-approved pre-F1 decision register), before any labelling and test-split access; v1.0.4 texts archived and hash-verified | as stated | `docs/specification/adoption_record_v1.0.5.json`; `docs/audit/owner_decision_register_v1.0.5.md` | E65.*; `scripts/adoption_record.py --check` | IMPL | Yes |
| R0 | Precision, recall, F1, accuracy, harmful rate, recommendation correctness, H1/H2/F-A outcomes, superiority over baselines | **NOT AVAILABLE** | — | 0 labels | REAL | **No: must not appear** |
| P0 | Pilot outcome table (e.g. B4 30/30 correct) | circular | `docs/dev/pilot_harness/summary.md` | — | (pilot) | **No** (Module B was debugged on these sites) |

## 2. NIST statements (E42)

Text was extracted locally from the official PDFs on 17 Nov 2026. Section and table numbers are as printed.

| Statement used | Source |
|---|---|
| RSA ≥ 112-bit, ECDSA ≥ 112-bit and EdDSA ≥ 128-bit signatures: deprecated after 2030, disallowed after 2035 | NIST IR 8547 (final, Oct 2026), Sec. 4.1.1, Table 2 |
| Finite-field DH/MQV, EC DH/MQV and RSA key establishment (≥ 112-bit): deprecated after 2030, disallowed after 2035 | IR 8547 Sec. 4.1.2, Table 4 |
| ML-KEM is the only approved PQ key-establishment scheme; NIST recommends ML-KEM-768 as the default parameter set | IR 8547 Sec. 4.1.2, after Table 5 |
| ML-DSA-44 is category 2, reduced to category 1 with an RBG < 192 bits | IR 8547 Table 3 note; FIPS 204 Sec. 3.6.1 |
| Hybrid solutions are typically temporary measures | IR 8547 Sec. 3.2 |
| A composite key-establishment scheme can be FIPS 140-validated if one input is from an approved scheme | IR 8547 Sec. 4.1.2 |
| Legacy use: processing already-protected information, e.g. verifying a signature; SP 800-131A to be revised | IR 8547 Sec. 4 |
| ML-KEM shared secret: used directly as a symmetric key, or keys derived via SP 800-108 / SP 800-56C | FIPS 203 Sec. 3.3 ("Approved usage of the shared secret key") |
| K-PKE is not approved as a stand-alone public-key encryption scheme | FIPS 203 Sec. 3.3 |
| KEM-DEM public-key encryption: encapsulate, then encrypt with a symmetric scheme keyed by K | SP 800-227 (Sep 2025) Sec. 5.2.1 |
| Post-processing of the shared secret key | SP 800-227 Sec. 4.3 |
| Multi-algorithm KEMs and PQ/T hybrids; approved key combiners | SP 800-227 Sec. 4.6, 4.6.2 |

## 3. Statements that must NOT appear in the manuscript

1. Any accuracy-type figure, or the words "outperforms", "improves" or "more correct" applied to pqscan. The RQ is unanswered.
2. "H1 / H2 / F-A supported (or rejected)".
3. Pilot outcome figures as evidence.
4. "First" or "novel" without the qualifier "to our knowledge, pending the final novelty audit".
5. "Independently validated" or "double-annotated". The design is a single annotator plus an isolated AI-assisted review.
6. "ML-KEM replaces RSA" without the redesign qualifier.
7. Demo counts presented as detection recall, or as a role distribution of real-world applications.
8. Any content from the sealed test repositories beyond `benchmark/real/manifest.json` metadata.
