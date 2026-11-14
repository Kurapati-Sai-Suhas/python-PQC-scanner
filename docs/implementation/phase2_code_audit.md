# Phase 2 code audit: Modules A–G (closure state)

The module breakdown comes from the frozen documents (`system_requirements.md` NFR7 and FR1–FR9) and the master implementation prompt, Phase 2.
State as of 14 Nov 2026, Phase 2 closure. The handoff-time state is in `opus_handoff_audit.md` Sec. 9–11.

Final run: 2026-11-14T07:05:11Z; 286 collected, 285 passed, 1 skipped, 0 failed; line coverage 89%. Log: `docs/implementation/test_logs/phase2_final_pytest.log`. Source fingerprint: `docs/implementation/phase2_closure_fingerprint.json`.

| Module | Files | Status | Tests (file: count) | Coverage | Known gaps |
|---|---|---|---|---|---|
| A Semgrep | `pqscan/detect/` (28 rules) | TESTED | `test_detect_rules.py`: 10 | `runner.py` 86% | — |
| B Semantic | `pqscan/semantic/` (incl. `hybrid.py`, `branches.py`) | TESTED; hybrid logic reviewed in 4 rounds | `test_semantic_typing.py`: 26; `test_semantic_evidence.py`: 22; `test_hybrid_review3.py`: 68 | typer 92%, consumers 88%, evidence 90%, hybrid 91%, branches 97% | flow-insensitive apart from if/else and try/except alternatives; at most 2 call levels when leaving a class; DH key agreement, DH parameters and PKCS#12 not typed; hybrid check conservative (cross-module combinations missed, which gives a note, not false assurance) |
| C Roles | `pqscan/roles/classifier.py` | TESTED | `test_roles.py`: 36 | 94% | PROTOCOL_CONFIG never emitted (out-of-scope libraries) |
| D Policy | `pqscan/policy/` | TESTED | `test_policy.py`: 54 | `engine.py` 96% | — (strict scoring decided: `scoring_policy.md` v1.0) |
| E Export | `pqscan/export/` | TESTED | `test_pipeline_export.py`: 21 (1 skipped: symlink privilege) | `cbom.py` 90% | — (SARIF validated against the OASIS 2.1.0 schema) |
| F Bench | `pqscan/bench/` (incl. `fileprobe.py`) | TESTED | `test_bench.py`: 49 (pilot-table regression, execution failures, strict scoring) | — | synthetic benchmark generator not built (Phase 3) |
| G Baselines | `pqscan/baselines/`, `benchmark/baselines_manifest.json`, `scripts/fetch_pinned.py` | TESTED | `test_bench.py` (adapters, failure profiles, simple baselines) | — | CBOMkit BLOCKED (Docker); Mehl results-only; batch runner that saves logs not built (Phase 3) |
| CLI / pipeline | `pqscan/cli.py`, `pqscan/pipeline.py` | TESTED | `test_pipeline_export.py` | `pipeline.py` 75% (worker-process code not measured) | — |

Security points verified by tests:
- No import or execution of scanned code.
- Root confinement for symlinks (test skipped on this machine) and Windows junctions (passed).
- File-size limit.
- Per-file timeout recorded as an execution failure.
- Parse failures recorded as execution failures.
- No key bytes, string literals or source snippets in any export.
- Out-of-scope crypto libraries reported as `unsupported`.

Independent review: four rounds, covered in Phase 2 report Section 13.
