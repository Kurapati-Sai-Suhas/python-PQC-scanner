# Change log for revision 3 (PROPOSED). Revisions 1 and 2 are preserved unchanged in `docs/proposals/v1.0.4/`.

## Revision 2 → revision 3

| Area | Revision 2 | Revision 3 | Reason | Decision |
|---|---|---|---|---|
| H2 rule | exact McNemar vs. 0 plus observed ≥ 10 pp (V10a) | fixed sequence: δ > 0, then δ > 0.10 (Tango-type margin hypothesis), repository-level t test; three categories (V10a′) | revision 2 did not test the literal claim: P(supported) at a true 10 pp was 0.47–0.54 regardless of n | V10a′ (replaces V10a) |
| Holm family | F-B, m = 3 | F-B, m = 4 (adds H2-margin) | valid familywise control with the margin hypothesis | V10b′ (replaces V10b) |
| Inferential unit | site-level McNemar; clustering mentioned only as a caveat | repository-level t (df = 6), sign-flip robustness, site-level tests secondary | site-level Tango size inflates from 0.025 to 0.069–0.083 at τ = 0.10 (simulated); 7 clusters | V13 (new) |
| Sidedness | unstated (two-sided .05 implied) | one-sided 0.025 for H2 and F-A | directional hypotheses; consistent with 95% CIs | V17 (new) |
| "At equal coverage" | not operationalised | coverage matching by evidence tier | genuine defect: the arms abstain at different rates | V12 (new) |
| Power statement | site-level, independence | cluster-aware simulation; margin step low-powered; "partially supported" most likely under moderate effects | honesty | V2, V13 |
| Repository count | "8–12 repositories" | 13 (4 development, 2 validation, 7 test) | factual: the manifest | V15 (new) |
| Quota table | test 30, development/validation 25 | split into development (4 × 25) and validation (2 × 25); total 360 explained | reconciliation | V2 |
| S2 and annotator-added | unspecified | excluded from quotas, targets and primary metrics; reported separately; sensitivity "all eligible" | different inclusion mechanisms | V14 (new) |
| Sampler mismatch M6 | — | non-app issuance never exceeds the remaining cap, even after S1-app is exhausted | found in revision 3's code comparison | V6 |
| Intra-rater | ≥ 50 per phase, phase undefined | Phase DV and Phase T; n = max(50, ⌈0.10·N⌉); stratified by repository and eligibility; seed suffixes; per-class agreement rule (≥ 5 items) | precision | V3 |
| AI review | Temporary Chat settings | adds: never the existing project conversation; per-batch isolation; reproducibility limits stated; repeat-run n = max(30, 10%) | blinding and honesty | V8 |
| Context | context-difference tag | owner records `context_used`; agreement reported for the `packet_sufficient` subset | interpretable owner–AI agreement | V16 (new) |
| Frame audit | ≥ 60 sites, ≥ 6 files, Wilson CI | round-robin seeded files, ≥ 1 per repository; file-level cluster bootstrap; descriptive; Wilson shown only with a caveat | clustering | V7 |
| Scope | example and vendored classes | explicit precedence vendored > test > example > app; three classes reported separately | determinism | V5, V11 |
| Workload | 60–105 h | 52 / 102 / 216 h (low / expected / high; assumed) | full model per phase | — |

## Corrections to revision 2 statements

1. "P(significant and observed ≥ 10 pp)" figures were correct, but they described Option A, which does not test the literal claim.
2. Revision 2's power claims (for example "0.84 at α = .05") assumed independent sites and two-sided tests. They are superseded by `R3_01`.
3. Revision 2 still said "8–12 repositories" (inherited). Corrected.
4. Revision 2's intra-rater "per phase" was undefined. It is now defined.
5. Revision 2's "Wilson CI" for the frame audit ignored clustering.

## Unchanged

The wording of H1–H4; the H1, H3 and H4 decision rules; `scoring_policy.md` v1.0; τ = T2; Dataset A; the manifests; D4 = A; protocol v1.0.3 and guide v1.0; all Phase 1 and 2 evidence; production code (no code changed in revision 3).
