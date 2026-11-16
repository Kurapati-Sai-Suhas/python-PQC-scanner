# R4-11 Final V12″ audit: validation and integration with the H2 design — PROPOSED, NOT ADOPTED

Prepared 15 Nov 2026 in response to the owner's final R4-03 follow-up.

**Unchanged and in force:**
- protocol v1.0.3;
- annotation guide v1.0;
- scoring policy v1.0;
- production code.

**Safeguards:**
- Nothing is committed.
- No test-split repository was accessed.
- Annotation, F1, F2 and E have not started.
- Development evidence used: only the already-labelled pilot (circular) and the code itself.

**Earlier R4-03 documents** are preserved in `superseded/`.

**Evidence:**
- **Tests:** 82 pass (`results/unit_tests_v12pp.txt`): 27 statistics tests, 29 matching tests and 26 V12″ tests.
- **Simulations:** planning figures under an assumed model, not results.
- **Pilot figures:** circular development data.

**Verdict: V12″ — APPROVE WITH MODIFICATION** (Sec. 10, as decisions V12″, V12″-E, V13″, V18′, V20–V24 in R4-15).
- The method measures complete-policy correctness at equal recommendation volume defensibly, for the 7 fixed repositories.
- The modifications: execution-failure rules; an exact guard definition; the exact tie-average point estimate; a random-key bootstrap (not a tie-averaged one); explicit gate consequences; T0 for all H2 arms; renamed IDs; two pre-test amendments of v1.0.3.

## 1. Deliverables

| Requested | File |
|---|---|
| final V12″ audit report | `R4_11_v12pp_final_audit.md` (this file) |
| updated matching methodology | `R4_03_coverage_matching.md`; algorithm `R4_03a_matching_implementation_spec.md` |
| execution-failure specification | `R4_12_execution_failure_spec.md` |
| updated calibration report | `R4_13_calibration_report_v12pp.md`; raw `results/calib_v12pp.*`, `results/family_v12pp.md` |
| updated worked example | `R4_03b_worked_example.md` Sec. 9; three-repository example `results/worked_example_v12pp.md`; pilot `results/pilot_v12pp.md` |
| primary and secondary metric table | `R4_14_metric_table.md` |
| updated owner decisions | `R4_15_owner_decisions_v12pp.md` |
| protocol consistency matrix | `R4_16_protocol_consistency_matrix.md` |
| tests | `scripts/test_v12pp.py` (26 new); existing `test_matching_ref_v4.py` (29) and `test_stats_v4.py` (27) still pass |
| scripts | `scripts/matching_ref_v4.py` (extended), `calib_v12pp.py`, `sim_family_v12pp.py`, `worked_example_v12pp.py` |

## 2. Failed-execution handling (R4-12)

**Code finding.** `pqscan/bench/run.py` (`judge_ours`) parses each file once and derives every Module C arm from the same evidence. A pqscan EXECUTION_FAILURE arises only when a file cannot be read or parsed. **For the H2 arms, failure is therefore always concordant:** a site fails for both arms or for neither.

**Bias.**
- **Between the arms:** excluding the failed sites cannot bias the comparison, because the same sites leave both arms. They also have no RECOMMEND, so k_r is unchanged.
- **The estimand does shift.** It becomes "sites in files the analyser can parse". Parse failures concentrate in legacy (Python-2), generated, very deeply nested or badly encoded files, which may hold older cryptographic idioms.
- **For external tools (F-A),** failures differ by tool and can bias heavily.

**Definitions:**
- **Eligible set E_r:** every site is always reported.
- **Common evaluable set C_r:** the primary H2 denominator.
- **Per-arm failure sets** and the four-way partition: both ran / F only / M only / neither.
- **Per-arm n_exec:** the frozen rate denominator.

**Sensitivity analyses:**
- **S-F1** (failures scored not correct on |E_r|): for H2 a pure rescaling, δ̃·n_r/|E_r|.
- **S-F2:** extreme bounds.

**Wording triggers:** 5% pooled or 10% in any repository.

**A discordant failure in an H2 comparison stops the run** as a software defect.

**Coexistence with the frozen rules:**
- EXECUTION_FAILURE stays its own judgment; rates stay on n_exec.
- The paired analysis uses both-ran sites (scoring policy Sec. 5; protocol Sec. 5).
- Nothing is rescored. S-F1 and S-F2 are additional, labelled analyses.

## 3. Feasibility gate and repository shortfalls (V21)

