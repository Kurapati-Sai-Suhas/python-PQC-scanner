# Phase 3 owner decisions (ADOPTED 2026-11-16)

**The decision.** On 16 Nov 2026, before any test-split access, the owner approved R4-18 (`docs/proposals/v1.0.4/rev4/R4_18_final_decision_matrix.md`) **as amended by R4-21 Sec. 6**, including corrections C1–C6. The owner also added the edge-case rules A–D below.

**What this file is.** The adopted record, with the amendments integrated. Normative texts:
- `evaluation_protocol.md` v1.0.4;
- `phase3_analysis_plan.md` v1.0;
- `docs/benchmark/annotation_guide.md` v1.1.

The proposal documents remain unchanged as history. V19 was never assigned.

| ID | Adopted decision | Normative text |
|---|---|---|
| V1 | Single-investigator design (owner labels and adjudicates); separately conducted isolated blind AI-assisted review; wording limits | protocol Sec. 3; guide Sec. 1, 8 |
| V2 | Quotas 30 (test) / 25 (development, validation); 360 primary-set; minimums 300 / 150; quota table as a tested constant | protocol Sec. 2 |
| V3 | Reliability: intra-rater, owner–AI and AI repeat-run per phase; samples, seeds, gap, reporting and κ(gt_role) < 0.60 rule | protocol Sec. 3 |
| V4 | Consensus and AI-label secondary analyses | protocol Sec. 5.6 |
| V5 | Scope classes and precedence vendored > test > example > app | protocol Sec. 2; guide Step F |
| V6 | Sampler fixes M1–M14, opaque IDs, B0, hash-chained ledger, strict validation | protocol Sec. 2 |
| V7 | Descriptive frame audit (6 DV repositories, ≥ 60 eligible) | protocol Sec. 2 |
| V8 | AI-review isolation, inputs, identification, export, repeat runs; **the owner names the interface and model before the first review** | protocol Sec. 3; guide Sec. 6 |
| V9 | Unresolved labels recorded before F2, excluded, listed, bounded; > 5% flagged | protocol Sec. 3, 5.6 |
| V10a | H2 is operationalised as H2a (confirmatory direction, H2-1) and H2b (exploratory 10-point criterion, H2-2). **They are always two separate statements; the unqualified phrase "H2 supported" is never used**; traceability table; templates (amended by R4-21 C4) | protocol Sec. 1.1; plan Sec. 8 |
| V10b | F-B = Holm (m = 3) over the **guarded** p-values of H2-1, H2-3, H2-4 at one-sided α = 0.025; a claim needs Holm rejection and a passed gate; H2b uses the guarded margin criterion (C5); F-A is a separate Holm family with documented assumptions (C6) | protocol Sec. 5.2–5.4; plan Sec. 7, 9 |
| V11 | Strata S1-app / S1-nonapp / S2; non-app classes reported separately | protocol Sec. 2 |
| V12 | Within-repository matching on the common evaluable set (k_r = min; lowest tier first; SHA-256 ties; withdrawn → ABSTAIN; label-free, hashed). Estimand: complete-policy correctness at equal recommendation volume over the **design mixture** (C2). Point estimate: the exact tie-average, repository-balanced. Precision and decomposition reported separately; ranking-free, seeded, 100-seed, V12-B, feasible-only and per-stratum sensitivities. | protocol Sec. 1.1, 5.3; plan Sec. 2, 4, 5 |
| V13 | Stratified re-matching percentile bootstrap, random tie keys per resample, B = 10,000, seed 20261113, Monte Carlo rule; site-level McNemar/Tango secondary; generalisation analyses exploratory; **confirmatory estimation requires K_e = 7** (C3); two-stratum calibration and its fallback (C1) | protocol Sec. 5.3, 5.5; plan Sec. 7, 11 |
| V14 | Primary population; S2, annotator-added and tool false-positive reporting | protocol Sec. 2 |
| V15 | 13 repositories (4 development, 2 validation, 7 test) | protocol Sec. 2 |
| V16 | `context_used` recorded before the AI review; packet-first 10% subset per phase | protocol Sec. 3; guide Sec. 5 |
| V17 | One-sided family-wise α = 0.025 for F-B and F-A | protocol Sec. 5.1 |
| V18 | H2 arms at T0: H2-1 full vs. method+args; H2-3 full vs. method+args+recv; H2-4 full vs. method-only; H2-S full at T2 vs. method+args at T0 | protocol Sec. 1.1 |
| V20 | Coverage-gap guard: g over the estimable repositories, exact; doubling iff g < 1/10, before Holm; also applied to H2b | plan Sec. 7.2 |
| V21 | Feasibility gate: k_r ≥ 5 per repository; Σk/Σn ≥ 1/5 and ≥ 5 feasible; otherwise "not assessable at equal coverage"; Phase DV viability check before F1; K / K_e reporting line | plan Sec. 7.3–7.4 |
| V22 | Execution failures: common evaluable set, four-way partition, concordance assertion, S-F1, S-F2, wording triggers, nothing omitted | plan Sec. 6 |
| V23 | Identifiers H2-1 … H2-4, H2-S, F-A; B-names only for code baselines | protocol Sec. 1.1 |
| V24 | Adoption of protocol v1.0.4 and guide v1.1 (this record); McNemar secondary for H2; cluster bootstrap by repository exploratory | protocol changelog |

**Owner edge-case rules (16 Nov 2026):**
- **A. K_e = 0.** No estimable-repository average exists. The coverage gap is undefined. Every H2 confirmatory and estimable-only result is reported as not assessable.
- **B. 1 ≤ K_e ≤ 6.**
  - The estimable-repository average is reported as secondary only.
  - H2a, H2-3 and H2-4 are not assessable as pre-registered.
  - H2b is not assessable for the original seven-repository estimand.
  - No zero differences are assigned and no repository is silently removed.
- **C. Two-stratum calibration.** A mandatory pre-F1 acceptance criterion:
  - app and non-app sites with different behaviour and coverage, under the actual design-mixture allocation;
  - if the unstratified bootstrap fails, the repository-by-stratum bootstrap is activated;
  - the result, code version and seed are recorded in the F1 evidence.
- **D. F-A.** The pooled McNemar is kept only with its documented assumptions. Required: per-baseline both-ran denominators; site-weighted and repository-balanced descriptive results; failure sensitivities; the stated limitation of the 7 fixed repositories.
- **No change to the statistical method after held-out results have been seen.**
