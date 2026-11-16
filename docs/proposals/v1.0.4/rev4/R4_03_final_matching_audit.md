# R4-03 final audit: equal-coverage matching and its statistical validity — PROPOSED, NOT ADOPTED

Prepared 14 Nov 2026, in response to the owner's R4-03 audit request.

**Unchanged and in force:**
- protocol v1.0.3;
- annotation guide v1.0;
- scoring policy v1.0;
- all production code.

**Safeguards:**
- No test-split repository was accessed.
- Nothing is committed.
- Annotation, F1, F2 and E have not started.
- The reviewed R4-03 is preserved unchanged as `superseded/R4_03_coverage_matching_as_reviewed.md` (identical SHA-256).

**Evidence for every claim below** comes from the scripts in `scripts/` and their outputs in `results/`:
- 56 tests pass (`results/unit_tests_matching.txt`): the 27 revision-4 statistics tests and 29 new matching tests.
- **Simulated figures are planning figures under an assumed model, not results.**
- **Pilot figures are circular development data, not results.**

**Verdict: V12′ — APPROVE WITH MODIFICATION (V12″, Sec. 10).** The matching rule is label-free, achieves exactly equal recommendation counts, and keeps a valid paired design on a common denominator. Three problems must be fixed before it is adopted:
1. **What it measures was mis-described.** The matched correct-per-eligible-site difference measures the *complete decision policy*, not migration-recommendation accuracy (Sec. 3).
2. **No feasibility criterion existed.** k_r can be 0 (Sec. 4).
3. **The specified bootstrap is liberal near equal natural coverage.** Its error rate is up to 0.042 at a nominal 0.025 (Sec. 6). A pre-registered, label-free guard fixes this in every simulated case.

## 1. Deliverables

| Item | File |
|---|---|
| This audit (verdict, V12″ text, affected sections) | `R4_03_final_matching_audit.md` |
| Updated R4-03 | `R4_03_coverage_matching.md` (reviewed version in `superseded/`) |
| Matching implementation specification | `R4_03a_matching_implementation_spec.md` |
| Numerical worked example (manual calculation) | `R4_03b_worked_example.md`; generated check `results/worked_example_v4.md` |
| Bootstrap calibration report | `R4_03c_bootstrap_calibration_report.md`; raw `results/calib_matching.*`, `results/calib_nearkink.*` |
| Frozen scoring table (generated from `judge`) | `results/scoring_table_v4.md` |
| Pilot (development) demonstration | `results/pilot_matching_v4.md` |
| Reference implementation (not production) | `scripts/matching_ref_v4.py` |
| Unit tests (29) | `scripts/test_matching_ref_v4.py` |
| Validation and calibration scripts | `scripts/calib_matching_v4.py`, `scripts/calib_nearkink_v4.py`, `scripts/worked_example_v4.py` |

## 2. What "equal coverage" means, checked against the frozen specification

| Claim | Frozen source | Verdict |
|---|---|---|
| Coverage = RECOMMEND / eligible sites | `data_dictionary.md` Sec. 4 ("Coverage = (RECOMMEND) / eligible sites") | **matches.** FLAG_NO_TARGET and ABSTAIN are not coverage. |
| The denominator is the eligible sites where the method ran; paired comparisons use sites where both ran | `scoring_policy.md` Sec. 5 | **matches,** once sites with EXECUTION_FAILURE in either arm are removed before matching (R4-03a Sec. 2). This was missing from R4-03. |
| The H2 metric is correct-per-eligible-site | H2 wording; `data_dictionary.md` Sec. 4 ("End-to-end correct per eligible site = CORRECT / eligible sites") | **matches** |
| k_r = min(R_F, R_M); the higher arm withdraws its lowest tiers first | not in the frozen documents: it is the H2 operationalisation (V12′). It is consistent with the frozen RQ3 risk–coverage curve, which varies coverage by tier threshold. | acceptable as a pre-registered operationalisation, **not** a scoring change |
| A withdrawn RECOMMEND becomes ABSTAIN | not in the frozen documents. The frozen `judge` is applied unchanged to the modified action. | acceptable; must be described as an operationalisation |

