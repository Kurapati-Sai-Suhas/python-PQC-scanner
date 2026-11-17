# Metrics, logs and implementation audit (final audit, 17 Nov 2026)

Every value was recomputed on 17 Nov 2026 from raw files: `runs/*/batch_summary.json` and `*.run.json`, tool outputs, `docs/implementation/acceptance/*.json`, `docs/demo/outputs/` and the new `docs/final/demo/outputs/`. The audit started at commit a89743a. pqscan's code is unchanged since the accepted commit aa9d6b0: `git diff aa9d6b0 HEAD -- pqscan` is empty.

**Rules applied:**
- **No human ground-truth labels exist.** So no precision, recall, F1, false-positive rate or recommendation accuracy is reported anywhere in this document. Where such a row would go, it says NOT AVAILABLE.
- **Development/validation (DV) runs are reported at execution level only.** Annotation guide v1.1 Sec. 2 forbids the owner, who is the sole annotator, from seeing tool outputs for a repository before its labels exist. Per-site, per-role, per-algorithm and per-recommendation distributions on DV repositories are therefore withheld.
- Role and recommendation distributions are reported only for non-benchmark code (the demo fixture and two installed libraries). That is detection **volume**, not accuracy.

## 1. Close-out claims reconciled with raw evidence

| Claim (`phase3_engineering_closeout.md`) | Verified value | Evidence |
|---|---|---|
| 475 production tests passed, 1 skipped | **475 + 1 skipped at a89743a.** 489 passed + 1 skipped after this audit's 14 new tests. | `pytest` runs on 17 Nov (Sec. 4) |
| 82 archived reference tests passed | **82** (rev4: 29 + 27 + 26). The folder also has 13 rev3 tests: **95 passed** in total. | `pytest docs/proposals --co` |
| Differential tests passed | pass (7 tests in the suite) | `tests/test_h2_differential.py` |
| Acceptance ACCEPTED, 85.9 min, code aa9d6b0 | ACCEPTED. pqscan unchanged since aa9d6b0. Re-aggregating the 132 cached checkpoints on 17 Nov reproduced every number byte-for-byte; only the commit and run-time fields differ, and the committed report was restored. | `statistical_acceptance.json`; `.cache/acceptance/1d58d7f3bed2b9ea/` |
| Adoption record intact | `scripts/adoption_record.py --check` exit 0 | Sec. 4 |
| Lecturer demo complete | Rebuilt in a fresh venv from `git archive`: **7/7 outputs byte-identical** to the committed ones | `docs/final/demo/RUN_LOG.md` |
| No specification review or annotation | `benchmark/annotation/` has no labels; the ledger has no issuance; no `docs/benchmark/ai_review_identity.json` | file listing |
| No F1/F2/E | no `docs/freeze/`; no `phase3-pretest-freeze` tag | `git tag`; `held_out_blocker()` returns "does not exist" |
| Test repositories not accessed | `.cache/repos/` has only development (4) and validation (2); `runs/` has only development, validation, errcheck and fetch | listing. The manifest records that bismuth was cloned on 14 Nov for repository-level counting only and then deleted, before F1. |
| `main` untouched | `main` = `origin/main` = 81f561e = `phase2-complete` | `git rev-parse` |

## 2. Metrics table

