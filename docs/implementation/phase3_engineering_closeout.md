# Phase 3 engineering close-out (R4-19 implementation)

Branch `phase3-preparation`. Implementation of R4-19 under protocol v1.0.4, adopted 16 Nov 2026 by owner approval of R4-18 as amended by R4-21 (C1–C6) and edge-case rules A–D. Closed 17 Nov 2026.

**Status:**
- No specification review, annotation, F1, F2 or E has started.
- No held-out test repository has been accessed, fetched, cloned or scanned.
- `main` is untouched; no force-push.
- No labels, credentials or keys are in git.

## 1. Completed components

| # | Component | Main files | Commit | Tests |
|---|---|---|---|---|
| — | Proposals R4-01…R4-21 archived as the historical record | `docs/proposals/` | 0b628f4 | 82 reference tests still pass |
| 16 | Protocol v1.0.4, annotation guide v1.1, adopted decision record, normative analysis plan, adoption notices on R4-02/05/06/07/09/10/18/21, adoption record with hashes | `docs/specification/evaluation_protocol.md`, `phase3_analysis_plan.md`, `phase3_decisions.md`, `adoption_record_v1.0.4.json`, `docs/benchmark/annotation_guide.md`; v1.0.3 and v1.0 kept as `*_v1.0.3.md` / `*_v1.0.md` | 325b9b3, e16219a | `tests/test_protocol_consistency.py` (15) |
| 1–2 | Sampler: M1–M14, scope classes, S1-app / S1-nonapp / S2, B0, non-app cap, strict inputs, quota constant; opaque IDs; DV orders regenerated (locations unchanged; only jwcrypto `tests.py` reclassified), v1.0.3 orders archived | `pqscan/bench/candidates.py`, `benchmark/candidates/` | ec80aba | `tests/test_candidates.py` (65) |
| 3–7 | Hash-chained ledger (hashes only), strict label validation with meta schema, packet rule `packet-v1` with forbidden-content check, packet-first subset, AI-review records (identity required; parser never fills fields), comparison, adjudication, unresolved report, workflow CLI | `pqscan/bench/ledger.py`, `labels.py`, `packets.py`, `review.py`, `annotate.py`; `docs/benchmark/meta_schema.json`, `ai_review_prompt_v1.md` | 8e22f4b | `tests/test_annotation_integrity.py` (22) |
| 8–9 | T0 arms `method-args-recv-T0` and `method-only-T0`; one parse per file shared by every arm; matching, exact tie-average, ranking-free variant, 100 seeds, decomposition, precisions, failure partition and S-F1/S-F2 | `pqscan/baselines/simple.py`, `pqscan/bench/matching.py` | 0fe9d7a | `tests/test_h2_matching.py` (19) |
| 10–12 | Re-matching bootstrap (random tie keys; stratified fallback implemented, inactive), Monte Carlo rule, exact guard (also on H2b), gate, K/K_e rules A–B, Holm m = 3, claims, H2a/H2b statements; F-A (one-sided exact McNemar, Holm, denominators, both weightings, CI, failures, assumptions); exploratory repository-level analyses | `pqscan/bench/h2.py`, `fa.py`, `stats.py` | 0aee42d | `tests/test_h2_inference.py` (26) |
| 13–15 | Reliability (intra-rater sample, 14-day gap, owner–AI, AI repeat-run, κ with CI, specific agreement, κ rule), frame audit, report generators (tables, abstract template, wording guard, V4/V9 label variants, analysis sets) | `pqscan/bench/reliability.py`, `frame_audit.py`, `reporting.py` | 00f8c0a | `tests/test_reliability_reporting.py` (9) |
| 17 | Differential verification against the reference; pre-F1 statistical acceptance (checkpointed) | `tests/test_h2_differential.py`, `scripts/phase3_acceptance.py`, `docs/implementation/acceptance/` | 3e8ee67, aa9d6b0, this commit | (7); acceptance below |
| — | Lecturer demonstration package | `docs/demo/` | 3c51dbc | real run in a fresh venv |

## 2. Tests and acceptance

**Production suite:** **475 passed, 1 skipped**. The skip is pre-existing. There are no failures.

**Reference suite** (archived proposal scripts): 82 passed. `scripts/adoption_record.py --check` passes.

**Differential tests (plan Sec. 11.1).** Production and the independent reference agree exactly on:
- 1,000 random matching cases: withdrawal sets, the tie-average, ranking-free, seeded estimates, b/c, arrays, precision;
- 1,000 guard / gate / Holm cases;
- the bootstrap distributions at three seeds;
- the three-repository worked example;
- the pilot tables for H2-1, H2-3 and H2-4.