**Clarifications required by the owner, all now in R4-03a:**
1. **Counts are equal, not sites.** After matching, both arms have exactly k_r RECOMMENDs in every repository. The recommended **sites** generally differ. In the worked example both arms recommend on 5 of 12 sites but share only 2 (R4-03b Sec. 3).
2. **One common denominator.** Both arms are scored over the same complete paired set of eligible sites.
3. **No labels.** Matching reads only site IDs, actions and tiers. The unit test `test_matching_ignores_labels` varies the labels and checks that the withdrawal is unchanged. Production must hash the label-free matching output before scoring.
4. **Withdrawn means ABSTAIN.** The frozen judge then scores it.
5. **Independent units.** Matching is per repository and per comparison.

**Estimand.** Fixed repositories r = 1..7. For arm A let p_A,r be its natural coverage and c*_r = min(p_F,r, p_M,r). E_A,r(c) is A's expected correct-per-eligible-site after its lowest-tier recommendations are withdrawn down to coverage c, uniformly within the boundary tier. Then

δ = (1/7) Σ_r [E_F,r(c*_r) − E_M,r(c*_r)].

The sample statistic is the matched difference on the 30 sampled sites. Its finite-sample bias was small in the simulations (|bias| ≤ 0.009, against an SD of about 0.035), except at equal natural coverage (+0.0095; Sec. 6).

**The scientific question it answers.** If each method may make the same number of migration recommendations in a repository, choosing where by its own evidence ranking, whose complete set of site decisions is more often correct?
- A "site decision" here is: recommend a target, flag no target, or abstain.

**It does not answer:**
- **"Is the full arm's recommendation more accurate on the same sites?"** Recommended sites differ between the arms.
- **"How accurate are each arm's migration recommendations?"** That is matched precision, Sec. 3.3.

**Equal recommendation rate vs. identical accepted sites.**
- Forcing identical accepted sites (scoring only sites both arms recommend on) would compare accuracy on the comparator's easy cases. It would discard every site where the evidence differs, which is exactly what H2 is about.
- Equal rate with different sites is the standard selective-classification comparison: risk at equal coverage, each method using its own confidence ordering.

## 3. Scoring consequences (frozen; nothing altered)

### 3.1 Complete table

Generated by calling `pqscan.bench.judge.judge` for every action × ground-truth combination (`results/scoring_table_v4.md`). **Bold** = counts as correct.

| Ground truth (expected class) | REC SIG | REC KEM | REC DUAL | REC PQC_ALREADY | FLAG_NO_TARGET | ABSTAIN | NO_FINDING | EXEC_FAILURE |
|---|---|---|---|---|---|---|---|---|
| SIGN/VERIFY, determinate (SIG) | **CORRECT** | INCORRECT/ROLE_INCOMPATIBLE | UNDECIDED | INCORRECT/FALSE_ASSURANCE | DETECTED_ONLY | UNASSESSABLE | MISSED | EXEC_FAILURE |
| KE/PK_*, determinate (KEM) | INCORRECT/ROLE_INCOMPATIBLE | **CORRECT** | UNDECIDED | INCORRECT/FALSE_ASSURANCE | DETECTED_ONLY | UNASSESSABLE | MISSED | EXEC_FAILURE |
| KEY_MATERIAL_ONLY / PROTOCOL_CONFIG (NONE) | INCORRECT/OVER_REC. | INCORRECT/OVER_REC. | UNDECIDED | INCORRECT/FALSE_ASSURANCE | **CORRECT** | UNASSESSABLE | MISSED | EXEC_FAILURE |
| approved hybrid component (NONE) | INCORRECT/OVER_REC. | INCORRECT/OVER_REC. | UNDECIDED | **CORRECT** | **CORRECT** | UNASSESSABLE | MISSED | EXEC_FAILURE |
| INDETERMINATE (ABSTAIN) | UNJUSTIFIED | UNJUSTIFIED | UNDECIDED | INCORRECT/FALSE_ASSURANCE | DETECTED_ONLY | **CORRECT** | MISSED | EXEC_FAILURE |
| UNKNOWN recorded as determinate (ABSTAIN) | UNJUSTIFIED | UNJUSTIFIED | UNDECIDED | INCORRECT/FALSE_ASSURANCE | DETECTED_ONLY | **CORRECT** | MISSED | EXEC_FAILURE |
| ineligible (N/A) | FALSE_POSITIVE_SITE | … (every reported action) | | | | | N/A | EXEC_FAILURE |

