# R4-20 Phase 3 readiness checklist (final) and sequence — PROPOSED, NOT ADOPTED

This replaces R4-10 as the current checklist. R4-10 is kept as a record.

**Status classes:**
- **COMPLETE**
- **PROPOSED, NOT IMPLEMENTED**
- **BLOCKED (owner approval)**
- **BLOCKED (future execution)**: waits on an earlier step that has not been executed.

No human annotation task is done.

## 1. Checklist

| # | Item | Status | Evidence / dependency |
|---|---|---|---|
| C1 | Phase 2 system (pqscan, baselines, batch runner, judge) | **COMPLETE** | tag `phase2-complete` (81f561e) |
| C2 | Frozen scoring policy v1.0, data dictionary, H1–H4 wording, τ = T2 | **COMPLETE** | `docs/specification/` |
| C3 | Repository manifest (13 repositories, pinned commits, split) and baseline manifest | **COMPLETE** | `benchmark/real/manifest.json`, `benchmark/baselines_manifest.json` |
| C4 | Dataset A (synthetic cases, validation subset) | **COMPLETE** | `benchmark/synthetic/` |
| C5 | Pilot labels (31) and development harness | **COMPLETE** (circular development data) | `docs/dev/pilot_harness/` |
| C6 | DV candidate pools and orders (v1.0.3 sampler) | **COMPLETE, to be regenerated** after V6 (the v1.0.3 sampler has the M1–M14 defects) | `benchmark/candidates/` (commit 664e640) |
| C7 | Revision-4 methodology: R4-01 … R4-20; reference implementation; calibration; 82 tests | **COMPLETE as proposals** | `docs/proposals/v1.0.4/rev4/` |
| A1 | Owner decisions (R4-18: V1–V18, V20–V24) | **BLOCKED (owner approval)** | — |
| A2 | Protocol v1.0.4 and guide v1.1 adopted and committed (V24) | **BLOCKED (owner approval)** | A1 |
| A3 | Owner names the AI interface and model; prompt template frozen and hashed | **BLOCKED (owner approval)**: an owner action | A1 |
| B1–B17 | Production items 1–17 of R4-19 (sampler, IDs, ledger, validation, packets, AI records, adjudication, T0 arms, matching, bootstrap, guard/Holm/claims, failures/gate, reliability, reporting, frame audit, adoption, reproducibility) | **PROPOSED, NOT IMPLEMENTED** | A2 |
| D1 | ChatGPT specification review of protocol v1.0.4 / guide v1.1 in an isolated session; owner sign-off | **BLOCKED (future execution)** | A2, A3, B6 |
| D2 | Pilot re-label (31) and synthetic-subset (78) validation loops | **BLOCKED (future execution)** | D1, B1–B7 |
| D3 | Frame audit (≥ 60 eligible sites, 6 DV repositories) | **BLOCKED (future execution)** | B15 |
| D4 | Phase DV annotation to quota (6 repositories × 25), with AI review and adjudication | **BLOCKED (future execution)** | D2, B1–B7 |
| D5 | Phase DV reliability: intra-rater (≥ 14 days later), owner–AI, AI repeat-run, packet-first subset; κ rule | **BLOCKED (future execution)** | D4, B13 |
| D6 | Phase DV H2 pipeline run (development results only); **DV feasibility check** (V21); c_DV recorded | **BLOCKED (future execution)** | D4, B8–B12 |
| D7 | Production re-calibration and differential tests within 3 MC-SE of R4-13 | **BLOCKED (future execution)** | B17 |
| E1 | F1 pre-test freeze record committed and tagged `phase3-pretest-freeze` | **BLOCKED (future execution)** | D1–D7 |
| E2 | Test fetch, sealed batch run, candidate extraction | **BLOCKED (future execution)** | E1 |
| E3 | Phase T annotation, AI review, adjudication, intra-rater | **BLOCKED (future execution)** | E2 |
| E4 | F2 label freeze, tagged `phase3-label-freeze` | **BLOCKED (future execution)** | E3 |
| E5 | Experiment E: one pre-registered evaluation; determinism check | **BLOCKED (future execution)** | E4 |
| E6 | Novelty audit | **BLOCKED (future execution)** | E5 |
| E7 | Final 60-page report | **BLOCKED (future execution)** | E5, E6 |

