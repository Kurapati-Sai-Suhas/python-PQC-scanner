# Implementation tracker

Project: Post-quantum crypto scanner for Python projects. Base paper DOI 10.1145/3774748.3795653.
Status vocabulary: NOT_STARTED / IN_PROGRESS / IMPLEMENTED / TESTED / VALIDATED / BLOCKED / FAILED_VALIDATION. VALIDATED requires independent review evidence, not only passing tests. Every completed item cites an evidence path or a test run.

Last updated: 2026-11-14 (Phase 2 closed; gate PASS, see Phase 2 report Sec. 12; final test log `docs/implementation/test_logs/phase2_final_pytest.log`).

## Summary view

| Bucket | Items |
|---|---|
| Completed | Phase 1 artefacts; Modules A–G, CLI, security requirements, pinned rebuild (TESTED: 286 collected, 285 passed, 1 skipped, 89% coverage, 2026-11-14T07:05:11Z); four independent review rounds; Phase 2 gate PASS; Phase 2 report and PDF; frozen scoring policy; baseline failure handling; Phase 3 readiness checklist |
| In progress | Phase 3 preparation on branch `phase3-preparation`: done: GitHub publication, two-stage freeze design, review kit, batch runner (C5), synthetic Dataset A (B3), second PyCryptodome repository (B2), CBOMkit investigation (C3); next: first real batch-runner run on development repositories |
| Pending | annotation (B1), pre-test freeze F1, test-label freeze F2, experiments |
| Blocked | CBOMkit baseline (Docker daemon stopped); human review and human annotation (need people outside the build team) |
| Failed validation | none open (the 5 Module B failures of 13 Nov were fixed on 13 Nov) |

## Phase 1 — Research specification, pilot, data foundation (gate: CONDITIONAL PASS, 2026-11-12)

| ID | Item | Status | Evidence |
|---|---|---|---|
| 1.1 | Environment and project inventory | VALIDATED | `docs/pilot/pilot_manifest.json`; `system_requirements.md` Sec. 6 |
| 1.2a | `system_requirements.md` | IMPLEMENTED | file v1.0 |
| 1.2b | `role_taxonomy.md` v1.0 | TESTED (AI re-derivation 12/12 roles) — human review pending | `h1_pilot_analysis.md` Sec. 2 |
| 1.2c | `recommendation_policy.md` v1.1 | TESTED (AI crypto review, 11 findings incorporated) — human review pending | policy Sec. 7 |
| 1.2d | `api_coverage.md` | IMPLEMENTED (row statuses lag Module A; update pending) | file |
| 1.2e | `evaluation_protocol.md` | IMPLEMENTED (pre-registered) | file |
| 1.2f | `data_dictionary.md` | IMPLEMENTED | file |
| 1.4 | H1 pilot (31 sites, 30 eligible, 5 baselines + Mehl artefact) | TESTED | `docs/pilot/*` |
| 1.4r | Independent review of pilot labels | TESTED (AI) — human review pending | `h1_pilot_analysis.md` Sec. 2 |
| 1.5a | Benchmark schema + annotation guide | IMPLEMENTED | `docs/benchmark/benchmark_schema.json`, `annotation_guide.md` |
| 1.5b | Repository split + ground-truth process | VALIDATED (mechanical verification) | `docs/benchmark/candidate_verification.{json,md}`, `benchmark/real/manifest.json` (frozen 2026-11-13, before Module C) |
| 1.6 | Phase 1 report + PDF | VALIDATED (9 pages, 14 sections, embedded fonts, footer; re-checked 13 Nov) | `docs/reports/Phase_1_Research_and_Feasibility_Report.{md,pdf}` |

Open Phase 1 conditions: human review before Phase 3 freeze; second PyCryptodome test repository (manifest open condition 1); CBOMkit route.

## Phase 2 — System implementation

