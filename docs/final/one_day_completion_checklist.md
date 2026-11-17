# One-day completion checklist (17 Nov 2026)

**Status values:**
- **DONE**: done and verified today;
- **REMAINING**: can be done, but was not done today;
- **BLOCKED**: waits on a named dependency;
- **IMPOSSIBLE TODAY**: cannot be done within one day without breaking the protocol.

No adopted document, hypothesis, estimand, threshold, sampling rule or sample size was changed.

## P0: complete and demonstrate the project

| Item | Status | Evidence / reason |
|---|---|---|
| Scanner installs and runs reproducibly | **DONE** | Two fresh venvs from `git archive HEAD`; `docs/final/demo/RUN_LOG.md` |
| CLI on permitted real-world data | **DONE**, with a caveat | Installed pyca cryptography 47.0.0 and PyCryptodome 4.4.0 (non-benchmark). DV repositories were deliberately **not** used, because guide v1.1 Sec. 2 bars the owner from seeing tool output on them before labelling. |
| RSA/ECC findings and role-based recommendations explainable | **DONE** | Every finding carries evidence, role reason, tier, rationale and NIST references (`*_scan.json`); demo talking points in `final_project_demo.md` Sec. 3 |
| JSON, CycloneDX CBOM and SARIF generated and validated | **DONE** | `validate_outputs.py`: 3 CBOMs and 3 SARIF files valid; CBOM deterministic |
| Failures handled safely | **DONE** | 0 failures on 305 real files; errcheck fixture matches every tool's measured profile |
| Setup and execution instructions work in a fresh environment | **DONE** | `run_final_demo.sh` ran as committed (run 2). The PowerShell live commands were re-run and match the recording exactly. |
| Demo outputs and logs reproducible | **DONE** | Lecturer demo 7/7 identical; real-code outputs 8/8 identical across two runs |
| README and architecture docs accurate | **DONE** | README status updated (W7); `docs/demo/architecture.md` unchanged and still accurate (scanner code unchanged since `phase2-complete`) |
| Dataset inventory and limitations | **DONE** | `dataset_inventory.md` |
| Final status report | **DONE** | `technical_readiness_report.md`, `metrics_and_logs_audit.md` |

## P1: high-impact quality improvements

| Item | Status | Evidence / reason |
|---|---|---|
| Fix actual correctness or integrity defects | **DONE** | W1: test-split fetch guard (196399b, 5 tests). W2: acceptance-script argument guard (5d78a06, 4 tests). |
| Regression tests pinning the NIST-verified policy facts | **DONE** | `tests/test_policy_nist_alignment.py` (5) |
| Correct misleading descriptions | **DONE** | README status. Close-out claims reconciled (`metrics_and_logs_audit.md` Sec. 1). |
| W5: show method-implied roles as such in the summary | **REMAINING** (optional) | Display only; actions are already ABSTAIN. Would change the recorded demo outputs, so it was deferred. |
| W6: policy citation precision (SP 800-227 Secs. 5.2.1, 4.3) | **BLOCKED** (owner) | The policy and recommendation documents are frozen and hashed; correct only through the pre-F1 correction route, with the owner's approval |
| W3: licence (README "none" vs pyproject Apache-2.0) | **BLOCKED** (owner decision D6) | The licence choice belongs to the owner |
| Score pqscan on synthetic-dev (Dataset A) | **BLOCKED** (D2) | Do it after the owner's blind validation of the 78-instance subset, so tool outputs cannot influence it. The holdout waits for F1. |

## P2: further research improvements (not started, by design)

| Item | Status | Reason |
|---|---|---|
| PROTOCOL_CONFIG detection (W4) | REMAINING | Feature change; must be decided before F1 |
| More libraries (pyOpenSSL, PyNaCl, python-ecdsa, M2Crypto, `rsa`) or patterns (finite-field DH, cross-module flows) | REMAINING | Outside the adopted frame; would need a protocol change |
| More repositories | not recommended | It would change the adopted frame and does not fix the binding weakness, which is the missing labels |
| External human validation | REMAINING | Needs a second annotator. The protocol has one annotator plus an AI review. |

## Research workflow (owner-gated, cannot be done by Claude)

| Step | Status | Dependency |
|---|---|---|
| Record `docs/benchmark/ai_review_identity.json` (V8) | **BLOCKED (owner)** | Must reflect the real interface, displayed model, timestamp and isolation settings. Claude must not create it. |
| Isolated ChatGPT specification review of v1.0.4 / v1.1 | **BLOCKED (owner)** | V8, then the owner's instruction. It cannot be replaced by a Claude review. |
| Pilot (31) and synthetic (78) validation loops (D2) | **BLOCKED** | Specification review |
| Phase DV annotation, frame audit, reliability | **BLOCKED** | Above. The intra-rater re-label needs ≥ 14 days after the latest primary label. |
| DV pipeline re-run and feasibility check (D6) | **BLOCKED** | DV labels |
| F1 freeze, test fetch, Phase T annotation, F2, E | **IMPOSSIBLE TODAY** | Each needs explicit owner approval and its freeze conditions. The 14-day gap alone exceeds one day. |
| Any accuracy, precision, recall, F1 or hypothesis result | **IMPOSSIBLE TODAY** | No labels exist, and they must not be fabricated |

## Commits made today (`phase3-preparation`)

| Commit | Content |
|---|---|
| 196399b | Test-split fetch guard; NIST-alignment policy tests |
| 5d78a06 | Acceptance-script argument guard |
| (final commits) | `docs/final/` deliverables, demo package, README status (see `git log`) |