### 3.2 Each action on DETERMINATE vs. INDETERMINATE sites

| Action | DETERMINATE | INDETERMINATE |
|---|---|---|
| **RECOMMEND** | correct only for the expected family (or "already PQC" on a hybrid); otherwise INCORRECT (harmful) or UNDECIDED | never correct: UNJUSTIFIED, UNDECIDED, or INCORRECT/FALSE_ASSURANCE |
| **ABSTAIN** | UNASSESSABLE (not correct, not harmful) | CORRECT |
| **FLAG_NO_TARGET** | correct only where the expected class is NONE; otherwise DETECTED_ONLY | DETECTED_ONLY |
| **NO_FINDING** | MISSED | MISSED |
| **EXECUTION_FAILURE** | excluded from the paired set | excluded from the paired set |

Two further points:
- Expected NONE (inventory or hybrid) takes precedence over INDETERMINATE in `expected_class`.
- The Module C arms emit only SIG or KEM recommendations, never DUAL or PQC_ALREADY (`judge.our_action`). The DUAL and PQC_ALREADY columns matter only for external tools, which are not matched.

**What a withdrawal does** (a RECOMMEND turned into ABSTAIN):

| Withdrawn recommendation was | Site | Becomes | Change in correct | Change in harmful |
|---|---|---|---|---|
| CORRECT | determinate | UNASSESSABLE | **−1** | 0 |
| INCORRECT (role-incompatible, false assurance, over-recommendation) | determinate | UNASSESSABLE | 0 | −1 |
| UNDECIDED | determinate | UNASSESSABLE | 0 | 0 |
| UNJUSTIFIED or UNDECIDED | indeterminate | CORRECT | **+1** | 0 |
| INCORRECT/FALSE_ASSURANCE | indeterminate | CORRECT | **+1** | −1 |

**Withdrawal can improve correctness.** Withdrawal raises the withdrawing arm's correctness exactly when the withdrawn recommendation sat on a site whose expected class is ABSTAIN. It lowers it exactly when the recommendation was correct. The matched comparison therefore credits an arm whose lowest-evidence recommendations are concentrated on undecidable sites.
- That credit is legitimate selective-abstention value.
- It is available only to the arm that withdraws, normally the full arm.
- Worked example site s10 (R4-03b): an UNJUSTIFIED T1 recommendation, once withdrawn, becomes CORRECT.

### 3.3 Why this measures the complete policy, and what to report

Split δ by the action each arm finally took (R4-03a Sec. 5):
- with equal counts k, the recommendation part is δ_REC = (k/n)(precision_F − precision_M);
- the rest comes from FLAG_NO_TARGET, own abstentions, and withdrawals that became correct abstentions.

**Pilot evidence** (development data, circular; `results/pilot_matching_v4.md`):

| | Natural coverage | Correct-per-eligible (natural) | Correct-per-eligible (matched) |
|---|---|---|---|
| full at T0 | 23/30 = 0.767 | 30/30 | 20/30 |
| method+args at T0 | 13/30 = 0.433 | 18/30 | 18/30 |
| difference | | **+0.400** | **+0.067** |

