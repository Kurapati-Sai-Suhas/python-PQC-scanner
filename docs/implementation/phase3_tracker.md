# Phase 3 implementation tracker and blocker register (live)

**Scope.** Implementation of R4-19 (17 items) under protocol v1.0.4, adopted 2026-11-16. Updated at every batch close.

**Status values:**
- `done`: the acceptance tests pass and the work is committed;
- `in progress`;
- `pending`;
- `blocked`: the reason is in the blocker register.

**Previous trackers.** `implementation_tracker.md` and `phase3_readiness_checklist.md` are the earlier records.

| # | R4-19 item | Batch | Status | Commit(s) | Acceptance evidence |
|---|---|---|---|---|---|
| 16 | Protocol v1.0.4, guide v1.1, decisions, analysis plan; R4 adoption notices; adoption record | 1 | done | 0b628f4 (proposals archived), 325b9b3 | `tests/test_protocol_consistency.py` (15); `scripts/adoption_record.py --check` |
| 2 | Opaque candidate IDs (collision check) | 1 | done | ec80aba | `tests/test_candidates.py` |
| 1 | Sampler M1–M14, scope classes, strata, B0, cap, quota constant; DV orders regenerated (v1.0.3 archived) | 1 | done | ec80aba | `tests/test_candidates.py` (65), byte-identical rebuild check |
| 3 | Hash-chained issuance ledger (hashes only) | 2 | done | 8e22f4b | `tests/test_annotation_integrity.py` |
| 4 | Strict label validation (envelope, `meta_schema.json`) | 2 | done | 8e22f4b | same |
| 5 | Packet builder `packet-v1`, forbidden-content check, packet-first subset | 2 | done | 8e22f4b | same |
| 6 | AI-review records (identity required, fixed prompt, parser that never fills fields) | 2 | done | 8e22f4b | same |
| 7 | Comparison, adjudication, unresolved report; workflow CLI `pqscan.bench.annotate` | 2 | done | 8e22f4b | same (22, incl. end-to-end on fixtures) |
| 8 | T0 arms for method+args+recv and method-only; one parse per file shared by all arms | 3 | done | 0fe9d7a | `tests/test_h2_matching.py` |
| 9 | Matching, tie-average, ranking-free, 100 seeds, decomposition, precisions | 3 | done | 0fe9d7a | same (19, incl. brute force over all tie orders) |
| 10 | Re-matching bootstrap (random tie keys), Monte Carlo rule, stratified fallback variant | 4 | done | 0aee42d | `tests/test_h2_inference.py` |
| 11 | Guard (exact, also on H2b), Holm, claims, H2a/H2b statements | 4 | done | 0aee42d | same |
| 12 | Execution failures (S-F1, S-F2, concordance), feasibility gate, K / K_e rules A–B | 3–4 | done | 0fe9d7a, 0aee42d | same |
| — | F-A (one-sided exact McNemar, Holm, denominators, both weightings, CI, failures) and exploratory repository-level analyses | 4 | done | 0aee42d | same (26) |
| 13 | Reliability statistics (intra-rater, owner–AI, AI repeat-run) | 5 | done | 00f8c0a | `tests/test_reliability_reporting.py` (κ checked against statsmodels) |
| 15 | Frame-audit tooling | 5 | done | 00f8c0a | same |
| 14 | Report generators (tables, abstract template, wording guard, V4/V9 label variants, analysis sets) | 5 | done | 00f8c0a | same (9) |
| 17 | Differential tests (1,000 + 1,000 random cases, bootstrap distributions, worked examples, pilot) | 6 | done | 3e8ee67 | `tests/test_h2_differential.py` (7) |
| 17 | Re-calibration, family-wise error, two-stratum calibration on production code | 6 | in progress | 3e8ee67 (code under test) | `docs/implementation/acceptance/` |
| — | Lecturer demo package (`docs/demo/`), built in a parallel session | parallel | in progress | | |

## Engineering notes (decisions taken within R4-18, recorded for the owner)

- **Packet-first rate.** The adopted rule is "a seeded 10% per phase, ≥ 50". Packet-first labels must precede the primary label, so the subset is drawn at issuance with rate max(0.10, 60 / planned phase candidates). That gives DV 12.8% (expected about 60) and T 10% (expected about 63). The realised count is reported; a shortfall below 50 cannot be topped up afterwards.
- **Packet rule `packet-v1`.** Guide v1.1 does not define the packet's contents, so the rule was fixed in `pqscan/bench/packets.py` and is hashed in the adoption record:
  - file path;
  - top-level imports;
  - the enclosing class (≤ 400 lines) or function, otherwise ±40 lines;
  - up to 3 same-file callers;
  - line numbers, with the candidate line marked.
- **AI-review records** use the label envelope with a *partial* site part: `site_id` plus the 8 compared fields the AI gave, nothing filled in. An AI answer missing `status`, `ambiguity`, `evidence_lines` or `rationale` is rejected, and the candidate counts as not reviewed.
- **Labels never enter git.** `benchmark/annotation/` is git-ignored; only the hash-only ledger in `benchmark/ledger/` is versioned.
- **Calibration uses a fixed B.** The pre-F1 calibration switches the Monte Carlo rule off, as R4-13 did. The real analysis always applies it.

## Blocker register

| # | Blocker | Blocks | Owner action? | Status |
|---|---|---|---|---|
| X1 | The AI interface and model identity are not yet recorded (`docs/benchmark/ai_review_identity.json`, V8) | any AI review (specification review, pilot loop) | **yes**, before any AI review | open; not needed for engineering |
| X2 | Specification review, human annotation, F1, F2 and E each need explicit owner approval | everything after engineering | yes | open, by design |