The proposed conditions are verified in code (`feasibility`) and tested (`test_gate_cases`):
- a repository is feasible iff k_r ≥ 5;
- the gate passes iff Σk/Σn ≥ 0.20 (an exact fraction) **and** at least 5 of the 7 repositories are feasible.

| Situation | Rule |
|---|---|
| Every repository still contributes? | **Yes.** All repositories with n_r ≥ 1 enter δ̃ with weight 1/K. None is removed for low coverage. |
| Zero matched coverage (k_r = 0) | δ̃_r is computed: the difference from FLAG_NO_TARGET, own abstentions and withdrawals only (worked example, repository C: +1/6 with no recommendation). The repository is reported as "matched coverage 0, not feasible". |
| A repository with no common evaluable site (all failed) | δ̃_r is undefined. It is listed with its failure counts and counted as not feasible; K becomes the number of repositories with n_r ≥ 1, printed with the estimate. |
| Fewer than 5 feasible, or pooled < 0.20 | **The gate fails.** The comparison's guarded p is still computed and reported, but **H2 is "not assessable at equal coverage"** for that comparison: no "H2 supported" statement can rest on it. |
| Repository-specific reporting | The full field list of R4-14 Sec. 3 for every repository, including non-feasible ones, plus all 7 δ̃_r values with per-repository bootstrap intervals (exploratory) |
| When fixed | Now, before test access. The Phase DV check (6 development/validation repositories, label-free k_r) only decides whether the design is viable before F1. It does not tune the thresholds. |

**Why the gate cannot inflate error.** It only removes claims. In the family runs, the "claims" FWER is always ≤ the plain FWER (Sec. 4).

## 4. Coverage-gap guard and validity of the complete procedure (V20, V13″)

**Definition.** g = C_full − C_comparator = (1/K) Σ_r (R_F,r − R_M,r)/n_r. It is computed on natural outputs over the common evaluable sets, repository-balanced like the estimand, and held as an exact fraction (`coverage_gap`).

| g | Guard | Example (tested in `test_guard_boundaries`) |
|---|---|---|
| < 0 (comparator covers more) | **active** | R = (2, 5) of 30 → g = −1/10 |
| = 0 | **active** | (3, 3) of 30 |
| 0 < g < 0.10 | **active** | (5, 3) of 30 → 1/15 |
| = 0.10 exactly | **not active** | (9, 6) of 30; or two repositories with (21, 0) and (0, 15) of 30 → (0.7 − 0.5)/2 = 1/10 |
| > 0.10 | not active | (10, 6) of 30 → 2/15 |

When the guard is active, p becomes min(1, 2p) before Holm.

**Why the correction is defensible:**
- **Pre-registered and label-free.** g is a function of tool outputs only, fixed before test access.
- **One-directional.** Doubling p shrinks the rejection region and can never raise an error rate.
- **Aimed at the known cause.** It targets the region where the matched functional min(p_F, p_M) is non-differentiable. That is the known failure mode of the bootstrap, observed as about 1.7× inflation at a and 1.8× at a/3.
- **Sized from evidence.** A factor of 2 covers every tested cell.

It is an **empirically sized** correction, **not a proven bound**.

**The complete procedure was simulated.** The steps were:
1. natural coverage;
2. guard;
3. matching;
4. tier withdrawal;
5. ties (exact tie-average point estimate; random keys in the bootstrap);
6. frozen-model scoring;
7. re-matching bootstrap;
8. Holm.

Results (R4-13):

| Check | Result (MC SE) |
|---|---|
| 17 fixed-repository scenarios, all three Holm levels | worst 0.0191 at a, 0.0093 at a/2, 0.0061 at a/3. All at or below nominal, including the previous failure case S04 (unguarded 0.0420). |
| 8 near-kink gaps | worst 0.0092 at a/3 (+1.0 SE above 0.0083) and 0.0125 at a/2 (= nominal), both at d = 0; 0.0213 at a |
| Generalisation (random repositories) | 0.0415: **invalid**, as expected (V13′) |
| Power, the same 18 scenarios at δ ≈ +0.05 | 0.11–0.34 at a where the gate passes (low by design) |
| **Holm family, 8 null and partial-null configurations, correlated comparisons** | FWER at most 0.0121 (Sec. 4a) |

**A variant was tested and rejected.** Bootstrapping the exact tie-averaged estimate itself (TA) is liberal: 0.0293 at a in the flat-tier scenario, and 0.0283 near equal coverage with the guard. The bootstrap must therefore keep random tie keys inside each resample.

