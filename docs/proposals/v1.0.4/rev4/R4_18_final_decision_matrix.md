# R4-18 Final consolidated decision matrix — PROPOSED, NOT ADOPTED

**This is the only list to approve.** It replaces the decision tables of R3-10, R4-06 and R4-15, which stay unchanged as records.

**Rules of the matrix:**
- Each decision appears **once**, in its final form.
- Superseded variants are listed in Sec. 2 so that they are not approved by mistake.
- **V19 was never assigned**: the numbering gap is deliberate, not a missing decision.

**How amendments work.** "Amendment" means the decision changes or adds text in frozen protocol v1.0.3 or guide v1.0. All such text is adopted together through **V24** as protocol v1.0.4 and guide v1.1. Each version has a dated changelog and is adopted before any test access.

**Column key:**
- **Frozen H/M?:** whether a frozen hypothesis or metric is affected.
- **Hand-off:** item numbers in R4-19.

## 1. Decisions

| ID | Decision (final form) | Rec. | Exact interpretation | Depends on | Frozen H/M? | Amendment? | Claude implements after approval |
|---|---|---|---|---|---|---|---|
| **V1** | Single-investigator design: the owner is the sole annotator and final adjudicator; a separately conducted, isolated, blind AI-assisted review; reporting wording limits | approve | Labels are "single-investigator labels with a separately conducted AI-assisted review and investigator adjudication". Never called inter-annotator or independent human validation. | V8, V3 | no H/M; changes v1.0.3 Sec. 3 (two annotators, external annotator, third-person adjudication) | **yes** (Sec. 3, 6: F2 contents) | guide/protocol text; record envelope; adjudication records (items 4, 7) |
| **V2** | Quotas 30 per test repository, 25 per development/validation repository; 360 primary-set; minimums 300 overall and 150 in test; shortfalls reported; quotas never moved | approve | the same numbers as v1.0.3, fixed as a tested constant | V15 | no | **yes**, minor ("double-annotated" removed via V1) | quota constant and test (item 1) |
| **V3** (was V3′) | Reliability: intra-rater per phase (DV, T), n = max(50, ⌈0.10·N⌉), ≥ 14-day enforced gap, 8 fields, κ with a within-repository bootstrap CI, raw agreement, confusion table, specific agreement; owner–AI agreement; AI repeat-run; rule κ(gt_role) < 0.60 → DV: revise and re-label before F1; T: test results exploratory | approve | three statistics, never called inter-annotator reliability | V1 | no H/M; replaces v1.0.3's Cohen's κ between annotators (target ≥ 0.70) | **yes** (Sec. 3, 5) | reliability sampler and statistics (item 13) |
| **V4** | Secondary label analyses (owner–AI consensus, AI-label sensitivity) on the matched outcomes | approve | secondary only; never ground truth | V12 | no | no (addition) | analysis code (item 14) |
| **V5** | Scope-classification rule: path patterns for test, example and vendored; precedence vendored > test > example > app | approve | decides which files are app vs. non-app | — | no | **yes** (sampling-rule text) | sampler M2 (item 1) |
| **V6** | Sampler, ledger and strict validation fixes M1–M14: opaque IDs, B0 for S2, non-app cap, unresolved = not eligible, hash-chained ledger, JSON booleans, unknown/duplicate IDs rejected | approve | fixes the v1.0.3 implementation defects without changing the sampling design's intent | V5, V11 | no | **yes** (sampling-rule text) | items 1–4; regenerate the DV orders |
| **V7** (was V7′) | Descriptive frame audit on the 6 DV repositories (≥ 60 eligible sites, ≥ 1 file each); states what it can and cannot estimate | approve | descriptive; no decision depends on it | — | no | no (addition) | frame-audit tooling (item 15) |
| **V8** | AI review protocol: fresh isolated session per batch (or API with a pinned model); fixed hashed prompt; packet only; interface and model identified; verbatim export; repeat-run sample. **The owner names the interface and model before the first review.** | approve | reproducible analysis from the archive; generation not reproducible | V1, V16 | no | **yes** (via V1) | item 6 |
| **V9** | Unresolved labels: recorded before F2, excluded, listed and bounded; > 5% flagged | approve | — | V1 | no | no (addition) | item 7 |
| **V10a** (final) | **H2 wording:** the frozen H2 sentence is kept verbatim; operational **H2a** (confirmatory direction, comparison H2-1) and **H2b** (pre-specified exploratory ≥ 10-point effect size, comparison H2-2). **"H2 supported" only if H2a is claimable AND H2b's 97.5% lower bound > 0.10.** Outcome table: R4-17 Sec. 2.3. | **approve** | a positive H2a never implies 10 points; templates in R4-17 Sec. 2.5 | V10b, V13 | **yes**: how the frozen H2 is tested and reported (its sentence is unchanged) | **yes** (Sec. 1) | report templates (item 14) |
| | *alternative V10a-alt:* H2b inside the confirmatory family (Holm m = 4) | — | "H2 supported" fully family-wise controlled | — | yes | yes | — |
| **V10b** (final) | **Confirmatory family F-B** = Holm (m = 3) over the **guarded** p of H2-1, H2-3, H2-4 at one-sided family α = 0.025. **A claim needs Holm rejection and a passed feasibility gate.** H2-2 stays outside F-B. F-A is a separate Holm family. | approve | sequence in R4-17 Sec. 4.2 | V13, V17, V20, V21 | refines v1.0.3 "Holm-corrected across arms" | **yes** (Sec. 1, 5) | item 11 |
| **V11** | Strata S1-app / S1-nonapp / S2, built from V5's scope classes; separate reporting of the three non-app classes | approve | — | V5 | no | **yes** (sampling-rule text) | item 1 |
| **V12** (final; includes the former V12″-E) | **Equal-coverage matching and estimand:** within each repository, on the common evaluable set, k_r = min(R_F, R_M); the larger arm withdraws lowest tier first (SHA-256 within a tier); withdrawn → ABSTAIN under the frozen judge; label-free, hashed before scoring. **Estimand:** complete-policy correctness at equal recommendation volume. **Point estimate:** exact tie-average δ̃, repository-balanced (site-weighted also reported). **Separately reported:** precision and the decomposition. **Sensitivities:** ranking-free; seeded table plus 100 seeds; V12-B fixed target; feasible-only. | approve | equal counts, not the same sites (R4-17 Sec. 3) | V18, V22 | uses the frozen metric and coverage definitions unchanged; operationalises "at equal coverage" | **yes** (Sec. 1, 5) | item 9 |
| **V13** (final) | **Confirmatory test:** stratified re-matching percentile bootstrap with random tie keys inside each resample. Repositories are fixed (inference about the 7 test repositories only); sites are resampled within repositories. B = 10,000, seed 20261113; Monte Carlo rule (B = 100,000 near a threshold). Secondary: site-level exact McNemar and Tango on the seeded matched pairs. Exploratory generalisation: repository-level t, sign-flip, Wilcoxon, leave-one-out, all 7 δ̃_r, and the cluster-by-repository CI. | approve | the bootstrap of δ̃ itself (TA) is rejected as liberal | V12 | changes the H2 test (v1.0.3: McNemar) | **yes** (Sec. 1, 5) | item 10 |
| **V14** (was V14′) | Primary population: S1 primary-set eligible sites in the candidate frame; S2, annotator-added and per-tool false-positive reporting | approve | results are limited to the stated population | V11 | no | no (addition) | item 14 |
| **V15** | 13 repositories: 4 development, 2 validation, 7 test, as frozen in the manifest | approve | replaces the planning range "8–12" | — | no | **yes** (Sec. 2) | none (manifest exists) |
| **V16** (was V16′) | `context_used` recorded in the hashed primary file before the AI review (`packet_sufficient` / `extended` plus extra ranges); packet-first labelling on a seeded 10% subset per phase (≥ 50) | approve | owner–AI agreement is interpretable on the `packet_sufficient` subset | V8 | no | **yes** (guide v1.1) | items 4–6 |
| **V17** | One-sided α = 0.025 as the family level for F-B and F-A | approve | per-test thresholds come from Holm | — | no H/M; adds a numeric level | **yes** (Sec. 5) | item 11 |
| **V18** (final) | **H2 arms, threshold T0** (no tier gate; UNKNOWN abstains): **H2-1** full vs. method+args (also H2-2); **H2-3** full vs. method+args+recv; **H2-4** full vs. method-only; secondary **H2-S** full at T2 vs. method+args at T0 | approve | the code baselines B2-method-args and B3-full-noabst already exist; T0 arms for method+args+recv and method-only must be added | — | names the frozen H2's two arms precisely | **yes** (Sec. 1) | item 8 |
| **V20** | **Coverage-gap guard:** g = (1/K) Σ_r (R_F,r − R_M,r)/n_r, exact; if g < 1/10, p → min(1, 2p) **before Holm**; if g ≥ 1/10, unchanged | approve | empirically sized correction for the equal-coverage failure of the bootstrap | V13 | no | **yes** (Sec. 5) | item 11 |
| **V21** | **Feasibility gate:** a repository is feasible iff k_r ≥ 5; the gate passes iff Σk_r/Σn_r ≥ 1/5 and ≥ 5 of 7 are feasible. If it fails: "not assessable at equal coverage". No repository dropped. Phase DV viability check before F1. | approve | label-free; can only remove claims | V12 | no | **yes** (Sec. 1) | item 12 |
| **V22** | **Execution failures** (R4-12): common evaluable set; four-way partition; concordance assertion for the Module C arms (a discordant failure stops the run); S-F1, S-F2; wording triggers at 5% / 10%; nothing ever omitted | approve | frozen n_exec and paired rules unchanged | — | no | **yes** (Sec. 5, addition) | item 12 |
| **V23** | **Identifiers:** H# for hypotheses and comparisons (H2-1, H2-2, H2-3, H2-4, H2-S, F-A); B1–B4 names only for code baseline variants; mapping per R4-17 Sec. 6.1 | approve | removes the B1–B4 collision | — | no | editorial | all documents (item 16) |
| **V24** | **Adoption package:** adopt protocol v1.0.4 and annotation guide v1.1. They contain exactly the text implied by the approved decisions above, including: H2's McNemar becomes secondary (V13); the cluster-by-repository CI becomes exploratory (V13); and the V1, V3, V5, V6, V11, V15 and V16 amendments. Dated changelog; v1.0.3 and v1.0 preserved; adopted before any test access. | approve **last** | the mechanism, not a new methodological choice | every approved decision | as listed per row | **is** the amendment | item 16, then commit in small steps |

