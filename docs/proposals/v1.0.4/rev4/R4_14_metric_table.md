# R4-14 H2 primary and secondary metrics — PROPOSED, NOT ADOPTED

The frozen metric definitions (`data_dictionary.md` Sec. 4, `scoring_policy.md` v1.0) are unchanged. This table fixes which of them, and which derived quantities, answer which question, before any test access.

**Notation:**
- C_r: common evaluable set (R4-12);
- n_r = |C_r|;
- k_r: matched recommendation count;
- X, Y: frozen CORRECT indicators of the full arm (F) and the comparator (M).

## 1. Primary endpoint and confirmatory test

| Item | Definition |
|---|---|
| **Primary endpoint** | **Complete-policy correctness at equal recommendation volume:** correct-per-eligible-site (frozen "end-to-end correct per eligible site", CORRECT / sites) of each arm after within-repository matching to k_r = min(R_F,r, R_M,r) RECOMMENDs. Withdrawn RECOMMENDs are judged as ABSTAIN. |
| Contrast | δ_r = (E[ΣX] − E[ΣY]) / n_r, where E is the exact expectation over all permitted tie orders (tie-averaging, R4-11 Sec. 7) |
| **Pooling (primary)** | **repository-balanced**: δ̃ = (1/K) Σ_r δ̃_r over the 7 test repositories (K = number with n_r ≥ 1) |
| Pooling (secondary) | site-weighted: Σ n_r δ̃_r / Σ n_r. **The two are equal only if every n_r is equal.** Shortfalls or failures make them differ, and both are always printed. |
| **Confirmatory hypotheses** | H2-1 (full vs. method+args), H2-3 (full vs. method+args+recv), H2-4 (full vs. method-only); all arms at T0 (V18); H0: δ ≤ 0 vs. δ > 0 |
| Test | stratified re-matching bootstrap of δ̃ (sites within repositories, B = 10,000, seed 20261113), percentile p; coverage-gap guard (p → min(1, 2p) if g < 0.10); Holm m = 3 at one-sided family α = 0.025 (V17) |
| Claim condition | Holm rejection **and** feasibility gate passed (R4-11 Sec. 3) |
| Allowed sentence | "At equal recommendation volume, the provenance-aware arm's complete set of site decisions was correct more often than the [comparator]'s, in the 7 test repositories (δ̃ = x; one-sided 97.5% bound y)." **Not** "more accurate recommendations"; **not** "≥ 10 points"; **not** generalised beyond the 7 repositories. |

## 2. Secondary and exploratory metrics (all pre-registered; none can create a confirmatory claim)

| # | Metric | Definition / denominator | Question it answers | Status |
|---|---|---|---|---|
| S1 | **B2 margin** (H2-1) | one-sided 97.5% lower bound of δ̃ (bootstrap 2.5th percentile) compared with 0.10 | Is the H2 magnitude ≥ 10 points? | **exploratory** (V10a‴). A positive B1 never implies ≥ 10 points. |
| S2 | **matched recommendation precision** | correct RECOMMENDs / k (tie-averaged), per arm, per repository and pooled; difference F − M with a bootstrap percentile CI | How accurate are the recommendations that each arm keeps at equal volume? | descriptive |
| S3 | frozen recommendation correctness | CORRECT / (eligible DETERMINATE sites with RECOMMEND), per arm, natural and matched | as defined in the data dictionary | descriptive |
| S4 | natural recommendation precision | correct RECOMMENDs / R_A, per arm | the same at the arm's own coverage | descriptive |
| S5 | **natural-coverage comparison** | correct-per-eligible-site without matching, on C_r; δ_nat; exact McNemar | Which complete policy is more often correct as deployed (coverage differences included)? | secondary; protocol v1.0.3's Experiment B/H2 McNemar, kept |
| S6 | decomposition | δ̃ split by final action: REC, WITHDRAWN, FLAG, ABSTAIN, NO_FINDING | Where does the matched difference come from? | required, descriptive |
| S7 | harmful / undecided / unjustified rates | per scoring policy, natural and matched, per arm | safety profile at both coverages | descriptive |
| S8 | **ranking-free matching** | δ̃ with withdrawal uniformly at random over all of the withdrawing arm's RECOMMENDs (tiers ignored; exact average) | What is the difference without the arm's own tier ranking? Primary − ranking-free = the value of the ranking. | pre-registered sensitivity |
| S9 | primary-seed per-site table | matching with tie seed `20261113`: binary X/Y per site, b, c, site-level exact McNemar and Tango | site-level illustration; paired tests (valid but conservative under matching) | secondary |
| S10 | 100-seed distribution | δ for seeds `20261113-S001…S100`: median, minimum, maximum, histogram | How much do tie-breaks move a single seeded estimate? | sensitivity |
| S11 | fixed-target matching (V12-B) | target ⌊c_DV·n_r⌋ where both arms reach it | Is the result robust to the matching target? | secondary |
| S12 | feasible repositories only | primary analysis restricted to repositories with k_r ≥ 5 | robustness to low-coverage repositories | descriptive |
| S13 | execution-failure sensitivity | S-F1 and S-F2 (R4-12) | Do failures change the picture? | pre-registered sensitivity |
| S14 | proposed system (H2-S) | full at T2 vs. method+args at T0, matched | the deployed system against the comparator | secondary |
| S15 | repository-level generalisation | all 7 δ̃_r; leave-one-repository-out; one-sided t (df = 6); sign-flip; Wilcoxon | Would the effect plausibly extend beyond these repositories? | exploratory (V13′) |
| S16 | cluster bootstrap by repository | protocol v1.0.3 Sec. 5 ("cluster bootstrap … by repo") | v1.0.3's planned CI | **exploratory only**, labelled "7 purposively chosen repositories; not a valid population CI" (R4-04) |
| S17 | strict scoring | all of the above under the strict variant | robustness to unsafe drop-in wording | pre-registered sensitivity (scoring policy Sec. 3) |

## 3. Required per-repository report (each comparison)

Generated by `matching_ref_v4.evaluate_repository`; layout in `results/worked_example_v12pp.md` and `results/pilot_v12pp.md`.

| Field | Field |
|---|---|
| eligible sites \|E_r\| | common evaluable sites n_r |
| execution failures per arm; both / F only / M only / neither | indeterminate sites (common and eligible) |
| natural RECOMMEND counts R_F, R_M | natural coverage F, M |
| matched count k_r and matched coverage | withdrawn per arm; boundary tier; withdrawn of tied |
| recommended after matching: both / F only / M only | correct and incorrect (harmful) per arm, natural and matched |
| complete-policy correctness per arm (natural, matched) | δ̃_r (primary), primary-seed δ_r, 100-seed min / median / max, ranking-free δ̃_r, natural δ_r |
| recommendation precision per arm, natural and matched | failure sensitivities S-F1, S-F2 |
| matching-feasible (k_r ≥ 5) | decomposition by final action |

**Pooled:**
- δ̃, repository-balanced and site-weighted;
- the signed coverage gap g and the guard state;
- the gate (pooled matched coverage, number feasible);
- raw and guarded p, the Holm-adjusted p;
- the one-sided 97.5% bound;
- the margin bound (H2-1).