**Empirical calibration ≠ proof.** No universal error control is claimed. The figures cover only the modelled range: about 30 sites × 7 repositories, random site sampling within repositories, error-free labels, and deterministic arms.

### 4a. Family-wise error (Holm m = 3; RK + guard)

| Config | Description | True nulls (H2-1, H2-3, H2-4) | FWER, RK + guard (MC SE) | RK, no guard | RK claims (gate) | TA + guard |
|---|---|---|---|---|---|---|
| C1 | global null; comparator coverages 0.40 / 0.58 / 0.36 | all null | 0.0044 (0.0007) | 0.0045 | 0.0044 | 0.0074 |
| C2 | global null; H2-3 comparator at equal coverage | all null | 0.0072 (0.0008) | 0.0115 | 0.0072 | 0.0136 |
| C3 | global null; strong dependence (rho 0.9) | all null | 0.0028 (0.0005) | 0.0028 | 0.0028 | 0.0055 |
| C4 | H2-1 null; H2-3 and H2-4 true delta +0.08 | null, alt, alt | 0.0059 (0.0008) | 0.0059 | 0.0059 | 0.0107 |
| C5 | H2-3 null at equal coverage; others +0.08 | alt, null, alt | 0.0121 (0.0011) | **0.0237** | 0.0121 | 0.0175 |
| C6 | global null; low comparator coverage | all null | 0.0059 (0.0008) | 0.0059 | 0.0001 | 0.0087 |
| C7 | global null on average; fixed heterogeneity (tau 0.015) | all null | 0.0037 (0.0006) | 0.0038 | 0.0037 | 0.0071 |
| C8 | H2-1 comparator above the full arm's coverage; others +0.08 | null, alt, alt | 0.0115 (0.0011) | **0.0223** | 0.0115 | 0.0174 |

**Family results** (10,000 data sets per configuration, B = 1,000; `results/family_v12pp.md`):
- **With the guard,** the family-wise error is **at most 0.0121** in every configuration, against 0.025. That covers global nulls, partial nulls, strong dependence, equal and inverted coverage, low coverage and heterogeneity.
- **Without the guard,** the two configurations where a true null sits at or beyond equal coverage come close to the limit (0.0237 and 0.0223). The guard therefore matters for the family, not only for single tests.
- **Claims never exceed rejections.** The claims FWER is always at most the FWER; in C6 the gate removes almost every claim (0.0001).
- **Power with Holm** at true delta +0.08 is 0.28–0.60 per false null.


## 5. Primary estimand and reporting (R4-14)

**Primary endpoint:** complete-policy correctness at equal recommendation volume, as δ̃ = (1/K) Σ_r δ̃_r. Recommendation precision is kept separate:
- matched precision (tie-averaged) and natural precision;
- the frozen "recommendation correctness".

**Every repository reports:**
- eligible sites and common evaluable sites;
- the natural counts R_F and R_M and the coverages;
- k_r;
- overlap, both / F-only / M-only;
- withdrawn recommendations;
- correct and incorrect decisions;
- complete-policy correctness;
- precision, natural and matched;
- execution failures;
- indeterminate counts.

A generator exists (`evaluate_repository`); see the three-repository example and the pilot tables.

**Weighting:**
- **Repository-balanced is primary** (1/K each).
- **Site-weighted** (Σ n_r δ̃_r / Σ n_r) **is always printed as well.** They coincide only if every common n_r is equal. Shortfalls and failures make them differ: example +0.0972 vs. +0.1042, unit test `test_repository_and_site_weighting_differ_with_unequal_denominators`.
- **Consistency.** The bootstrap uses the same weighting as the estimate. The guard uses the repository-balanced gap; the gate uses site-weighted pooled coverage, because it measures how many recommendations exist overall.

## 6. Evidence-tier asymmetry

**Tier distribution of RECOMMENDs on the pilot** (T0, development, circular; `results/pilot_v12pp.md`):

| Arm | RECOMMEND | T0 | T1 | T2 | T3 |
|---|---|---|---|---|---|
| full | 23 | 0 | 0 | 15 | 8 |
| method+args | 13 | 1 | 12 | 0 | 0 |
| method+args+recv | 13 | 0 | 0 | 13 | 0 |
| method-only | 13 | 12 | 1 | 0 | 0 |