## 2. Superseded labels (do not approve; listed only to prevent duplication)

| Superseded | Replaced by |
|---|---|
| V10a′, V10a‴, V10a‴′ | V10a (final) |
| V10b′, V10b″, V10b‴ | V10b (final) |
| V12, V12′, V12″, V12″-E, V12-B as primary | V12 (final); V12-B is a secondary analysis inside it |
| V13, V13′, V13″ | V13 (final) |
| V18, V18′ | V18 (final) |
| V3′, V7′, V14′, V16′ | V3, V7, V14, V16 (same content, primes dropped) |
| "H2-1 margin" (R4-15) | H2-2 |
| revision-4 hypothesis labels B1, B2, B3, B4 | H2-1, H2-2, H2-3, H2-4 |
| TA bootstrap; unguarded test; seeded point estimate as primary | rejected; inside V13 / V20 / V12 |

## 3. Consistency check of this matrix

- **One test, one estimate.** No two rows specify the same element differently: V12 is the only estimate, V13 the only test, V10b the only family and V17 the only α.
- **Dependencies are acyclic.** The order is V15, V5 → V11 → V6 → V18 → V22 → V12 → V13 → V20 → V21 → V17 → V10b → V10a → V24.
- **Changes to frozen hypotheses and metrics.** Only **V10a**, V13 and V18 affect how a frozen hypothesis is operationalised or tested. No frozen metric definition changes. No threshold in H1, H3 or H4 changes.
- **Owner actions that are not decisions,** required before the relevant step:
  - name the AI interface and model (V8);
  - run the ChatGPT specification review and sign off;
  - carry out all annotation.