| Metric | Existing value | Evidence/file | What it tells us | Limitation | Recommended action |
|---|---:|---|---|---|---|
| **Labelled real-world accuracy** (precision, recall, F1, recommendation correctness, harmful rate) | **NOT AVAILABLE** | 0 owner-final labels | Nothing yet | All correctness claims wait for annotation | Owner: V8 identity → specification review → DV annotation → F1 → T annotation |
| Synthetic (Dataset A) scores | **NOT AVAILABLE**: pqscan has never been scored on Dataset A | no result file; holdout sealed | Nothing yet | Labels by construction; validation loop D2 not done | Score synthetic-dev after D2. Do not show tool outputs to the owner before the D2 labels. Holdout after F1. |
| DV candidate frame | 3,503 candidates in 6 repositories (S1-app 920, S1-nonapp 1,080, S2 1,503) | `benchmark/candidates/*/order_*.json` | Enough S1 candidates for every DV quota (25 eligible per repository, cap 8 non-app) | Over-approximation; eligibility unknown | None. Issue batches after V8 and the specification review. |
| DV tool runs (run1) | **60/60 completed**: development 40/40, validation 20/20; 0 timeouts | `runs/{development,validation}/run1/batch_summary.json` | All 6 baselines and 4 pqscan arms execute on every DV repository | Run on 14 Nov, before the T0 arms were wired into the analysis (0fe9d7a); must be re-run at D6 | Re-run at D6 with the frozen code |
| File-level processing in DV runs | 5,230 development + 1,600 validation file-runs = `processed`; 0 skipped or failed | same, `file_status_counts` | No parse or execution failures on real DV code for any tool | Real code may still hold rare failure modes | None |
| DV run determinism (run1 vs run2, development) | pqscan arms 16/16 byte-identical; adapter-parsed findings 24/24 identical; 12 raw files differ only in embedded timestamps or random serial UUIDs | `findings_digest` over `runs/development/run{1,2}` | Every tool is deterministic on the same input | Two runs, one machine | Keep `findings_sha256` (added for validation run1) for every run |
| Baseline failure handling | errcheck fixture (4 files: good, latin-1, null byte, syntax error): every tool's measured profile matches. pqblocks-scan fails the **whole run** on any bad file (4/4 `run-failed`). pqscan logs 2 files as execution failures and processes 2. | `runs/errcheck/real_tool_failure_check.md` | Failure handling and denominators are implemented as the protocol says | Fixture only | None. The pqblocks whole-run failure is reported as the protocol says. |
| Baselines not run | CBOMkit (owner decision D4 = A); Mehl ESEM 2026 (no source) | `batch_summary.json` → `not_run` | Two comparators are missing from every table | Fewer baselines | Report as not run (already the protocol) |
| Pilot (31 sites; development) | e.g. B4-full-T2 30/30 correct, coverage 23/30; baselines' harmful rates 0–9 of 30 | `docs/dev/pilot_harness/summary.md` | The harness works end to end | **Circular**: Module B was debugged on these sites. Not a result. | Never cite as evidence |
| H1 pilot values | H1a 51.7% (15/29); H1b 7–31% | protocol Sec. 1 | Planning information | Circular pilot | Never cite as evidence |
| **Statistical calibration** (simulation) | Type I worst 0.0061 / 0.0093 / 0.0191 (a/3, a/2, a; 17 fixed-repository scenarios); near-kink worst 0.0092 / 0.0125 / 0.0213; FWER worst 0.0125 (8 configurations); two-stratum unstratified worst 0.0025 / 0.0040 / 0.0114 | `docs/implementation/acceptance/statistical_acceptance.{md,json}` | The production procedure holds its error rates **under the archived planning model** | Assumed model; B = 1,000 in calibration against B = 10,000 in analysis; S16 (random repositories) gives 0.0415, so the result is not valid for generalisation | Report as calibration, never as accuracy |
| Lecturer demo (synthetic fixture) | 7 files, 23 sites; fresh rebuild 7/7 byte-identical; CBOM identical across runs | `docs/demo/outputs/`, `docs/final/demo/RUN_LOG.md` | Install and CLI reproducible from a clean environment | Synthetic fixture | None |
| Real-code demo: pyca `cryptography` 47.0.0 | 77 files, 0 skipped, 0 failures, Semgrep ok. 13 sites: RECOMMEND 2 (SIG), ABSTAIN 11 (role UNKNOWN 4, tier T1 < T2 4, tier T0 < T2 3). 1 excluded (symmetric receiver). | `docs/final/demo/outputs/real/` | Runs on real library code. Abstains when key provenance is not visible. | Library-internal code, not application code. **No labels: volume, not accuracy.** | Use only as a demonstration |
| Real-code demo: PyCryptodome 4.4.0 | 228 files, 0 failures. 1,214 sites: RECOMMEND 210 (SIG 124, KEM_DEM 86), FLAG_NO_TARGET 431 (INVENTORY), ABSTAIN 573 (T0 328, UNKNOWN 198, T1 47). 729 excluded (not public key 574, signer object 120, cipher object 35). 1,135 of 1,214 sites are in test-scope files; all 210 recommendations are in `Crypto/SelfTest`. | same | Handles the PyCryptodome API surface at scale, including DSA and EC-or-DSA ambiguity | Self-test code dominates. The 328 T0 abstentions are mostly symmetric-cipher `encrypt`/`decrypt` calls whose receiver is unresolved (method-implied role). | Defect W5 (readiness report): consider marking method-implied roles in the summary |
| Role → class consistency (real-code demo) | **1,227 / 1,227 sites consistent with policy v1.1**: SIGN/VERIFY → SIG; PK_ENCRYPT/PK_DECRYPT → KEM_DEM; KEY_MATERIAL_ONLY → INVENTORY; UNKNOWN → ABSTAIN. 0 RECOMMEND at T0/T1. | `real_stats.json` | The policy engine applies the role mapping and the tier gate without exception | Consistency is not correctness | None |
| Semgrep vs semantic detection | **cryptography:** 11/13 sites carry a Semgrep rule (7 of them only the generic `pqscan.common.method.candidate`); 2 semantic-only; 3 Semgrep-only matches not turned into sites. **PyCryptodome:** 1,214/1,214 carry a rule (431 generic only); 35 Semgrep-only. | `real_stats.json`; `semgrep_only` in the JSON | Module B finds sites independently, and Semgrep adds rule ids. Semgrep-only matches are listed, not dropped silently. | Overlap is not recall | Report the Semgrep-only list in the frame audit |
| Unknown/abstain volume | cryptography 11/13; PyCryptodome 573/1,214 (47%) | same | Abstention is used heavily where evidence is missing | Whether abstention is *correct* needs labels | Measured by coverage matching (H2) after annotation |
| CBOM validity | 3/3 valid: demo fixture, cryptography, PyCryptodome (strict CycloneDX 1.6). Each is byte-identical across two runs. | `validate_outputs.py` → `validation.txt` | The CBOM is standard-conformant and reproducible | Schema validity is not completeness | None |
| SARIF validity | 3/3 valid against the OASIS 2.1.0 schema (draft-04): demo fixture, cryptography, PyCryptodome | same | Usable by code-scanning tools | — | None |
| Recommendation distribution by role and tier on DV | **WITHHELD** (blinding, guide v1.1 Sec. 2) | `runs/` | — | — | Report after DV labels exist |

