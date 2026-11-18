# One-day execution plan (18 Nov 2026)

**Basis.** The plan follows from the dataset audit, the metrics audit and the readiness audit (`docs/audit/`).

**Priority order.** A working, demonstrable application comes first; research quality second. Nothing here changes the protocol, thresholds or confirmatory families.

**Status values:**
- ✅ done today;
- ⏳ owner action;
- ⛔ impossible today without breaking the protocol.

## Critical (complete, working, demonstrable software)

| # | Task | Estimate | Status / evidence |
|---|---|---|---|
| C1 | Verify Git state; identify uncommitted work | 5 min | ✅ HEAD db5b2a6 = origin; `main` = 81f561e; only the untracked PDF package from the previous turn |
| C2 | Dataset audit from raw files | 45 min | ✅ `one_day_dataset_audit.md` + `dataset_audit.py` |
| C3 | Logs, metrics and canonical test reconciliation | 45 min | ✅ `one_day_metrics_and_logs_audit.md`; `test_log_db5b2a6.txt` |
| C4 | Fresh clone + README install + full test suite in that environment | 20 min | ✅ `software_readiness.md`; `docs/audit/e2e/run_e2e.sh` |
| C5 | End-to-end CLI: demo fixture, worked example, hybrid, robustness, missing path, CBOM/SARIF validation, determinism | 30 min | ✅ same |
| C6 | Baselines runnable end to end (synthetic fixture side-by-side) | 30 min | ✅ `docs/final/demo/baselines/side_by_side.md` |
| C7 | Fix reproducible software defects found by C4–C6 | as needed | see `software_readiness.md` Sec. 4 |
| C8 | Lecturer demo sequence based on verified outputs | 20 min | ✅ `software_readiness.md` Sec. 6 |
| C9 | Commit and push in logical commits | 10 min | ✅ |

## Important (quality and credibility)

| # | Task | Estimate | Status |
|---|---|---|---|
| I1 | Apply D7 Option A consistently | 15 min | ✅ manuscript Secs. I and IX; decision log |
| I2 | Inspect Mehl's scanner (D14) and the B1 variants (D15); write recommendations | 45 min | ✅ `research_decisions_and_novelty.md`; **decisions wait for the owner** |
| I3 | Mark method-implied roles in the summary output (W5; display only) | 1 h | not done. It would change the committed demo outputs and their recorded hashes. Recommended after the demo. |
| I4 | Licence decision (D5) and the pyproject licence-table deprecation | 10 min after the decision | ⏳ owner |
| I5 | Correct the stale pilot figure (51.7% → 53.3%) and the SP 800-227 citation precision (W6) in adopted documents | 30 min after approval | ⏳ owner approval (pre-F1 correction route; adoption-record update) |

## Research workflow (owner-gated; cannot be done by Claude)

| # | Task | Earliest | Status |
|---|---|---|---|
| R1 | Record `docs/benchmark/ai_review_identity.json` (V8) with the real interface, model, timestamp and isolation | today | ⏳ owner |
| R2 | Isolated ChatGPT specification review and sign-off | after R1 | ⏳ owner |
| R3 | Pilot and synthetic validation loops (D2) | after R2 | ⏳ owner |
| R4 | DV annotation, then the intra-rater re-label after ≥ 14 days | after R3 | ⏳ owner; ⛔ cannot finish today (14-day gap) |
| R5 | D6 re-run and feasibility check; F1 freeze; test fetch; T annotation (+ 14 days); F2; E | after R4 | ⛔ cannot happen today |

## Optional (publication; later)

| # | Task | Estimate |
|---|---|---|
| O1 | Format the manuscript to the owner's IEEE sample (D1) | 3–4 h after the sample arrives |
| O2 | Re-check Yuan et al., CryptoPyt and Cryptbara in full text (library access) | 2 h |
| O3 | Final novelty audit (D11) | after E |
| O4 | Linux reproducibility run | 1 h |
