# One-day metrics, logs and experiment audit (18 Nov 2026)

HEAD db5b2a6.

**Sources, all re-run or re-read today:**
- `docs/audit/test_log_db5b2a6.txt` (canonical test run);
- `docs/paper/verify_evidence.py` (81 values recomputed from raw files);
- `runs/*/batch_summary.json` (execution-level fields only);
- `docs/implementation/acceptance/*`;
- the demo outputs;
- a new baseline run on the synthetic demo fixture (`docs/final/demo/baselines/side_by_side.md`).

**Ground rule.** There are no human labels, so no precision, recall, accuracy or correctness figure appears anywhere below. Development/validation (DV) tool outputs are reported at **execution level only**, because the owner must not see per-site tool outputs before labelling (guide v1.1 Sec. 2).

## 1. Canonical test summary (re-run today; `docs/audit/test_log_db5b2a6.txt`)

| Suite | Command | Result | Where each historical number came from |
|---|---|---|---|
| **Production suite (`tests/`)** | `pytest -o addopts="" -q tests` | **489 passed, 1 skipped** | Current canonical figure (since 5d78a06) |
| Production suite without the 14 tests added on 17 Nov | same, ignoring `test_fetch_guard.py`, `test_policy_nist_alignment.py`, `test_acceptance_cli.py` | **475 passed, 1 skipped** | The engineering close-out (a89743a) figure: reproduced |
| — | — | 485 passed, 1 skipped | Intermediate figure at 196399b (before the 4 acceptance-CLI tests); superseded |
| Archived reference suite, rev4 | `pytest docs/proposals/v1.0.4/rev4` | **82 passed** | The "82 reference tests" figure: reproduced |
| Archived reference suite, rev3 | `pytest docs/proposals/v1.0.4/rev3` | **13 passed** | The rev3 tests that make the folder total 95 |
| Differential tests (part of the production suite) | `pytest tests/test_h2_differential.py` | **7 passed** | Included in the 489 |
| Adoption-record hashes | `scripts/adoption_record.py --check` | exit 0 | — |

**The skipped test** is `tests/test_pipeline_export.py:118`: "symlink creation not permitted on this system" (Windows without developer mode).

**Canonical statement:** production 489 passed + 1 skipped; archived reference 82 (rev4) + 13 (rev3) = 95 passed; these are separate suites and are never added together.

## 2. Consolidated table

| Component | Actual metric | Evidence / source | Status | Limitation | Improvement |
|---|---|---|---|---|---|
| Production tests | 489 passed, 1 skipped | test log | ✅ verified | Unit and integration tests; they do not measure accuracy | — |
| Differential verification | Production matching, guard, gate, Holm and bootstrap are identical to the independent reference (1,000 + 1,000 random cases, 3 bootstrap seeds, worked example, pilot tables) | `tests/test_h2_differential.py` (7 passed) | ✅ | Both implementations were written by this project; this is agreement, not external validation | — |
| DV tool execution (14 Nov) | **60/60 runs ok**; 0 timeouts; 5,230 + 1,600 file-runs processed; 0 failed files | `runs/{development,validation}/run1/batch_summary.json` | ✅ execution only | Made before the T0 arms were wired into the analysis; must be re-run at D6 | Re-run at D6 with the frozen code |
| DV runtime (pqscan `full`) | 28.7 s for 523 files (development), 10.3 s for 160 files (validation) | same | ✅ | One machine; Semgrep start-up dominates small repositories | — |
| DV runtime (baselines) | Slowest QSA-regex: 89.2 s for 523 files; fastest pqblocks-scan: 2.1 s | same | ✅ | — | — |
| DV determinism | pqscan arms 16/16 byte-identical; adapter-parsed baseline findings 24/24 identical (run1 vs run2) | `verify_evidence.py` E55; `findings_digest` | ✅ | Two runs, one machine | Keep `findings_sha256` for all runs |
| DV per-site findings, roles, recommendations | **WITHHELD** | — | blinding | — | Report after DV labels exist |
| Error handling | Fixture with good, latin-1, null-byte and syntax-error files: every tool matches its measured failure profile. pqscan logs 2 execution failures and processes 2 files. pqblocks-scan aborts its whole run. | `runs/errcheck/real_tool_failure_check.md` | ✅ | Fixture only | — |
| Baseline run on the synthetic demo fixture (new) | 10/10 runs ok (6 baselines + 4 pqscan arms). Sites reported anything at, of the 23 fixture sites: pqcheck 18, pqc-audit 11, PostQuant 21, qsafe 11, QSA-regex 14, pqblocks-scan 9 | `docs/final/demo/baselines/side_by_side.md` | ✅ demonstration | Synthetic fixture; no labels; descriptive only | — |
| Synthetic demo fixture (pqscan) | 23 sites: RECOMMEND 20 (SIG 8, KEM 6, KEM_DEM 6), FLAG 1, ABSTAIN 2; 0 failures | `docs/demo/outputs/` | ✅ | Synthetic | — |
| Real library code (pqscan) | cryptography 47.0.0: 77 files, 13 sites, 0 failures. PyCryptodome 4.4.0: 228 files, 1,214 sites, 0 failures, 25 s. | `docs/final/demo/outputs/real/` | ✅ demonstration | Library-internal code; not application code; no labels | — |
| Policy consistency | 1,227/1,227 real-code sites: each non-abstaining site has its role's class; each abstention is UNKNOWN or tier < T2; 0 recommendations at T0/T1 | `verify_evidence.py` E52 | ✅ | Consistency, not correctness | — |
| Evidence-tier distribution (real code) | cryptography: T0 3, T1 8, T2 2. PyCryptodome: T0 328, T1 245, T2 439, T3 202 | `real_stats.json` | ✅ descriptive | The T0 mass is mostly symmetric-cipher calls on unresolved receivers (method-implied role; always abstain) | Mark method-implied roles in the summary (W5) |
| CBOM / SARIF validity | 3/3 CBOMs valid (strict CycloneDX 1.6); 3/3 SARIF valid (2.1.0) | test log, section H | ✅ | Validity is not completeness | — |
| Reproducibility | Two fresh venvs: lecturer-demo outputs 7/7 byte-identical; real-code outputs 8/8 identical; CBOM deterministic | `docs/final/demo/RUN_LOG.md`; re-checked in Phase 3 (`software_readiness.md`) | ✅ | Windows only | — |
| Candidate frames | 3,503 DV candidates; 0 duplicates; 0 structural defects | `dataset_audit_values.json` | ✅ | Candidates, not eligible sites | — |
| Coverage and feasibility reports | **None exist.** The D6 feasibility check needs DV labels. | — | ⛔ not yet possible | — | Run at D6 |
| Detection recall / precision; role accuracy; recommendation correctness; false positives and negatives | **NOT AVAILABLE** (0 labels) | — | ⛔ | — | Owner annotation → F1 → T → F2 → E |
| Statistical calibration | ACCEPTED (Sec. 3) | `statistical_acceptance.{md,json}` | ✅ under the planning model | Not accuracy | — |
| Pilot outcome table | e.g. B4-full-T2 30/30 correct | `docs/dev/pilot_harness/summary.md` | ⚠ circular | Module B was debugged on these sites | Never cite as evidence |