**Statistical acceptance (plan Sec. 11.2–11.5)** — `docs/implementation/acceptance/statistical_acceptance.md` and `.json`:
- **Code under test:** commit aa9d6b0, clean `pqscan/` tree. Python 3.12.10, numpy 2.5.4, scipy 1.18.1. B = 1,000.
- **Seeds:** `default_rng([20261113, stream, task, chunk])`.
- **Run time:** 85.9 min.

| Check | Data sets | Result | Criterion |
|---|---|---|---|
| A. 17 fixed-repository null scenarios (S00–S15, S17) | 20,000 each | worst 0.0061 / 0.0093 / 0.0191 at a/3 / a/2 / a. **Identical, cell for cell, to R4-13's RK column.** | ≤ nominal + 3 MC-SE: pass |
| A. 8 near-equal-coverage cells | 10,000 each | worst 0.0092 / 0.0125 / 0.0213 (d = 0); identical to R4-13 | pass |
| A. S16 (random repositories, generalisation) | 20,000 | 0.0415. Not valid for generalisation, as expected; not used for inference. | n/a |
| B. Family-wise error, 8 configurations (production `run_family`, Holm m = 3) | 10,000 each | worst **0.0125** (C8); claims FWER ≤ 0.0125 | ≤ 0.025 + 3 MC-SE: pass |
| C. Two-stratum calibration, 3 configurations (design-mixture null) | 10,000 each | unstratified worst 0.0025 / 0.0040 / 0.0114 | pass; **the unstratified bootstrap stays in force**, so the fallback is not activated |

**Overall: ACCEPTED.** This is empirical calibration under the archived planning model, not a mathematical guarantee (plan Sec. 11; protocol Sec. 7).

## 3. Repository state

- All work is committed and pushed to `origin/phase3-preparation`. The working tree is clean at close-out.
- **Git-ignored and local only:**
  - `benchmark/annotation/` (future labels);
  - `benchmark/candidates/*/pool_sources_*.json`;
  - `.cache/` (acceptance checkpoints, pinned development/validation checkouts);
  - `runs/`.

## 4. Engineering notes recorded for the owner

These are decisions taken within R4-18 and documented in `docs/implementation/phase3_tracker.md`:
- **Packet-first rate:** max(0.10, 60 / planned phase candidates), giving DV 12.8% and T 10%. The realised count is reported; it cannot be topped up later.
- **Packet rule `packet-v1`:** imports, the enclosing class or function, same-file callers. Hashed in the adoption record.
- **AI-review records:** use a partial site part; incomplete AI answers are rejected rather than filled.
- **Labels never enter git:** only the hash-only ledger is versioned.
- **Lecturer demo:** local scratch paths containing the Windows user name were redacted to `<SCRATCH>` in two output files; the original hashes are recorded.

## 5. Readiness (R4-20, updated)

| Item | Status |
|---|---|
| R4-19 items 1–17 | **COMPLETE** |
| Protocol v1.0.4 / guide v1.1 adopted (A2) | **COMPLETE** |
| DV candidate orders regenerated | **COMPLETE** |
| Statistical acceptance incl. two-stratum calibration (D7) | **COMPLETE** (pre-F1 evidence stored) |
| Lecturer demo package | **COMPLETE** |
| AI interface and model recorded in `docs/benchmark/ai_review_identity.json` (A3, V8) | **BLOCKED (owner action)** |
| ChatGPT specification review of v1.0.4 / v1.1 (D1) | **BLOCKED (owner instruction + A3)** |
| Pilot (31) and synthetic (78) validation loops (D2) | BLOCKED (future execution) |
| Frame audit (D3), Phase DV annotation (D4), reliability (D5), DV pipeline and feasibility check (D6) | BLOCKED (future execution; owner instruction) |
| F1, test fetch and run, Phase T annotation, F2, E, novelty audit, final report | BLOCKED (each needs explicit owner approval; F1 first) |

## 6. Remaining owner decisions and actions

1. **Record the AI-review identity** (V8). Create `docs/benchmark/ai_review_identity.json` with:
   - `interface_or_api` (for example "ChatGPT web, Temporary Chat");
   - `model`, exactly as displayed in the model picker, or the API model ID;
   - `recorded_utc`;
   - `isolation` (the settings used).

   The tooling refuses to build any AI-review prompt until this exists.
2. **Instruct the start of the specification review**, the next step in the R4-20 sequence. It is followed by the pilot and synthetic loops and then Phase DV annotation. None starts without your explicit instruction.
3. **F1** needs separate explicit approval after Phase DV. The test split stays inaccessible until the `phase3-pretest-freeze` tag exists.
