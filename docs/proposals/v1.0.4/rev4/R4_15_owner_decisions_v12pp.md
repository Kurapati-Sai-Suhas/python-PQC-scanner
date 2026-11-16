# R4-15 Owner decisions after the final V12″ audit — PROPOSED, NOT ADOPTED

**Status of the earlier documents:**
- **R4-06 stays unchanged** as the record of revision 4's first recommendations. This document lists the decisions on H2 that replace or amend R4-06 rows.
- **Unaffected R4-06 rows remain as they were:** V1–V9, V11, V14′–V17.
- **Nothing takes effect until the owner approves it.** Approved items are committed one by one on `phase3-preparation`, after which R4-02, R4-05, R4-06, R4-07, R4-09 and R4-10 are edited as listed in R4-16.

| # | Decision | Recommendation | Owner alternative | Consequence of the alternative |
|---|---|---|---|---|
| **V12″** (replaces V12′) | Equal-coverage matching for H2 exactly as in R4-11 Sec. 10: within-repository k_r = min on the common evaluable set; lowest tier first; withdrawn → ABSTAIN under the frozen judge; label-free, hashed before scoring; complete-policy interpretation; required decomposition and precision reporting; ranking-free sensitivity | **approve** | V12-B fixed target (c_DV) as primary | can fail on test data if an arm's coverage falls below the target; R4-03 Sec. 2 |
| **V12″-E** (new) | **Point estimate = exact tie-average δ̃** (no seed). Primary-seed table and 100-seed distribution secondary. | **approve** (your provisional preference; it is exact and O(n)) | seeded δ(20261113) as the point estimate | ties add 3–23% of the point estimate's variance (R4-03c Sec. 8); the decision is unchanged either way |
| **V13″** (amends V13′) | Confirmatory test = **stratified re-matching percentile bootstrap with random tie keys inside each resample** (B = 10,000, seed 20261113), applied to the 7 fixed repositories; Monte Carlo rule (B = 100,000 if within 3 MC-SE of a threshold); site-level McNemar/Tango secondary | **approve** | bootstrap of δ̃ itself (TA) | **reject:** liberal, 0.0293 at a nominal 0.025 (R4-13 Sec. 2) |
| **V20** (new) | **Coverage-gap guard:** g = (1/K) Σ (R_F − R_M)/n_r as an exact fraction; active iff g < 1/10 (negative, zero and below 0.10 activate; exactly 0.10 does not); when active, p → min(1, 2p) before Holm | **approve** | no guard | unguarded error at equal coverage is 0.042 at a nominal 0.025 (R4-13 Sec. 3) |
| **V21** (new) | **Feasibility gate:** repository feasible iff k_r ≥ 5; gate passes iff pooled Σk/Σn ≥ 0.20 and ≥ 5 of 7 feasible; if it fails, the comparison is "not assessable at equal coverage" and cannot support an H2 claim; no repository is dropped; Phase DV check before F1 | **approve** | gate descriptive only | a "win" could rest on flags and abstentions alone (`results/worked_example_v12pp.md`, repository C) |
| **V22** (new) | **Execution failures** per R4-12: common evaluable set C_r as the paired denominator; full partition reported; S-F1 and S-F2 sensitivities; wording triggers at 5% / 10%; concordance assertion for the Module C arms | **approve** | — | — |
| **V18′** (amends V18) | H2 arms, all at threshold T0 (no tier gate; UNKNOWN abstains): **H2-1** full vs. method+args; **H2-3** full vs. method+args+recv; **H2-4** full vs. method-only; secondary **H2-S** full at T2 vs. method+args at T0 | **approve** | — | V18 as written left H2-3 and H2-4 thresholds unstated |
| **V10a‴′** (amends V10a‴) | Direction confirmatory (H2-1); the 10-point margin exploratory via the RK bootstrap's one-sided 97.5% lower bound; the protocol states that the recommendation part of δ cannot exceed the matched coverage | **approve** | margin confirmatory under Holm m = 4 | margin power at a/3 is only 0.02 when the true δ is 0.12, 2 points above the margin (R4-13 Sec. 4, S17+); higher true δ is not reachable in this model |
| **V10b‴** (amends V10b″) | Holm m = 3 over **guarded** p of H2-1, H2-3, H2-4 at one-sided family α = 0.025; a claim also needs the gate | **approve** | m = 4 with the margin | as above |
| **V23** (new) | Rename the hypothesis IDs B1, B3, B4 (and the margin B2) to **H2-1, H2-3, H2-4 (and "H2-1 margin")** in every document, to remove the collision with the baseline names B1-algorithm…B4-full-T2 | **approve** | keep, with a mapping table | risk of misreporting the arms |
| **V24** (new) | **Amend frozen protocol v1.0.3 in v1.0.4** (before any test access; dated changelog): H2's paired McNemar becomes secondary, replaced as primary by V13″; the "cluster bootstrap … by repo" CI is kept only as an exploratory output with the caveat that the 7 repositories are purposive | **approve** | keep McNemar as the primary H2 test | McNemar on matched pairs is valid but conservative (variance ratio 0.486), and at natural coverage it tests a different estimand |

**Unchanged:**
- **V17:** one-sided α = 0.025 as the family level.
- **The H2 wording, the metrics, the scoring policy, τ = T2, the manifests** and every non-H2 decision.

**Before F1, implementation and calibration items (not owner decisions):**
- production code for the V12″/V13″/V20–V22 items;
- T0 arms for method+args+recv and method-only in the harness;
- the concordance assertion;
- re-running R4-13 on production code;
- the Phase DV feasibility check.

All of these are listed in R4-16 rows 4 and 25.
