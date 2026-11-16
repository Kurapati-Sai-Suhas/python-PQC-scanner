# Phase 3 implementation tracker and blocker register (live)

**Scope.** Implementation of R4-19 (17 items) under protocol v1.0.4, adopted 2026-11-16. This tracker is updated at every batch close.

**Status values:**
- `done`: the acceptance tests pass and the work is committed;
- `in progress`;
- `pending`;
- `blocked`: the reason is in the blocker register.

**Previous trackers.** `docs/implementation/implementation_tracker.md` and `phase3_readiness_checklist.md` are the earlier records.

| # | R4-19 item | Batch | Status | Commit(s) | Acceptance evidence |
|---|---|---|---|---|---|
| 16 | Protocol v1.0.4, guide v1.1, decisions, analysis plan; R4 adoption notices | 1 | in progress | | `tests/test_protocol_consistency.py`; `scripts/adoption_record.py --check` |
| 2 | Opaque candidate IDs | 1 | pending | | |
| 1 | Sampler (M1–M14, scope classes, strata, B0, cap, stopping, quota constant); regenerated DV orders | 1 | pending | | |
| 3 | Hash-chained issuance ledger | 2 | pending | | |
| 4 | Strict label validation (envelope, meta schema) | 2 | pending | | |
| 5 | Packet builder, forbidden-content test, packet-first subset | 2 | pending | | |
| 6 | AI-review records | 2 | pending | | |
| 7 | Owner adjudication, unresolved reporting | 2 | pending | | |
| 8 | T0 arms for method+args+recv and method-only; shared evidence | 3 | pending | | |
| 9 | Coverage matching, tie-average, ranking-free, 100 seeds | 3 | pending | | |
| 10 | Re-matching bootstrap, Monte Carlo rule | 4 | pending | | |
| 11 | Guard, Holm, claim logic, H2a/H2b statements | 4 | pending | | |
| 12 | Execution failures, feasibility gate, K / K_e | 4 | pending | | |
| — | F-A and other pre-registered analyses | 4 | pending | | |
| 13 | Reliability statistics | 5 | pending | | |
| 15 | Frame-audit tooling | 5 | pending | | |
| 14 | Analysis and reporting | 5 | pending | | |
| 17 | Differential tests, re-calibration, two-stratum calibration, family-wise error | 6 | pending | | |
| — | Lecturer demo package (`docs/demo/`), built in a parallel session | parallel | in progress | | |

## Blocker register

| # | Blocker | Blocks | Owner action? | Status |
|---|---|---|---|---|
| X1 | The AI interface and model identity are not yet named (V8) | the first AI review (specification review, pilot loop) | **yes**, before any AI review | open; not needed for engineering |
| X2 | Human annotation, F1, F2 and E need separate owner approval | everything after engineering | yes | open, by design |