## 2. Sequence from owner approval to the final report

Each step has an entry condition and an exit artefact. The durations are estimates, not commitments, and depend on the owner's available time.

| Step | What happens | Entry | Exit artefact | Who |
|---|---|---|---|---|
| 1. Protocol adoption | Write protocol v1.0.4 and guide v1.1 from the approved R4-18; edit R4-02/05/06/07/09/10 per R4-16; small commits on `phase3-preparation` | owner approves R4-18 (explicitly, in chat) | committed v1.0.4 and v1.1 with changelogs; v1.0.3 preserved | Claude, on owner approval of each commit |
| 2. Production implementation | R4-19 items 1–15 and 17 (16 is done in step 1); tests with every commit | step 1 | passing suite; regenerated DV orders; differential-test report | Claude |
| 3. Specification review | ChatGPT review of v1.0.4 / v1.1 in a new isolated session (V8 procedure); the owner decides on each finding; any change is logged | steps 1–2; owner names the interface and model | review archive; owner sign-off; changelog entries if any | owner (Claude prepares the packet) |
| 4. Pilot and synthetic validation | The full annotation loop on the 31 pilot and 78 synthetic sites: primary → AI review → compare → adjudicate; tooling defects fixed | step 3 | validated tooling; loop records (reported separately, no re-label rule) | owner labels; Claude runs the tooling |
| 5. DV annotation | Phase DV to quota under the ledger, AI review and adjudication; frame audit | step 4 | DV labels (hashed); frame-audit report | owner |
| 6. Intra-rater checks | Re-label sample ≥ 14 days after the latest sampled primary label; owner–AI and AI repeat-run statistics; κ rule (< 0.60 → revise the guide and re-label DV before F1) | step 5 + 14 days | reliability report (DV) | owner re-labels; Claude computes |
| 6b. DV pipeline and feasibility | The H2 pipeline on DV (development results only); the V21 viability check; production re-calibration (D7) | steps 5, 2 | DV H2 report; c_DV; calibration record | Claude |
| 7. F1 | Freeze record: hashes of the protocol, guide, scoring, policy, code tree, DV labels, Dataset A, prompts, scripts, calibration; tag `phase3-pretest-freeze` | steps 1–6b complete | `docs/freeze/pretest_freeze.json`; tag | Claude prepares; owner approves |
| 8. Test evaluation run | Fetch the 7 test repositories at their pinned commits; sealed batch run; mechanical candidate extraction; Phase T annotation, AI review, adjudication, intra-rater | step 7 | sealed run (`test_run_seal.json`); Phase T labels | Claude (mechanical); owner (labels) |
| 9. F2 | Label freeze: hashes of the primary and AI files, adjudication log, reliability, unresolved list; tag `phase3-label-freeze` | step 8 | `docs/freeze/label_freeze.json`; tag | Claude prepares; owner approves |
| 10. E | One pre-registered evaluation with the frozen code and statistics; determinism check; every failure and exclusion recorded | step 9 | evaluation outputs; H2 table and statements per R4-17 Sec. 2.3 | Claude runs; owner reviews |
| 11. Novelty audit | Re-check the novelty claims against the base paper (DOI 10.1145/3774748.3795653), the pinned competitor versions and recent literature; adjust claims, never results | step 10 | novelty audit note | Claude drafts; owner decides |
| 12. Final 60-page report | Methods, results (including negative results), limitations, artefact description | steps 10–11 | report and artefact package | Claude drafts; owner approves |

**Indicative durations (assumed):**

| Steps | Estimate |
|---|---|
| 1–2 | about 1–2 weeks |
| 3–4 | about 1 week |
| 5 | about 30–90 owner hours |
| 6 | ≥ 14 days elapsed, plus the re-label |
| F1 | about 4–7 weeks after approval, as estimated earlier |

**Hard rules along the way:**
- **After F1:** no change to code, policy, scoring, thresholds or the analysis plan may influence step 10.
- **After step 8 begins:** nobody tunes anything on test material.
- **Any negative result is reported as such.**