**Structural advantage?**
- Only the withdrawing arm's own order is used, so tiers are never compared across arms.
- The full arm has up to four levels; method+args and method-only effectively have one or two; method+args+recv had a single level (T2) on the pilot.
- When the full arm withdraws, it can drop its least-evidenced recommendations first. That is an advantage, but it is the *capability being tested*: provenance evidence that tells the tool where its evidence is weak.
- When a comparator must withdraw (S05; near-kink cells), its coarse tiers make the withdrawal close to random. That is its own limitation, not a bias of the rule.
- The guard covers the statistical side of these cases.

**Which question each variant answers:**

| Variant | Question | Pilot H2-1 (δ̃) | Worked example (δ̃) |
|---|---|---|---|
| **tier-ordered matching (primary)** | Which complete policy is more often correct when each arm keeps its best-evidenced recommendations? | +0.059 | +0.125 |
| **ranking-free** (uniformly random withdrawal, exact average) | Which policy is better if the kept recommendations were a random subset? This is the base quality of the arm's recommendations at equal volume. | +0.059 | +0.010 |
| difference | **the value of the arm's own evidence ranking** | 0 (all pilot recommendations correct) | +0.115 |
| primary-seed table | one concrete tie order (per-site table, McNemar) | +0.059 | +0.083 |
| 100 seeds | how much a single tie order can move the estimate | min = max = +0.0588 | +0.083 to +0.167 |

**No tier ordering is tuned on labels.** The order T0 < T1 < T2 < T3 is fixed by the frozen data dictionary. The ranking-free variant uses no tiers at all.

## 7. Exact tie-averaged estimate (V12″-E; your provisional preference, adopted)

- **Feasibility.** Exact and cheap.
  - δ_r is linear in the withdrawal indicators.
  - Under a uniformly random choice of j of the m tied recommendations, each is withdrawn with probability j/m.
  - So E[δ_r] needs no enumeration: O(n) per repository (`tie_average_delta`; vectorised `tie_average_batch`).
  - It is verified against brute-force enumeration of every permitted withdrawal order (`test_tie_average_equals_brute_force_over_all_orders`, both tier-ordered and ranking-free) and against the per-site reference on bootstrap resamples.
- **Must the bootstrap also average over tie orders?** It must account for them, **but by randomising, not by exact averaging.**
  - Random keys inside each resample average over tie orders in distribution and are calibrated (Sec. 4).
  - Exact averaging inside resamples (TA) is liberal (0.0293).
  - So the decision uses the RK bootstrap, and the point estimate reported with it is δ̃.
- **Is the p-value invariant to the tie seed?** **Yes, exactly.** The primary analysis contains no observed tie order at all:
  - δ̃ is an expectation;
  - the bootstrap draws its own keys from the bootstrap generator (seed 20261113, fixed).
  - The only remaining randomness is Monte Carlo error from B, controlled by the B = 100,000 rule.
  - Unit tests: `test_bootstrap_p_does_not_depend_on_the_observed_tie_break_seed`, `test_bootstrap_ta_deterministic_and_has_no_tie_randomness`.
- **What the 100-seed analyses still do.** They are retained, unchanged, as sensitivity: the distribution of the seeded estimate δ(seed) and of the site-level McNemar p. They show how much a single arbitrary tie order would have moved the result. Seed `20261113` builds the binary per-site table.
- **No seed is selected for its result,** and no seed can change the confirmatory decision.

## 8. Integration with R4-02 and the H2 design (R4-16)

Every H2 element was cross-checked across v1.0.3, R4-02, R4-03/03a, R4-05/R4-07 and R4-06 (26 rows). After V18′ fixes **T0 for all H2 arms** (H2-1, H2-3, H2-4; H2-S full at T2 vs. method+args at T0), the tested arms and thresholds agree across documents.

**Edits required after approval:**
- V18 had left H2-3 and H2-4 without thresholds.
- The IDs B1–B4 collide with the code's baseline names (V23).
- R4-02's "repository-balanced = site-weighted" holds only with equal common n_r.
- Guard, gate, failures and δ̃ must be added to R4-02, R4-06 and R4-07.

**Two departures from frozen v1.0.3 text,** both pre-test amendments with stated consequences (V24):
- the H2 McNemar becomes secondary;
- the cluster-by-repository bootstrap CI becomes exploratory only.

**Distinctions fixed for reporting:**

