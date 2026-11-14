# System requirements specification (v1.0)

Project: **Post-quantum crypto scanner for Python projects** (title fixed). Base paper: Lei Zhang, "Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography Migration", ICSE-Companion '26, pp. 402–403, DOI 10.1145/3774748.3795653. The system instantiates Pillar P1 (PQC-aware detection with protocol roles and enriched inventories). P2 and P3 are out of scope except an optional single-pattern migration-validation experiment.

Frozen 12 Nov 2026 (Phase 1). Changes require a dated entry in the changelog and a tracker update.

## 1. Lecturer requirements (mandatory, L1–L4)

| ID | Requirement | Realised by |
|---|---|---|
| L1 | Identify RSA and ECC usage in Python projects | Module A + B |
| L2 | Semgrep rules for cryptographic detection | Module A (Semgrep CE, pinned 1.185.0) |
| L3 | Generate a CycloneDX CBOM | Module E (CycloneDX 1.6) |
| L4 | Suggest ML-KEM / ML-DSA migration alternatives | Module D (policy v1.0) |

## 2. Functional requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR1 | Scan a directory of Python source and emit candidate call sites for every API in `api_coverage.md` with status ≥ TESTED, including aliased imports and `from x import y as z`. | Semgrep rule tests; fixture precision/recall per row |
| FR2 | Resolve, per candidate, the receiver type (RSA/EC/X25519/… public or private key object), arguments (padding, hash, curve, key size) by constant propagation within the function, and the key provenance (Sec. 5 of `role_taxonomy.md`) by bounded def-use plus one call level. | Module B labelled tests by feature |
| FR3 | Classify the cryptographic role of each eligible site with the taxonomy v1.0 and emit an evidence tier T0–T3, supporting locations, conflicting evidence and a reason. | Confusion matrix, macro-F1 on benchmark |
| FR4 | Apply policy v1.0 to produce a target class, rationale, standards references and policy version, or an explicit abstention naming the missing evidence. | Exhaustive policy unit tests; no SIG↔KEM substitutions |
| FR5 | Export a CycloneDX 1.6 CBOM that validates against the official schema and carries per-asset role, tier, recommendation/abstention, provenance evidence and source occurrences. | Schema validation + semantic link tests |
| FR6 | Export SARIF 2.1.0 and JSON for tooling. | Round-trip tests |
| FR7 | Report unsupported libraries/patterns explicitly (`unsupported`), never silently drop them. | Negative fixtures |
| FR8 | Provide a CLI: `pqscan scan <path> [--format cbom|sarif|json] [--policy <file>] [--tier-threshold T1|T2|T3] [--include-tests]`. | Integration test on two real repos |
| FR9 | Evaluation harness: ingest benchmark, run baselines via adapters, normalise, judge, compute metrics and plots, keep raw outputs. | Reproduce pilot numbers from raw outputs |

## 3. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR1 | Deterministic output for identical input and configuration (sorted findings, stable IDs, no timestamps in the comparable payload). |
| NFR2 | Pure static analysis: never import or execute scanned code; no network access during a scan. |
| NFR3 | Per-file timeout (default 30 s) and size limit (default 2 MB); malformed files produce a recorded `EXECUTION_FAILURE`, never a crash. |
| NFR4 | File traversal confined to the supplied root (symlinks not followed); no secrets, key bytes or file contents beyond a one-line snippet (≤ 200 chars, optional) in outputs or logs. |
| NFR5 | Pinned dependencies (`uv.lock`/`requirements.txt` with hashes); Semgrep, PyCG (if used) and baseline tools pinned by version and commit. |
| NFR6 | Python ≥ 3.12; runs on Windows and Linux (CI on both if available). |
| NFR7 | Modular packages: `pqscan/detect` (A), `pqscan/semantic` (B), `pqscan/roles` (C), `pqscan/policy` (D), `pqscan/export` (E), `pqscan/bench` (F), `pqscan/baselines` (G). No monolithic script. |
| NFR8 | Type hints and docstrings on public functions; unit tests written with the implementation (TDD); ≥ 80% line coverage on A–E. |
| NFR9 | Logging with levels; no secret values logged. |

## 4. Research constraints (from the frozen direction)

- Semgrep, CBOM generation and abstention are requirements/mechanisms, **not** novelty claims.
- No LLM in the core pipeline. An LLM adjudicator is an optional, separately reported baseline arm.
- No numeric confidence; ordinal tiers only.
- Ground truth never derives from the scanner's own output.
- Held-out repositories are frozen before Module C is written and never used to repair the system.

## 5. Out of scope

Binary analysis, full application refactoring (P2), protocol verification (P3), side-channel analysis, symmetric-key and hash migration recommendations, dependency-manifest scanning as a research claim, non-Python languages.

## 6. Environment baseline (recorded 12 Nov 2026)

Windows 11 Home 10.0.26300; Python 3.12.10; venv at `.venv` with semgrep 1.185.0, cryptography 47.0.0, pycryptodome 4.4.0, cyclonedx-python-lib 11.12.0, pytest 9.1.1, scipy 1.18.0, statsmodels 0.15.0, reportlab 5.1.0, xhtml2pdf, markdown; Node v24.15.0 (PostQuant build); Docker 29.5.2 installed but daemon stopped; WSL Ubuntu 26.04 available. No git repository existed in the project folder at Phase 1 start.

## Changelog

- v1.0 (2026-11-12): initial.