- After matching, both arms' 13 recommendations are all correct, so the recommendation part is exactly 0.
- The whole +0.067 comes from the full arm's correct FLAG_NO_TARGET on two KEY_MATERIAL_ONLY sites, where method+args abstains (UNASSESSABLE).
- The worked example shows the same pattern: matched precision is 4/5 for both arms, and δ = +1/12 comes from one FLAG.

**Consequences (part of V12″):**
1. **Reporting language.** H2's matched result is reported as "correct-per-eligible-site at equal recommendation count (complete decision policy)", never as "recommendation accuracy".
2. **Required report for every comparison:**
   - the decomposition (REC, WITHDRAWN, FLAG, ABSTAIN, NO_FINDING);
   - matched precision (correct RECOMMENDs / k) per arm;
   - the frozen "recommendation correctness" (CORRECT / determinate sites with RECOMMEND) per arm;
   - the harmful, undecided and unjustified rates after matching.
3. **The margin is bounded by coverage.** The recommendation part cannot exceed the matched coverage: |δ_REC| ≤ c*. At the pilot's c* = 0.43, B2's 10-point margin needs a precision gap of about 23 points if it is to come from recommendations at all. That is stated in R4-02's B2 text as a feasibility fact, not a change of margin.
4. **Strict scoring.** The pre-registered strict variant is applied after matching in the same way. A withdrawn drop-in-worded KEM recommendation loses its UNSUPPORTED_DROP_IN harm.

## 4. Minimum matched-coverage feasibility

**What happens at k_r = 0.**
- If one arm makes no recommendation in r, the other withdraws all of its recommendations.
- Both arms then differ only through FLAG_NO_TARGET and abstention, so δ_r measures no recommendation at all.
- The design stays valid. In simulation S06 (k_r = 0 in 22.5% of repositories) the error rate was 0.0155; in S07 (two repositories always 0) it was 0.0135.
- But the result answers a different question. Power also collapses: with a 15-point precision gap, power at a/3 is 0.01 at c* = 0.05 and 0.07 at c* = 0.10 (R4-03c Sec. 7).

**Development information** (pilot: paramiko, python-jose; circular):
- per-repository matched coverage 7/17 = 0.41 and 6/13 = 0.46;
- pooled 13/30 = 0.43;
- both repositories had k_r ≥ 6.

There is no Phase DV tool output yet, and none was generated: it would expose tool behaviour to the owner before Phase DV labelling.

**Proposed criterion, fixed now and never changed after test access.** It is label-free and evaluated per comparison.

| Element | Rule | Justification |
|---|---|---|
| Matching-feasible repository | k_r ≥ 5 (≥ 1/6 of a 30-site quota) | With ≤ 4 recommendations, one recommendation moves the repository's matched precision by ≥ 25 points, and δ_r is dominated by non-recommendation actions |
| **Feasibility gate** | pooled Σk_r / Σn_r ≥ **0.20** and ≥ **5 of 7** repositories feasible | Below 0.20, even a 30-point precision gap contributes < 6 points to δ, and power at a/3 for a 15-point gap is ≤ 0.26 (R4-03c Sec. 7). 0.20 is under half the pilot's 0.43, allowing for test repositories with more key-material sites, where method+args abstains. |
| Repositories below the flag | **stay in** the confirmatory estimand and the pooled descriptive results | Excluding them on test-data outputs would make the estimand data-dependent. The estimand was fixed in advance. |
| Their contribution to confirmatory inference | full, through δ | as above |
| Gate fails | the bootstrap p is still computed and reported, but **cannot support "H2 direction supported"**. The result is reported as "H2 not assessable at equal coverage (matched coverage too low)". The natural-coverage comparison and RQ3 risk–coverage are reported as planned. | A gate can only remove claims, so family-wise error cannot increase (in simulation, the gate never raised a rejection rate) |
| Secondary | the same analysis restricted to matching-feasible repositories, labelled descriptive | |
| **Phase DV check (before F1)** | compute k_r per comparison on the 6 development/validation repositories, label-free, after Phase DV labelling is complete. If pooled DV matched coverage < 0.20, or ≥ 2 DV repositories have k_r < 5, the owner must revisit the H2 design **before F1**. | Uses development data while change is still allowed. The thresholds themselves are not tuned on DV; DV only decides whether the design is viable. |
| Test data reveal very low coverage | the gate decides as above: no new threshold, no re-specification, no dropped repositories | pre-registration |

