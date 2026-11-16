# Phase 3 readiness checklist v2 (PROPOSED, revision 2)

Status vocabulary: READY / NOT READY / BLOCKED (owner decision). No item below has been done by a human yet.

## A. Methodology and specifications

| # | Item | Status |
|---|---|---|
| A1 | Owner approves V1–V11 (`06_open_decisions.md`) | BLOCKED (owner decision) |
| A2 | Protocol v1.0.4, guide v1.1 and the meta schema committed; v1.0.3 and guide v1.0 preserved in history | NOT READY (after A1) |
| A3 | Owner names the AI interface or API and the model (V8); prompt template frozen and hashed | NOT READY |
| A4 | ChatGPT specification review (taxonomy v1.0.1, policy v1.1, scoring v1.0); owner sign-off per document | NOT READY |
| A5 | Owner blind re-label of the 31 pilot sites; AI review; comparison with the Phase 1 AI labels | NOT READY |
| A6 | Synthetic subset (78): owner plus AI review; generator fixes, if any; Dataset A regenerated | NOT READY |

## B. Tooling (Claude, after A1)

| # | Item | Status |
|---|---|---|
| B1 | Sampler requirements R1–R4, R7, R13 and R15, with tests | NOT READY |
| B2 | Ledger (R5, R14), strict envelope validation (R6, R12), with the adversarial tests | NOT READY |
| B3 | Packet builder and prompt template (R9), with the forbidden-content test | NOT READY |
| B4 | Comparison, κ, intra-rater, self-consistency, derivation, secondary and bounding scripts (R10) | NOT READY |
| B5 | Frame-audit tooling (R8) | NOT READY |
| B6 | Development/validation orders regenerated (opaque IDs, scope classes, S1-nonapp) | NOT READY |
| B7 | Batch runner on real tools | READY (`docs/implementation/runner_evidence/`; `runs/validation/run1`) |
| B8 | Dataset A reproducible; holdout unscanned | READY |

## C. Development and validation labels (owner)

| # | Item | Status |
|---|---|---|
| C1 | Frame audit: ≥ 60 eligible sites audited | NOT READY |
| C2 | Development/validation annotation loop to quota (25 per repository); every ledger entry pushed | NOT READY |
| C3 | Intra-rater sample (≥ 50, ≥ 14 days later): κ(gt_role) ≥ 0.60, or guide revised and re-labelled | NOT READY |
| C4 | AI self-consistency (≥ 30) reported | NOT READY |
| C5 | Unresolved cases listed | NOT READY |
| C6 | Development/validation results reported as development results | NOT READY |

## D. Frozen rules

| # | Item | Status |
|---|---|---|
| D1 | Hypotheses, H1/H3/H4 rules, scoring v1.0, τ = T2, statistics | READY |
| D2 | H2 outcome categories and comparison families (V10) | BLOCKED (owner decision) |
| D3 | Manifests (7 test repositories, baselines), D4 = A | READY |
| D4 | Sampling rule (v1.0.3 plus the V2, V5, V6, V9 and V11 amendments) | NOT READY (after A1) |

## E. Freeze and evaluation

| # | Item | Status |
|---|---|---|
| E1 | F1 record with v1.0.4 contents, committed and tagged | NOT READY (needs A–D) |
| E2 | Test fetch; sealed extraction; test annotation loop with the ledger pushed after each step; intra-rater; attestation | NOT READY (after E1) |
| E3 | F2 record, tagged | NOT READY (after E2) |
| E4 | E run once; determinism check; primary, secondary and bounding analyses | NOT READY (after E3) |

## Not required for F1

Licence (D6); optional external re-annotation; the novelty audit and final report (after E).
