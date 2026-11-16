# Evaluation protocol v1.0.4, revision 4 — PROPOSED, NOT ADOPTED (protocol v1.0.3 remains in force)

Project: Post-quantum crypto scanner for Python projects. Revisions 1–4 were all prepared on 14 Nov 2026, in that order, before any annotation or test-split access. Supporting analyses: `R4_01`–`R4_06`; change log `R4_09`. Marked items await owner decisions (V#).

## 1. Research questions and hypotheses

The wording of RQ1–RQ4 and H1–H4 is unchanged. The H1, H3 and H4 decision rules are unchanged; their intervals are annotated "sites clustered in 7 purposively selected repositories".

**H2 (wording unchanged):** "correct-per-eligible-site of the provenance-aware arm exceeds the method+argument arm by ≥ 10 percentage points at equal coverage."

**H2 operationalisation [v1.0.4]:**
- **Arms (V18):** Module C `full` vs. `method+args`, both with no tier gate (T0); UNKNOWN roles abstain.
- **Equal coverage (V12′):** R4-03.
- **Estimand:** the repository-balanced matched difference δ over the 7 frozen test repositories' primary-set eligible sites (R4-02 Sec. 2).
- **Confirmatory (V10a‴, V10b″, V13′, V17):** B1 (H0: δ ≤ 0), together with B3 and B4, under Holm m = 3 at one-sided family α = 0.025. Test: stratified re-matching bootstrap, B = 10,000, seed 20261113.
- **Exploratory, pre-specified:** B2 (H0: δ ≤ 0.10), by the bootstrap lower bound.
- **Categories:** R4-02 Sec. 4.
- **Secondary:**
  - the proposed system (full at τ = T2) vs. method+args, matched;
  - natural-coverage comparisons;
  - a fixed-target matching variant;
  - site-level exact McNemar / Tango on matched pairs.
- **Exploratory generalisation:** the repository-level t test, sign-flip, Wilcoxon, leave-one-repository-out, and all seven δ_r values (R4-04).
- **Planning statement:** the confirmatory direction test is likely to detect true effects of about 15 pp or more. The 10 pp margin can be established with adequate power only if the true effect is about 20–25 pp or more (R4-02 Sec. 3). Confirmatory claims concern the 7 selected repositories only.

**F-A (Experiment A):** the proposed system vs. each baseline that ran, at natural coverage. δ > 0, pooled exact McNemar, Holm, one-sided 0.025, a separate family.

## 2. Datasets and sampling

- **Dataset A:** unchanged.
- **Dataset B:** 13 repositories (4 development, 2 validation, 7 test), as frozen in the manifest (V15). Labelled by the owner blind to tool outputs, reviewed by a separately conducted, isolated, blind AI review, and adjudicated by the owner.
- **Quotas:** 30 per test repository and 25 per development or validation repository, giving 360 primary-set eligible sites. Minimums: 300 for Dataset B and 150 for test. Shortfalls are reported.
- **Primary population and analysis sets (V14′):** R4-05 Sec. 1–2, including S2, annotator-added and tool false-positive reporting.
- **Sampling rule:** revision 3 (`R3_07` Sec. 2), unchanged: strata S1-app, S1-nonapp and S2; scope precedence vendored > test > example > app; opaque IDs; B0; non-app issuance never beyond the remaining cap; counted = S1-app + min(S1-nonapp, cap); stopping rules; ledger pushed after every step; strict validation.
- **Frame audit (V7′):** R4-05 Sec. 4; descriptive.

## 3. Annotation

As in revision 3 (`R3_07` Sec. 3), with:
- **Reliability (V3′):** R4-05 Sec. 3 for Phase DV and Phase T.
- **Context (V16′):** R4-05 Sec. 5. `context_used` sits inside the hashed primary file before the AI review. A packet-first seeded 10% subset per phase.

## 4. Experiments

Unchanged (CBOMkit not run, D4 = A).

## 5. Statistics

- **Family level:** one-sided α = 0.025 (V17).
- **H2:** the stratified re-matching bootstrap is primary (R4-02 Sec. 5). Holm adjustment table: R4-02 Sec. 6.
- **Site-level tests:** used only for the fixed-repository estimand.
- **Repository-level tests:** exploratory.
- **Cluster bootstrap over repositories:** never used for inference with K = 7.
- **Secondary label analyses and unresolved bounding (V4, V9):** as in revision 3, applied to matched outcomes.
- **Seed sensitivity:** matched results over 100 tie-break seeds.

## 6. Freeze

Revision 3 F1/F2 contents (`R3_07` Sec. 6), plus:
- the `rev4/scripts` hashes and their unit-test log, re-run at F1 on the production implementations;
- the bootstrap calibration result (checklist B5);
- the Phase DV matched coverage c_DV;
- the V18 arm configuration.

## 7. Threats to validity

Revision 3 list, plus:
- **purposive repository selection:** no generalisation claim;
- **coverage matching:** depends on tiers and seeds;
- **bootstrap calibration:** based on an assumed generative model;
- **the margin:** exploratory by design.

## Changelog

`R4_09`. The wording of H1–H4, the H1/H3/H4 decision rules, the metric definitions, τ = T2 (proposed system) and the manifests are unchanged.