## 3. Statistical validation

**Inputs.**
- Production code aa9d6b0 (pqscan unchanged since: `git diff aa9d6b0 HEAD -- pqscan` is empty).
- B = 1,000, with the Monte Carlo rule off in calibration.
- Seeds `default_rng([20261113, stream, task, chunk])`.

**Reproduction.**
- The 17 Nov re-aggregation of the 132 cached checkpoints reproduced every value byte-for-byte.
- Today, `verify_evidence.py` re-parsed the generated report: worst-case values E31–E33 match.
- A full 86-minute re-run was not repeated: the code under test is unchanged, and the differential tests (re-run today) cover the same production functions.

| Check | What it establishes | Worst observed |
|---|---|---|
| Type I error, 17 fixed-repository null scenarios | Under the planning model, the guarded re-matching bootstrap rejects a true null at or below each Holm level (+ 3 MC-SE) | 0.0061 / 0.0093 / 0.0191 at α/3, α/2, α (α = 0.025) |
| 8 near-equal-coverage cells | The coverage-gap guard holds error at nominal when the two arms' natural coverage is nearly equal | 0.0092 / 0.0125 / 0.0213 |
| Family-wise error, Holm m = 3, 8 configurations | The family F-B (H2-1, H2-3, H2-4) controls the probability of any false claim | 0.0125 (≤ 0.025 + 3 MC-SE) |
| Two-stratum calibration, 3 configurations | The unstratified bootstrap stays valid when app and non-app strata behave differently (design-mixture null), so the stratified fallback is not needed | 0.0025 / 0.0040 / 0.0114 |

**What it does NOT establish:**
- **That the scanner is accurate.** The simulator generates arm behaviour from assumed parameters, not from pqscan's real outputs.
- **Generalisation.** S16 (repositories redrawn per data set) gives 0.0415 at α = 0.025. Inference is valid only for the seven fixed test repositories.
- **Power on the real data,** which depends on the real recommendation counts and correctness rates.
- **Error control at B = 10,000.** The analysis uses B = 10,000; no B-sensitivity run exists for the final guarded procedure (manuscript Sec. IX).

**Why calibration under the planning model is not accuracy evidence.** It shows that *if* the data behaved like the planning model, the test would rarely claim a difference that is not there. It says nothing about whether pqscan's recommendations are correct on real code. That requires labelled test sites and stage E.

## 4. Baseline comparison: is it fair as it stands?

**What makes the comparison fair:**
- **Pinned and comparable inputs.** All tools run on the same pinned files, under one runner, with measured failure profiles.
- **Failure handling.** Execution failures are never counted as misses.
- **Dual targets** are scored as UNDECIDED, not harmful.
- **Comparison families.** F-A compares at natural coverage and F-B coverage-matched (D7, Option A).

**What still limits it:**
- No labels, so no comparison of correctness exists yet.
- Coverage differs widely (fixture: 9–23 of 23 sites), so every F-A result must print coverage.
- CBOMkit is not run (D4 = A). The Mehl scanner is not run; its stated reason is inaccurate (D14).
- The algorithm-name variant for F-A is not yet named (D15).
- The harness's text classifier interprets free-text tool advice. It is frozen, but it is a heuristic.

## 5. Conclusion

**Valid as evidence today:**
- software correctness (tests, differential agreement);
- execution reliability and determinism;
- schema validity;
- policy consistency;
- simulation calibration of the statistics.

**Engineering or simulation checks only (not accuracy):** all of the above.

**Missing:** every accuracy-type metric and every hypothesis outcome. They need owner labels and the F1 → T → F2 → E sequence.
