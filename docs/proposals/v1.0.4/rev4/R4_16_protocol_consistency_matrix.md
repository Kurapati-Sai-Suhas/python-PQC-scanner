# R4-16 Protocol consistency matrix for H2 — PROPOSED, NOT ADOPTED

**Purpose.** This matrix cross-checks every H2-related element across:
- the frozen protocol v1.0.3 (`docs/specification/evaluation_protocol.md`) and the frozen scoring and data dictionary;
- the revision-4 documents.

"Final V12″" is the position recommended in R4-11. Nothing is edited in the other documents until the owner approves; the "action" column lists each required edit.

**Status codes:**
- **OK**: consistent.
- **EDIT**: consistent in intent, but the text must be updated.
- **CONFLICT**: documents disagree; the resolution is stated.
- **AMEND-v1.0.3**: the change departs from frozen v1.0.3 text and needs a dated v1.0.4 changelog entry. That is allowed before test access; its consequence is stated.

| # | Element | Frozen v1.0.3 / scoring / dictionary | R4-02 | R4-03, R4-03a | R4-05 / R4-07 | R4-06 | Final V12″ | Status and action |
|---|---|---|---|---|---|---|---|---|
| 1 | H2 wording | "correct-per-eligible-site … exceeds … by ≥ 10 pp at equal coverage" | unchanged | unchanged | unchanged | unchanged | unchanged | **OK**. The wording is kept; R4-07 adds "complete-policy" interpretation text. |
| 2 | What H2 measures | not stated | "more often correct" | complete policy (R4-03 audit 1) | not stated | not stated | complete-policy correctness at equal recommendation volume; precision separate (R4-14) | **EDIT** R4-02 Sec. 2 and 4, R4-07 Sec. 1 |
| 3 | Primary arm pair | "provenance-aware vs. method+argument arm" | full vs. method+args, both T0 | same | R4-07: full vs. method+args at T0 | V18: same | H2-1: `full` T0 vs. `method+args` T0 | **OK** |
| 4 | Other confirmatory arms | Experiment B ablation ladder (method-only → +args → +receiver → +provenance → +downstream) | B3 full vs. method+args+recv; B4 full vs. method-only; **threshold not stated** | H2-3, H2-4 at T0 | R4-07: B3, B4, threshold not stated | V18 covers only full vs. method+args | H2-3 and H2-4: both arms at T0 | **EDIT** V18 must name all three pairs and T0. `pqscan/baselines/simple.py` has T0 arms only for method+args and full, so production needs T0 arms for method+args+recv and method-only (checklist B4). |
| 5 | Comparison IDs | — | B1–B4 | H2-1/H2-3/H2-4 | B1–B4 | B1–B4 | H2-1, H2-3, H2-4 (H2-S secondary; margin = "H2-1 margin") | **CONFLICT**: the IDs B1–B4 collide with the baseline names B1-algorithm…B4-full-T2. Rename in R4-02, R4-06, R4-07 and R4-10. |
| 6 | Secondary system comparison | τ = T2 is the proposed system | full at T2 vs. method+args at T0, secondary | H2-S | secondary | V18 alternative | H2-S, secondary, matched | **OK** |
| 7 | Confirmatory family | "Holm-corrected across arms" | Holm m = 3 (B1, B3, B4) | m = 3 | m = 3 | V10b″ | Holm m = 3 over H2-1, H2-3, H2-4, using **guarded** p | **EDIT** R4-02 Sec. 6, R4-06 V10b″ (guarded p) |
| 8 | Significance level | not fixed numerically for H2 | one-sided 0.025 family | same | same | V17 | V17 | **OK** |
| 9 | Margin (10 pp) | part of H2 | B2 exploratory (bootstrap lower bound) | same | same | V10a‴ | exploratory; a feasibility note that the recommendation part ≤ c* | **EDIT** R4-02 Sec. 3 (add the note) |
| 10 | Inferential population | not stated | the 7 fixed repositories | same | R4-04 | V13′ | same; the bootstrap is invalid for generalisation (S16: 0.042) | **OK** (add the S16 evidence) |
| 11 | Coverage definition | RECOMMEND / eligible | same | same | — | V12′ | same | **OK** |
| 12 | Matching rule | not specified | "re-apply matching" | k_r = min, lowest tier first, SHA-256 ties | R4-07 → R4-03 | V12′ | same, plus a ranking-free sensitivity | **OK** |
| 13 | Point estimate | "difference" | δ (unspecified ties) | seeded δ primary, δ̃ reported | — | V12′ "seeded ties" | **δ̃ exact tie-average primary**; seeded table secondary | **EDIT** R4-02 Sec. 2, R4-03a Sec. 5/8, R4-06 V12 |
| 14 | Primary test | "paired McNemar … same sites" | re-matching bootstrap (random keys), percentile | percentile + guard | R4-07 Sec. 5 | V13′ | re-matching bootstrap **of δ̃** (no tie keys), percentile, guard | **AMEND-v1.0.3**: McNemar becomes secondary. Consequence: McNemar on matched pairs is valid but conservative (variance ratio 0.486), and McNemar at natural coverage tests a different estimand (not "at equal coverage"). **EDIT** R4-02 Sec. 5. |
| 15 | Coverage-gap guard | — | absent | g < 0.10 → 2p | absent | absent | g = (1/K) Σ (R_F − R_M)/n_r, exact fraction; active iff g < 1/10 | **EDIT** R4-02 Sec. 5–6, R4-06, R4-07 Sec. 5 |
| 16 | Feasibility gate | — | absent | k_r ≥ 5; pooled ≥ 0.20; ≥ 5 of 7 | absent | absent | same; a failed gate means "not assessable"; no repository dropped | **EDIT** R4-02 Sec. 4 (categories), R4-06, R4-07 Sec. 1 |
| 17 | Pooling | not stated | repository-balanced; "coincides with site-weighted under equal quotas" | — | — | — | repository-balanced primary; site-weighted secondary; they coincide only if every **common evaluable** n_r is equal | **EDIT** R4-02 Sec. 2 (the "coincide" sentence is true only with equal n_r) |
| 18 | Execution failures | scoring policy Sec. 5: rates on n_exec; paired on both-ran; protocol Sec. 5: paired test not applied to different site sets, reason stated | not addressed | removed before matching | R4-05 Sec. 2: "files the tool attempted" | — | R4-12: common evaluable set; full partition; S-F1, S-F2; concordance assertion | **EDIT** R4-05 Sec. 2 (paired H2 denominator = C_r), R4-07 Sec. 5. Frozen rules unchanged. |
| 19 | Cluster bootstrap by repository | Sec. 5: "cluster bootstrap (1,000 resamples) by repo … for differences" | not used for inference (K = 7) | — | R4-07: "never used for inference" | V13′ | reported as exploratory S16 only | **AMEND-v1.0.3**: retained as reporting, demoted to exploratory. Consequence: no population CI is claimed. |
| 20 | Resamples, seeds | 1,000 (cluster) | B = 10,000, seed 20261113 | same; sensitivity seeds S001–S100; Monte Carlo rule | — | V13′ | same; the bootstrap has no tie randomness | **OK** |
| 21 | Calibration evidence | — | 0.0145 (one model) | R4-03c | — | — | R4-13 (complete procedure, 18 + 8 scenarios, power, family) | **EDIT** R4-02 Sec. 5 and 7 (cite R4-13) |
| 22 | Decision categories | — | 4 categories | — | R4-07 | V10a‴ | + "not assessable at equal coverage" (gate failed) | **EDIT** R4-02 Sec. 4 |
| 23 | Natural-coverage comparison | Experiment B McNemar, same sites | secondary | secondary | secondary | — | secondary (S5) | **OK** |
| 24 | RQ3 random withholding | Experiment C, 100 seeds | — | — | — | — | unaffected (different procedure) | **OK** |
| 25 | Readiness items | — | — | — | R4-10 B4/B5 cite V12′ | — | B4: V12″ incl. T0 arms for H2-3/H2-4, the failure assertion, δ̃; B5: the R4-13 calibration re-run on production code; new C5: Phase DV feasibility check | **EDIT** R4-10 |
| 26 | Changelog | — | — | — | R4-09 | — | entries for rows 13–19 and 22 | **EDIT** R4-09 |

**Summary.**
- **No conflict remains unresolved.** The two departures from frozen v1.0.3 text (rows 14 and 19) are pre-test amendments with stated consequences.
- **One real gap.** V18 does not yet fix the thresholds of the H2-3 and H2-4 arms (row 4).
- **One naming collision.** The hypothesis IDs clash with the baseline names (row 5).