## 5. Evidence-tier comparability

**Definitions.** `data_dictionary.md` Sec. 3 and `pqscan/roles/classifier.py`, one function for all arms.

| Tier | Meaning (same rule for every arm) |
|---|---|
| T0 | no meaningful evidence (name only) |
| T1 | one evidence type (method/argument, or key API), or conflicting evidence (capped) |
| T2 | resolved arguments and receiver/key evidence |
| T3 | T2 plus mutually consistent provenance and downstream use |

The tiers are ordinal; no numeric confidence is derived (frozen).

**Achievable tiers per arm** (code; pilot counts from `docs/dev/roles_on_pilot.md`):

| Arm | Can produce | Pilot | Notes |
|---|---|---|---|
| method-only | T0, T1 | T0 13, T1 17 | T0 = operation sites; T1 = key-material sites. Here the tier encodes **site kind** more than strength of evidence on comparable sites. |
| method+args | T0, T1 | T0 2, T1 28 | |
| method+args+recv | T0, T1, T2 | T1 16, T2 14 | |
| full | T0–T3 | T2 21, T3 9 | |

Answers to the owner's questions:
1. **Not every arm can produce every tier.** No comparator reaches T3; method-only and method+args do not reach T2.
2. **Ordering.** Yes, by definition: each step adds a resolved evidence type. Whether a higher tier is more often *correct* is an empirical question. On the pilot every full-arm recommendation was correct at both T2 and T3.
3. **Same meaning across arms?** Yes: same rule, same code. For a given site, the full arm's tier is ≥ the comparator's, except where receiver evidence reveals a conflict (capped at T1).
4. **Does it create an algorithm-specific advantage?**
   - The rule never compares tiers across arms. Only the withdrawing arm's *own* order is used, so cross-arm comparability is not required.
   - The real asymmetry is resolution. The full arm has four levels to withdraw by; the comparators have two or three.
   - When the full arm withdraws, it can drop its least-evidenced recommendations. That is part of what H2 evaluates: whether provenance evidence helps decide where to recommend.
   - On the pilot the advantage was small. The full arm's recommendations were all T2/T3, and 7 of 9 and 3 of 6 tied T2 recommendations had to be withdrawn by tie-break.
   - Simulation: Type I is controlled with flat tiers (S08, 0.0134) and with steep tiers (S09, 0.0047).
5. **Missing tiers and ties.**
   - Every Module C decision carries a tier: the classifier initialises T0. A RECOMMEND without a tier is a **validation error**.
   - Ties are broken by SHA-256 (R4-03a Sec. 3), which is library-independent.

**Is a common ordering needed?** No. Tier comparability across arms is not required by the rule. However, the measured difference mixes "better recommendations" with "better ranking of one's own recommendations". V12″ therefore adds a pre-registered, label-free **ranking-free sensitivity**: withdrawal in SHA-256 order alone, ignoring tiers. The gap between the primary and ranking-free results shows how much the tier ranking contributes. No ordering is chosen using labels.

## 6. Validation of the complete bootstrap (R4-03c)

**What it resamples.** Sites within repositories, with replacement; repositories are fixed. Each resample repeats every step:
1. resampling;
2. counts;
3. k_r;
4. tier withdrawal;
5. tie-breaks (fresh uniform keys);
6. frozen scoring;
7. δ*.