## 3. Statistical audit

| Component | Implementation (production) | Verification | Status |
|---|---|---|---|
| Simulator | Archived planning models (`docs/proposals/v1.0.4/rev4/scripts/calib_matching_v4.py`, `calib_v12pp.py`, `sim_family_v12pp.py`), used unchanged as data generators | Acceptance reproduces R4-13's RK column cell for cell | Assumed model: arm behaviour is postulated, not measured |
| Matching and equal coverage | `pqscan/bench/matching.py`: per repository k_r = min(R_F, R_M); the lowest tier is withdrawn first; SHA-256 tie keys; withdrawn → ABSTAIN under the frozen judge; exact tie-average point estimate; ranking-free variant; 100 seeds | `test_h2_matching.py` (19, including brute force over all tie orders); differential test on 1,000 random cases identical to the reference | Correct (software) |
| Bootstrap and random tie-breaking | `h2.bootstrap`: re-matching percentile bootstrap with fresh random tie keys per resample; B = 10,000; seed 20261113; Monte Carlo rule (B = 100,000 near the threshold); stratified fallback implemented but inactive | `test_h2_inference.py`; bootstrap distributions identical to the reference at three seeds | Correct |
| H2a / H2b | Separate statements. H2a is confirmatory (H2-1 direction); H2b is the exploratory 10-point margin. The phrase "H2 supported" is never generated (wording guard). | `test_protocol_consistency.py`, `test_reliability_reporting.py` | Correct |
| Coverage-gap guard | exact g < 1/10 → 2p, before Holm; also applied to H2b (98.75% bound) | 1,000 random guard/gate/Holm cases identical to the reference | Correct |
| Feasibility gate | k_r ≥ 5; Σk/Σn ≥ 1/5; ≥ 5 of 7 feasible | same | Correct |
| Holm | m = 3 (H2-1, H2-3, H2-4) | same; FWER acceptance | Correct |
| K and K_e | K = 7 always reported. K_e < 7 → "not assessable as pre-registered". K_e = 0 → no average and g undefined (rules A/B). | `test_h2_inference.py` edge cases | Correct |
| Two-stratum calibration | Design-mixture null; app and non-app strata with different behaviour | Acceptance part C: worst 0.0114 at a; unstratified bootstrap stays in force | Passed (under the model) |
| MC-SE criteria | Each cell ≤ nominal + 3·√(p(1−p)/n) | acceptance JSON, `failed_cells` = [] | Passed |
| Family-wise error | Production `run_family`, Holm, fixed B (Monte Carlo rule off in calibration, as in R4-13) | worst 0.0125 ≤ 0.025 + 3 MC-SE | Passed |
| Failure handling and denominators | Common evaluable set; concordance assertion; S-F1/S-F2 sensitivity; failed files never change executed-site rates | `test_h2_matching.py`, `test_bench.py`, errcheck fixture | Correct |
| F-A | One-sided exact McNemar on both-ran sites, Holm, both weightings | `test_h2_inference.py` (`mcnemar_exact_one_sided` against scipy) | Correct |

**Four levels of evidence, kept apart:**
1. **Software correctness:** established. There are 489 tests, differential agreement with an independent reference implementation, and byte-identical rebuilds.
2. **Calibration under the assumed simulation model:** established for the fixed-repository design (ACCEPTED). It says nothing about how the scanners behave on real code.
3. **Performance on annotated real-world sites:** **does not exist**, because there are 0 labels.
4. **Generalisation beyond the seven fixed test repositories:** **not supported by design.** S16 shows the procedure is not calibrated for random repositories (0.0415 at a nominal 0.025). Every report must say "on these seven repositories".

## 4. Commands run for this audit (17 Nov 2026)

```bash
.venv/Scripts/python -m pytest -o addopts="" -q                  # 485 + 1 skipped at 196399b (intermediate); final: 489 passed, 1 skipped at a640c15
.venv/Scripts/python -m pytest -o addopts="" -q docs/proposals   # 95 passed (82 rev4 + 13 rev3)
.venv/Scripts/python scripts/adoption_record.py --check          # exit 0
bash docs/final/demo/run_final_demo.sh <scratch>                 # fresh venv, demo reproduction, real-code scan
.venv/Scripts/python docs/final/demo/validate_outputs.py         # CBOM / SARIF schema validation
```

The DV execution metrics were computed by a read-only script over `batch_summary.json` and `*.run.json`, using `pqscan.bench.batch.findings_digest` for determinism. No DV finding content was printed.