| ID | Module / requirement | Status | Evidence |
|---|---|---|---|
| A / L2 | Semgrep candidate rules (28) | TESTED | `tests/test_detect_rules.py` 10 |
| B | Semantic layer (typing, arguments, consumers, evidence) | TESTED | `test_semantic_typing.py` 26, `test_semantic_evidence.py` 22, `test_hybrid_review3.py` 68; real-code development check `docs/dev/semantic_on_pilot.csv` |
| C | Role inference + tiers + ablation arms | TESTED | `test_roles.py` 36; development check `docs/dev/roles_on_pilot.md` |
| D / L4 | Policy v1.1 + abstention | TESTED | `test_policy.py` 54 |
| E / L3 | CycloneDX 1.6 CBOM + SARIF + JSON | TESTED | `test_pipeline_export.py` 21; four real CBOMs validated |
| L1 | RSA/ECC identification end to end | TESTED | four development repositories, `docs/dev/e2e/` |
| F | Benchmark judging + statistics | TESTED | `test_bench.py` 49 incl. pilot-table regression, execution failures, strict scoring |
| G | Baselines, adapters, pinned manifest, rebuild script | TESTED; CBOMkit BLOCKED | `benchmark/baselines_manifest.json`; rebuild reproduced outputs identically |
| CLI + NFR1–NFR4 | CLI, determinism, no execution, root confinement, limits, failures | TESTED | `test_pipeline_export.py` |
| NFR8 | ≥ 80% coverage on A–E | TESTED (package 89%; every A–E file ≥ 86%) | final test log |
| R | Independent code + methodology review | VALIDATED (AI reviewers in separate contexts): round 1 FAIL, round 2 PASS WITH FIXES, round 3 FAIL, confirmation PASS WITH FIXES; every listed condition fixed and each reviewer probe a regression test; no further round after the last fixes; human review still a Phase 3 condition | Phase 2 report Sec. 13; `tests/test_hybrid_review3.py` |
| P2 | Phase 2 report + PDF | VALIDATED (PDF checked: sections, footer, fonts) | `docs/reports/Phase_2_System_Implementation_Report.{md,pdf}` |
| G2 | Phase 2 gate | PASS (2026-11-14) | Phase 2 report Sec. 12; `docs/implementation/phase2_closure_fingerprint.json` |

## Phase 3 — Experiments and validation

Readiness is tracked item by item in `docs/implementation/phase3_readiness_checklist.md` (written 2026-11-14).

| ID | Item | Status | Evidence |
|---|---|---|---|
| S1 | Scoring rules frozen (primary + strict UNSUPPORTED_DROP_IN sensitivity) | TESTED (implemented, tested, frozen before any test-split action; human review pending, checklist A4) | `docs/specification/scoring_policy.md` v1.0; `tests/test_bench.py` |
| S2 | Baseline execution-failure handling | TESTED | measured failure profiles in `benchmark/baselines_manifest.json`; `tests/fixtures/baseline_errors/`; `tests/test_bench.py` |
| V | Version control and publication | TESTED | git `main` + tag `phase2-complete` (`81f561e3`) on `Kurapati-Sai-Suhas/python-PQC-scanner`; fresh clone 285 passed / 1 skipped; `docs/implementation/github_release_record.md` |
| FZ | Two-stage freeze design (F1 pre-test, F2 test-label, E) | IMPLEMENTED (documented) | `evaluation_protocol.md` v1.0.1 Sec. 6; checklist Sec. E |
| C5 | Baseline batch runner (logs, exit status, timing, per-file status, pinned-commit check) | TESTED (stub tools; real-tool run pending) | `pqscan/bench/batch.py`; `tests/test_batch.py` 13; suite 298 passed / 1 skipped, 90% |
| B3 | Synthetic benchmark generator and Dataset A (61 base cases, 388 instances, split by base case, blind validation subset) | TESTED (external validation pending) | `pqscan/bench/synth.py`; `tests/test_synth.py` 13; `benchmark/synthetic/`; suite 311 passed / 1 skipped, 90% |
| C3 | CBOMkit execution route | BLOCKED (user decision; investigated) | `docs/implementation/cbomkit_route.md` |
| HR | Human review and annotation kit (procedures, blind pilot form, review forms, adjudication log, register) | IMPLEMENTED; no review performed | `docs/review/` |
| S3 | Code fingerprint without git | TESTED | `scripts/tree_hash.py`; Phase 2 closure fingerprint `5cbe7392…f437` (92 files) |
| H | External annotator, adjudicator, human review of taxonomy/policy/labels | BLOCKED | needs people outside the build team |
| B2 | Second PyCryptodome test repository | TESTED (mechanical qualification) | `hclivess/bismuth` @ `328a6b9d61`; `docs/benchmark/qualification_round3.md` |
| B1 | ≥ 300 double-annotated real sites | BLOCKED (annotators) | checklist B1 |
| E | Freeze record and held-out evaluation | NOT_STARTED (must not start before A–D are READY) | checklist E |

## Open decisions for the user

- C2: RESOLVED 2026-11-14 — strict scoring adopted as a pre-registered sensitivity analysis (`scoring_policy.md` Sec. 3); primary scoring unchanged.
- Who acts as the human reviewer and the external annotator.
- Git: RESOLVED 2026-11-14 — repository initialised and published (`github_release_record.md`).
- Licence for the public repository (none chosen; default all rights reserved).
- Per-repository site cap and sampling seed for the test split (needed before F1).
- Rotate the Consensus API key pasted in chat earlier.