This is unit-tested (`test_bootstrap_resamples_match_exactly_in_every_replicate`; `test_vectorised_core_matches_reference_on_identity_resample`).

**Reproduction.** Revision 4 reported 0.0145 (2,000 × 400). The independent re-implementation on the same model gives 0.0170 (20,000 × 1,000; MC SE 0.0009). They agree within Monte Carlo error.

**Extension.** 18 scenarios × 20,000 data sets (MC SE 0.0011 at 0.025). They vary:
- natural coverage, from 0.17 to 0.80;
- which arm withdraws;
- matched coverage near 0 (S06) and exactly 0 in two repositories (S07);
- tier shape, flat and steep;
- indeterminate share, 15% and 35%;
- discordance (ρ = 0, 0.5, 0.9);
- fixed heterogeneity (τ = 0.05, 0.08);
- mixed coverage across repositories;
- random repositories;
- the margin boundary.

| Finding | Evidence |
|---|---|
| Valid and conservative in 16 of 17 fixed-repository scenarios | worst 0.0170 at a, 0.0074 at a/2, 0.0052 at a/3 |
| **Liberal at equal natural coverage** | S04: 0.0417 at a, 0.0216 at a/2, 0.0151 at a/3; estimator bias +0.0095, only partly reproduced by the bootstrap. Confirmed at B = 5,000 (0.0428). |
| Liberal whenever the comparator's coverage is within about 0.03 of the full arm's or above it | near-kink run: d = −0.11: 0.0307; −0.07: 0.0397; 0: 0.0388; +0.03: 0.0230; ≥ +0.07: ≤ 0.0075 |
| **The guard fixes it.** If the pooled natural-coverage gap G < 0.10, the p enters Holm as 2p. | guarded worst: 0.0203 at a, 0.0108 at a/2, 0.0077 at a/3 across all 8 gaps; the guard is essentially never on when d ≥ 0.20, so there is no power cost (pilot gap 0.33) |
| "Basic" bootstrap alternative rejected | liberal: S01 0.0284, S09 0.0316, S10 0.0333 |
| Not valid for generalisation | S16 (random repositories): 0.0422 |
| The bootstrap does not depend on the tie-break seed | structural: it re-draws its own keys (unit test) |