| Quantity | Status | May be claimed as |
|---|---|---|
| positive matched difference (H2-1, H2-3, H2-4) | **confirmatory** (Holm, guard, gate) | "more site decisions correct at equal recommendation volume, in these 7 repositories" |
| 10-point margin (H2-1) | **exploratory** (RK lower bound vs. 0.10) | "the estimated improvement is / is not above 10 points (exploratory)". **A positive B1 result never implies ≥ 10 points.** |
| natural-coverage comparison | secondary | difference as deployed, coverage effects included |
| matched-coverage comparison | primary | as above |
| recommendation precision (natural, matched) | descriptive with CIs | "of the recommendations each arm kept, x% vs. y% were correct". No test, no H2 claim. |
| complete-policy correctness | primary endpoint | — |

## 9. What remains uncertain

1. **Real arm behaviour on the test repositories is unknown.** The pilot is circular, with 100% recommendation precision for both arms, so the matched effect there is driven by FLAG_NO_TARGET alone.
2. **Calibration covers one generative family.** The guard's factor of 2 is empirical, and the strict Holm step sits at nominal within MC error at exactly equal coverage.
3. **Label error is not modelled.** There is a single annotator.
4. **Power is low** for small complete-policy differences, about 0.11–0.34 at δ = +0.05. The margin is essentially untestable.
5. **Parse-failure prevalence on the test repositories is unknown.** It decides how far the "parseable files" qualification matters.
6. **Production code must reproduce every reference result** and re-run R4-13 before F1.

## 10. Exact V12″ (final) recommendation

> **V12″ (final).** For H2-1, H2-3 and H2-4 (V18′: full vs. method+args, method+args+recv and method-only, all at T0) and the secondary H2-S:
>
> **(a) Paired set.** The common evaluable set C_r per R4-12. Failures are reported, analysed (S-F1, S-F2) and must be concordant.
>
> **(b) Matching.** k_r = min(R_F,r, R_M,r). The larger arm withdraws lowest tier first, SHA-256 order within a tier. Withdrawn → ABSTAIN under the frozen judge. Label-free, hashed before scoring.
>
> **(c) Endpoint.** Complete-policy correctness at equal recommendation volume. Point estimate δ̃: the exact tie-average, repository-balanced; the site-weighted value is also reported. Precision and decomposition are reported separately (R4-14).
>
> **(d) Test.** Stratified re-matching percentile bootstrap with random tie keys in each resample (B = 10,000, seed 20261113). Guard: if g = (1/K) Σ (R_F − R_M)/n_r < 1/10 (exact), then p → min(1, 2p). Holm m = 3 at one-sided family α = 0.025. B = 100,000 rule.
>
> **(e) Gate.** Feasible repository iff k_r ≥ 5. The claim requires Σk/Σn ≥ 0.20 and ≥ 5 of 7 feasible. Otherwise "not assessable at equal coverage". No repository is excluded. Phase DV check before F1.
>
> **(f) Margin.** Exploratory: the RK one-sided 97.5% bound vs. 0.10.
>
> **(g) Seeds.** There is no tie seed in the primary analysis. Seed 20261113 drives the bootstrap generator and the per-site table. Sensitivity seeds S001–S100 are reported as a distribution.
>
> **(h) Secondary analyses** as listed in R4-14.

## 11. Decisions to approve (R4-15)

**Approve:**
- V12″, V12″-E, V13″, V20, V21, V22;
- V18′, V10a‴′, V10b‴;
- V23 (IDs), V24 (v1.0.3 amendments).

**Reject:** the TA bootstrap variant and the unguarded test.

**Unchanged:** V17 and every non-H2 decision.

## 12. Answers

- **Does it defensibly measure complete-policy correctness at equal coverage?** **Yes,** for the 7 fixed repositories, under the assumptions in Sec. 9: equal recommendation counts, a common denominator, the frozen judge, label-free matching and a calibrated test.
- **What it can claim about recommendation precision:** only descriptive estimates with intervals. Precision is not the H2 endpoint and is not tested.
- **Are the bootstrap and guard adequately validated?**
  - Empirically, yes, across 18 + 8 single-comparison scenarios and the Holm family (Sec. 4, 4a): every single-comparison error rate is at or below nominal everywhere it was tested, except a +1 MC-SE excursion at one Holm step at exactly equal coverage, and the family-wise error is at most 0.0121.
  - There is no mathematical proof.
  - It must be re-run on production code.
- **What remains uncertain:** Sec. 9.
- **Which decisions to approve:** Sec. 11.
