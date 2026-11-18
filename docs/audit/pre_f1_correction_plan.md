# Pre-F1 correction plan (protocol v1.0.4 → v1.0.5)

**Basis:** owner-approved decision register `owner_decision_register_v1.0.5.md` (18 Nov 2026). **Verification:** `chatgpt_review_finding_verification.md`. **Execution record:** `pre_f1_correction_log.md`.

**Unchanged throughout:** hypotheses and their wording, thresholds, primary metrics, frozen scoring, baseline membership, F-A and F-B, D7, D15, τ = T2, the sampling unit, pool and orders. **Safeguards:** no held-out test access; no annotation, pilot or synthetic loop; no F1, F2 or E; the nine files of the E30 calibration closure are never modified (`scripts/calibration_closure.py` after every code step).

## Priorities

- **P0:** F05 (until the simulation passed), F06, F14.
- **P1:** F03, F01, F02, F21, F08, F10, F04, F07, F12, F16, pilot exposure.
- **P2:** F09, F11, F13, F15, F17, F18, F19, F20, E01.

## Dependency-aware order (as executed)

| Step | Work | Depends on | Findings |
|---|---|---|---|
| 1 | Baseline quality gate; E30 closure check | — | — |
| 2 | Tests before changes: the F04 S-F1 identity on unchanged code; the F03 source-only census and its evidence | 1 | F04, F03 |
| 3 | Annotation tooling outside the E30 closure: forbidden-token gate; failures by stratum; multi-call marking; pilot-exposure tagging | 2 | F07, F04, F03, pilot |
| 4 | F-A Type I error simulation (separate script; stop and report on any failure) | 1 | F05 |
| 5 | Normative documents, archived first: protocol v1.0.5, plan v1.0.1, guide v1.2, taxonomy v1.1, dictionary v1.1, scoring note v1.0.1; run specification H-1 to H-6; amendment and adoption records; consistency tests | 3, 4 | F01–F21 |
| 6 | Paper wording and evidence register (E63–E65); E01 patch prepared, not applied | 4, 5 | F05, F06, F09, F12, F14, F04, E01 |
| 7 | Second-review package: v1.0.5 instructions, decision-status page, 21-document packet (v1.0.3 and implementation rules included), README with readiness checklist; the v1.0.4 packet kept frozen | 5 | F16 |
| 8 | Full quality gate; logical commits; push to `phase3-preparation` | all | — |

## Not done in this plan (and why)

- **External human review (F14):** needs a human reviewer outside the build team. It is a pending F1 prerequisite.
- **E01 identity commit:** needs the owner's separate approval.
- **H3/H4 analysis code:** Phase 3 work; the definitions are frozen now, the code comes before F1 in a new module.
- **Pilot, synthetic and DV annotation, F1, F2, E:** each needs its own explicit approval.
