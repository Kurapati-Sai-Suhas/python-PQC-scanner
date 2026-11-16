# Owner decisions — PROPOSED, revision 3

Nothing here takes effect until the owner approves it. Classification of revision 2's items: **APPROVE** (adopt as revision 3 states), **MODIFY** (adopt only in revision 3's modified form), **REJECT/REPLACE**, **HOLD**.

## 1. Audit of V1–V11 (revision 2 → revision 3)

| # | Revision 2 item | Revision 3 classification | What changed |
|---|---|---|---|
| V1 | single investigator + blind ChatGPT + owner adjudication | **APPROVE** (revision 3 form) | isolated-session rule; `context_used` (V16); wording limits |
| V2 | quotas 30 / 25, power statement | **MODIFY** | quotas kept (360 primary-set sites, 13 repositories); power claims replaced by the cluster-aware statement (`R3_01` Sec. 5) |
| V3 | intra-rater ≥ 50 per phase, κ < 0.60 rule | **MODIFY** | phases defined (DV, T); n = max(50, 10%); stratified; per-class reporting rule |
| V4 | consensus and AI-label analyses; robust wording | **APPROVE** | applied to the matched-coverage, repository-level H2 |
| V5 | broader test-file rule | **APPROVE** | precedence added (V11) |
| V6 | sampler, ledger and validation fixes | **MODIFY** | mismatch M6 added; S2 handling per V14 |
| V7 | frame audit ≥ 60 sites, Wilson CI | **MODIFY** | descriptive; round-robin across repositories; file-level cluster bootstrap |
| V8 | ChatGPT settings | **MODIFY** | the existing conversation is never used; per-batch isolation; reproducibility limits; repeat-run n |
| V9 | unresolved: excluded and bounded | **APPROVE** | — |
| V10a | McNemar vs. 0 plus observed ≥ 10 pp | **REJECT → replace with V10a′** | does not test the literal claim |
| V10b | Holm F-B, m = 3 | **REJECT → replace with V10b′** | margin hypothesis added; m = 4 |
| V11 | S1-nonapp (test, example, vendored) under one cap | **APPROVE** (revision 3 form) | precedence; three classes reported separately |

## 2. Decisions requiring the owner's approval (revision 3)

| # | Decision | Recommendation | Main alternative |
|---|---|---|---|
| V1 | design as in `R3_07` Sec. 3 | approve | — |
| V2 | quotas 30 test / 25 development and validation; 360 primary-set; 300 / 150 minimums; cluster-aware power statement | approve | 35 per test repository (helps step 1 only marginally under heterogeneity; does not rescue step 2) |
| V3 | intra-rater per `R3_03` Sec. 3 | approve | threshold 0.70 |
| V4 | secondary label analyses and robust wording | approve | — |
| V5 | test-file rule | approve | — |
| V6 | sampler and ledger requirements, including M6 | approve | — |
| V7 | descriptive frame audit per `R3_04` | approve | skip (frame recall unknown) |
| V8 | AI review per `R3_03` Sec. 5 | approve; **the owner names the interface and model before the first review** | API with a pinned snapshot (better identity; the owner holds the key) |
| V9 | unresolved handling | approve | — |
| **V10a′** | H2 = fixed sequence δ > 0 then δ > 0.10; three categories; the H2 wording unchanged | **approve** (the only option that tests the literal claim) | keep δ > 0 only and drop the margin (does not test H2 as written) |
| **V10b′** | F-B = Holm over 4 hypotheses | approve | H2 alone confirmatory at full α, the other arms secondary (more power, but changes the frozen "Holm across arms") |
| V11 | strata and scope precedence | approve | — |
| **V12** | "at equal coverage" = coverage matching by evidence tier (primary); natural coverage secondary | **approve** (literal) | natural coverage primary (the wording would then be misdescribed) |
| **V13** | repository as the confirmatory unit (t test, df = 6); sign-flip robustness; site-level tests secondary | **approve** | declare H2 exploratory altogether |
| **V14** | S2 and annotator-added sites excluded from quotas, targets and primary metrics; reported separately; all-eligible sensitivity | approve | pool them (no defined estimand) |
| **V15** | "8–12 repositories" corrected to 13 (4/2/7) | approve (factual) | — |
| **V16** | owner records `context_used`; agreement on the `packet_sufficient` subset | approve | owner labels the identical packet first (about +30 h, assumed) |
| **V17** | one-sided α = 0.025 for H2 and F-A | approve | two-sided α = 0.05 (equivalent in the favourable direction; conventional reporting) |

## 3. Not decided here

The licence (D6); hypotheses H1–H4 and their wording; the metric definitions; τ.