**6.4 Test chosen.** The percentile test as specified in R4-02 (p = (1 + #{δ* ≤ d0})/(B + 1), B = 10,000), plus the coverage-gap guard, plus the Monte Carlo rule (R4-03a Sec. 6).

**Population and assumptions supported.**
- **Supported:** inference about the 7 fixed repositories, with sites randomly sampled within each.
- **Not supported:** inference about a wider population of projects.

The figures rely on:
- the assumed generative model;
- error-free labels;
- deterministic arm outputs;
- about 30 sites × 7 repositories;
- the guard.

Sampling without replacement from finite pools makes the with-replacement bootstrap more conservative. Below-nominal rates in the simulated scenarios do not establish validity in situations the model does not represent.

**Cost of conservatism.** In most scenarios the test rejects at about half the nominal rate, which costs some power. Power at a/3 for a 15-point precision gap is 0.47 at c* = 0.30 and 0.73 at c* = 0.45. Power for a 30-point gap is ≥ 0.91 once c* ≥ 0.20.

## 7. Worked example

R4-03b gives the full 12-site calculation by hand, reproduced by the code and asserted in tests. It covers:
- natural counts 8 vs. 5, k = 5;
- withdrawal of s10 (T1), then s3 and s5 (2 of 4 tied T2, by SHA-256);
- overlap: both recommend s1, s8; F only s2, s4, s7; M only s3, s5, s12;
- correctness before and after matching (F 8 → 7, M 6);
- the paired table: b = 3, c = 2, δ = +1/12;
- the decomposition: the recommendation part is 0, and δ comes from s11's FLAG;
- all six tie outcomes, with tie-average +0.125.

## 8. Seed sensitivity

| Requirement | Status |
|---|---|
| Seed 20261113 is the sole primary analysis | **Yes.** The tie-break seed string `20261113`, the bootstrap generator `default_rng(20261113)`, and no other seed in the primary analysis. |
| 100 other seeds only for sensitivity | **Yes.** `20261113-S001` … `S100`, fixed now (R4-03a Sec. 8; `matching_ref_v4.SENSITIVITY_SEEDS`). |
| No seed selected for a favourable result | **Yes,** guaranteed procedurally: the seeds were fixed before any test data. In the worked example the primary seed happens to give the *less* favourable value (+0.0833 vs. a seed median of +0.1667). |
| Median, minimum, maximum and distribution reported | required in R4-03a Sec. 8, for δ and the site-level McNemar p; plus the exact tie-average δ̃ |
| No sensitivity seed changes the primary decision | **Guaranteed by construction for the confirmatory (Holm) decision.** The bootstrap p does not depend on the observed tie-break seed (unit test). What the seeds can change is the point estimate (tie SD 0.006–0.016 under the null, R4-03c Sec. 8) and the secondary McNemar p. If any seed would change a *secondary* conclusion, that is reported. The bootstrap's own Monte Carlo error is handled by the B = 100,000 rule, not by varying seeds. |

## 9. Remaining limitations

- **Untested arm behaviour.** All calibration uses an assumed model. Real arm behaviour on test repositories is unknown, and the pilot is circular.
- **Label noise is not modelled.** Single-annotator error would add noise of unknown direction.
- **The guard's 0.10 threshold** was chosen from the near-kink run of this model. It is fixed now, before any data.
- **Matching rewards ranking quality,** which the ranking-free sensitivity separates out.
- **H2's matched result is a complete-policy measure.** The paper must say so.

## 10. Exact V12″ recommendation (for owner approval)

> **V12″ — Equal-coverage comparison for H2 (replaces V12′).**
> (a) **Rule.** Coverage = RECOMMEND / eligible sites (frozen). For each comparison (H2-1 full vs. method+args; H2-3 full vs. method+args+recv; H2-4 full vs. method-only; all at T0 per V18) and each test repository, on the paired set (primary-set eligible sites where both arms ran): k_r = min(R_F, R_M). The arm with more RECOMMENDs withdraws its lowest-tier RECOMMENDs first, ties in SHA-256(`20261113|comparison|repository|site_id`) order, until both have exactly k_r. Withdrawn RECOMMENDs become ABSTAIN and are scored by the frozen judge. Matching is label-free, and its output is hashed before scoring. Specification: R4-03a.
> (b) **Interpretation.** The matched difference in correct-per-eligible-site is a complete-decision-policy measure at equal recommendation count. Every report gives the action decomposition, matched precision, the frozen recommendation correctness, and harmful/undecided/unjustified rates. It is never called recommendation accuracy.
> (c) **Feasibility gate.** A repository is matching-feasible if k_r ≥ 5. The gate passes if pooled matched coverage ≥ 0.20 and ≥ 5 of 7 repositories are feasible. If it fails, the comparison cannot support an H2 claim and is reported as "not assessable at equal coverage". No repository is ever excluded from the estimand. Phase DV check before F1 as in Sec. 4.
> (d) **Test.** The stratified re-matching percentile bootstrap (R4-02 Sec. 5; B = 10,000; seed 20261113), with the coverage-gap guard: if (ΣR_F − ΣR_M)/N < 0.10, the comparison's p enters Holm as min(1, 2p). Monte Carlo rule: within 3 MC-SE of a Holm threshold → B = 100,000 with the same seed.
> (e) **Seeds.** Primary tie-break seed 20261113 only. Sensitivity seeds 20261113-S001…S100 for reporting (median, minimum, maximum, distribution), plus the exact tie-average δ̃.
> (f) **Pre-registered secondary analyses:**
> - natural coverage;
> - the ranking-free withdrawal;
> - the fixed-target variant V12-B (target c_DV);
> - feasible-repositories-only (descriptive);
> - the proposed system (full at T2) vs. method+args, matched.

**Owner alternatives:**
- **(i)** Make the exact tie-average δ̃ the primary *point estimate*. The test is unaffected. It is statistically preferable (ties add 3–23% of the variance of the point estimate), at the cost of fractional per-site outcomes in the tables.
- **(ii)** Make the gate descriptive only, rather than claim-blocking. Not recommended.

## 11. Affected protocol sections and decisions (to be edited only after approval)

| Document | Section | Change |
|---|---|---|
| R4-02 | Sec. 2, 3 | comparison IDs H2-1/H2-3/H2-4 (the IDs B1–B4 collide with the baseline names B1-algorithm…B4-full-T2 in `pqscan/baselines/simple.py`); estimand interpreted as complete policy |
| R4-02 | Sec. 3 (B2) | feasibility fact |δ_REC| ≤ c* |
| R4-02 | Sec. 4 | "H2 direction supported" also requires the feasibility gate; wording "more site decisions correct at equal recommendation count" |
| R4-02 | Sec. 5 | calibration figure 0.0145 → reproduced as 0.0170, plus the 18-scenario results; the guard; percentile retained; the Monte Carlo rule |
| R4-02 | Sec. 6 | guarded p enters Holm |
| R4-03 | whole | replaced by the updated version (reviewed version preserved) |
| R4-05 | Sec. 1–2 | paired set excludes EXECUTION_FAILURE sites before matching |
| R4-06 | V12′ row | → V12″; sub-options (i) and (ii); V13′ and V10b″ rows reference the guard |
| R4-07 | Sec. 1 (H2 operationalisation), 5, 6 (freeze adds: hash of matching outputs, gate, guard, sensitivity-seed list), 7 (threats: complete-policy measure, ranking contribution, kink) | text updates |
| R4-09 | | change-log entries |
| R4-10 | B4, B5 | B4/B5 now cite R4-03a and the 29 tests. B5: the calibration on the assumed model is done (R4-03c) and must be re-run on the production code. New C5: Phase DV feasibility check. |
| R4-01 | D3 | resolved with modification; new findings: complete-policy interpretation, kink inflation, ID collision |

**Decisions affected:**
- **V12′ → V12″.**
- **V13′:** test details (guard, Monte Carlo rule).
- **V10b″:** guarded p in Holm.
- **V10a‴:** the B2 feasibility statement.
- **Unchanged:** V17, V18 and every other decision.
- **Unchanged frozen material:** H1–H4 wording, metrics, scoring, τ = T2 and the manifests.

## 12. Final verdict

**V12′: APPROVE WITH MODIFICATION, as V12″ (Sec. 10).**

Does the method measure recommendation correctness at equal coverage in a scientifically defensible way? **Not as previously described.**

What it defensibly measures is **the correctness of each arm's complete site-level decision policy when both may recommend equally often**. Recommendations, FLAG_NO_TARGET and abstentions all count, and matching withdrawals can turn into correct abstentions. Recommendation accuracy at equal coverage is reported alongside, as matched precision plus the decomposition.

With V12″, the confirmatory test controls family-wise error for claims about **the 7 fixed repositories**, under these narrower assumptions:
1. sites are randomly sampled within each repository;
2. labels are treated as correct;
3. arm outputs are deterministic;
4. about 30 sites in each of 7 repositories;
5. the coverage-gap guard is applied when natural coverages are close;
6. the feasibility gate passes, for the result to count as an H2 claim;
7. calibration under the assumed generative family, to be re-run on the production implementation before F1.

It does not support generalisation beyond the 7 repositories.
