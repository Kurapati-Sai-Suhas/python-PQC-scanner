# Results placeholders

Every table, figure and metric below depends on completed annotation and the protocol sequence. **No cell may be filled before its prerequisite exists.** The analysis plan forbids filling any confirmatory cell before stage E.

**Pipeline:**
1. V8 (AI-review identity);
2. specification review;
3. D2 loops (pilot and synthetic);
4. DV annotation and reliability;
5. D6 re-run and feasibility check;
6. F1 freeze and tag;
7. test fetch and T annotation;
8. F2;
9. E.

| Status | Meaning |
|---|---|
| **NYE** | NOT YET EVALUATED — requires owner annotation and F1/F2/E |
| **NYE-D** | requires DV annotation only (development data; not a test result) |
| **NYE-A** | requires the Dataset A validation loop (D2) |

All generators already exist in `pqscan/bench/reporting.py`, `h2.py`, `fa.py` and `reliability.py`. Nothing new needs to be designed.

## Tables

| # | Table | Content (pre-registered) | Prerequisite | Status |
|---|---|---|---|---|
| T-1 | Benchmark composition | per repository: pool sizes per stratum, issued, eligible S1-app/S1-nonapp, counted, shortfall, S2, annotator-added, unresolved | annotation of each split | NYE-D (DV) / NYE (test) |
| T-2 | Label quality | intra-rater κ with CI (n = max(50, ⌈0.1N⌉), ≥ 14 days); owner–AI agreement and specific agreement; AI repeat-run agreement; adjudication categories | annotation + 14 days | NYE-D / NYE |
| T-3 | H1a | share of eligible sites needing evidence beyond the method/algorithm name, Wilson 95% CI, by evidence scope | T labels | NYE |
| T-4 | H1b / Experiment A | per tool: n_exec, execution failures, correct, harmful (by harm category), undecided, unjustified, unassessable, detected-only, missed, coverage, Wilson CIs; strict-scoring column | T labels + E | NYE |
| T-5 | F-A | proposed system vs each baseline that ran: b, c, one-sided exact McNemar p, Holm decision, both weightings, CI; CBOMkit and Mehl reported as not run | E | NYE |
| T-6 | H2 family F-B | per comparison (H2-1, H2-3, H2-4): K, K_e, k_r per repository, matched coverage, c_pool, gate, g, guard, δ̃ with bound, p, p*, Holm decision; statement template | E | NYE |
| T-7 | H2b (exploratory) | δ̃ vs 0.10, guarded margin criterion; "met / not met / not assessable" | E | NYE |
| T-8 | H2 sensitivity | δ̃_site, seeded table with McNemar, 100-seed distribution, ranking-free δ̃, decomposition by final action, natural δ, S-F1/S-F2 | E | NYE |
| T-9 | Recommended-by-both / F only / M only | per repository and comparison | E | NYE |
| T-10 | H3 | risk–coverage at τ ∈ {T1, T2, T3}, always-recommend, random withholding (100 seeds) at matched coverage; AURC with bootstrap CI; harm at 70/80/90% coverage | E | NYE |
| T-11 | H4 | per operator × tool invariance rate, Wilson CI, base case as unit; `loaded-key` separately | D2; holdout after F1 | NYE-A / NYE |
| T-12 | Dataset A role results | role correctness by operator and library, clustered by base case | D2; holdout after F1 | NYE-A / NYE |
| T-13 | Frame audit | descriptive candidate-frame statistics (V7) | DV and T frames | NYE-D / NYE |
| T-14 | Tool false-positive profile | findings on adjudicated-ineligible candidates, by category | labels | NYE |
| T-15 | Unresolved sites | listed and bounded (Sec. 5.6) | labels | NYE |
| T-16 | Repository-level exploratory | δ̃_r for all r, leave-one-out, one-sided t (df = K_e − 1), sign-flip, Wilcoxon (S15) | E | NYE |

## Figures

| # | Figure | Prerequisite | Status |
|---|---|---|---|
| F-1 | Architecture (Modules A–E, F–G) | none | **created**: `figures/fig1_architecture.svg` (restyle to the template) |
| F-2 | Role decision and tier flow | none | **created**: `figures/fig2_role_tier_flow.svg` |
| F-3 | Protocol timeline (spec review → DV → F1 → T → F2 → E) | none | **created**: `figures/fig3_protocol_timeline.svg` |
| F-4 | Calibration: Type I by scenario with the nominal lines | none | **created**: `figures/fig4_calibration.svg`, labelled simulation |
| F-5 | Risk–coverage curves per method | E | NYE |
| F-6 | δ̃_r per repository with bounds (forest plot) | E | NYE |
| F-7 | Outcome-class stacked bars per tool | E | NYE |
| F-8 | Invariance heat map (operator × tool) | D2 / F1 | NYE-A / NYE |

## Metrics that must never be reported before their prerequisite

Precision, recall, F1, accuracy, harmful/undecided/unjustified rates, coverage at equal volume, AURC, κ, any p-value or bound for H1–H4 or F-A, and any "improves" or "outperforms" statement.

**Pilot numbers:** never, because they are circular. **Demo counts:** never as accuracy.

## Abstract and conclusion sentences to be completed after E (templates from the analysis plan, Sec. 8)

- "In seven pre-registered test repositories, matching each method to the same number of migration recommendations per repository, the provenance-aware analysis made correct site-level decisions [more often than / not detectably more often than] method-and-argument analysis (difference x pp, one-sided 97.5% bound y pp). [The 10-point improvement of the original hypothesis was / was not met in a pre-specified exploratory analysis.] Results describe these repositories only."
- "H2a (confirmatory): supported / not supported / not assessable [as pre-registered | at equal coverage]".
- "H2b (exploratory, pre-specified; not under family-wise error control): 10-point criterion met / not met / not assessable".
