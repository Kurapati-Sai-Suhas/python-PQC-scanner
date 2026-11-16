# R4-17 Consolidated final methodology audit — PROPOSED, NOT ADOPTED

Prepared 15 Nov 2026. **This document consolidates; it does not redesign.**
- Every procedure below is the one already specified, simulated and tested in R4-03a, R4-11 to R4-16.
- Where this audit adds anything, it is wording, a label or a reporting template. Each such item is marked **[new wording]**.

**Status:**
- Protocol v1.0.3, guide v1.0 and scoring policy v1.0 remain in force. Nothing is committed and no production code was changed.
- No test-split repository has been accessed, fetched, cloned or scanned. Annotation, F1, F2 and E have not started.
- Companion documents:
  - **R4-18:** the single decision matrix;
  - **R4-19:** the engineering hand-off;
  - **R4-20:** readiness and sequence.

**Verdict: READY FOR OWNER APPROVAL.** No critical or major defect remains. Four minor items are listed in Sec. 8. Each is resolved by a decision in R4-18 or by mechanical edits that follow approval; none needs a further design change.

## 1. Safeguards (confirmed for this audit)

| Safeguard | Status |
|---|---|
| Test repositories not accessed, fetched, cloned or scanned | confirmed. Only the manifest's names and commits were ever read. |
| No annotation, F1, F2 or E | confirmed (`docs/freeze/` is empty; the only tag is `phase2-complete`) |
| No production code modified | confirmed (`git status`: only `?? docs/proposals/`; `git diff HEAD` is empty) |
| No commit or push | confirmed (HEAD `664e640`) |
| Protocol v1.0.3 and history preserved | confirmed. Every superseded proposal is kept in `rev4/superseded/` or the earlier `rev3/` and v1.0.4 folders. |
| New material marked PROPOSED, NOT ADOPTED | confirmed for R4-11 to R4-20 and the results files |

## 2. The H2 wording

### 2.1 Why "δ > 0" and "δ ≥ 0.10" are different claims

The frozen sentence is: "correct-per-eligible-site of the provenance-aware arm exceeds the method+argument arm by ≥ 10 percentage points at equal coverage". It makes a **magnitude** claim.

**A test of H0: δ ≤ 0 makes a direction claim.**
- Rejecting it supports only δ > 0.
- That is equally compatible with δ = 0.01 and with δ = 0.30.
- Its error control says nothing about whether δ ≥ 0.10.

**The magnitude needs its own null, H0: δ ≤ 0.10.**
- It is rejected only if the one-sided 97.5% lower bound of δ exceeds 0.10.
- Under the planning model, power for this is very low:
  - 0.02 at the strictest Holm step, when the true δ is 0.12 (R4-13 Sec. 4, S17+);
  - 0.07–0.43 at a true 15 points in the earlier unmatched planning grid (R4-02 Sec. 3).
- The recommendation part of the matched difference cannot exceed the matched coverage. At the pilot's 0.43, a 10-point recommendation effect needs a precision gap of about 23 points (R4-03 audit Sec. 3.3).

**Therefore:**
- A significant positive result never proves a 10-point improvement.
- Calling such a result "H2 supported" would overstate the original hypothesis.

### 2.2 Recommended wording **[new wording; decision V10a in R4-18]**

**Research hypothesis H2 (frozen v1.0.3 sentence, kept verbatim as the motivating hypothesis).** "Correct-per-eligible-site of the provenance-aware arm exceeds the method+argument arm by ≥ 10 percentage points at equal coverage."

**Operational statements (v1.0.4):**

> **H2a (confirmatory; comparison H2-1).** In the seven test repositories, at equal recommendation volume within each repository, the complete-policy correctness per eligible site of Module C `full` (threshold T0) is higher than that of Module C `method+args` (threshold T0): δ > 0. Tested in the confirmatory family F-B under Holm (m = 3) at one-sided family α = 0.025, with the coverage-gap guard and the feasibility gate.

> **H2b (pre-specified exploratory effect-size analysis; comparison H2-2).** The same difference is at least 10 percentage points: δ ≥ 0.10. This is assessed by whether the one-sided 97.5% lower bound of δ (from the same bootstrap) exceeds 0.10. It is reported with the point estimate whatever H2a's outcome, and it is outside the family-wise error control.

### 2.3 Exact use of the phrase "H2 supported"

| Outcome (for comparison H2-1) | Permitted statement |
|---|---|
| gate fails | "H2 could not be assessed at equal coverage in these repositories (matched coverage too low)." Report estimates descriptively. |
| gate passes; H2a not rejected (Holm-adjusted guarded p > 0.025) | "**H2 not supported**: no evidence that the provenance-aware arm's complete policy is more often correct at equal recommendation volume." |
| H2a rejected; H2b lower bound ≤ 0.10 | "**H2a supported** (direction): … more often correct (δ̃ = x; 97.5% lower bound y). **The 10-point improvement stated in H2 was not established.**" Never "H2 supported". |
| H2a rejected **and** H2b lower bound > 0.10 | "**H2 supported**: … higher by at least 10 percentage points at equal recommendation volume. The direction was tested under family-wise control; the 10-point criterion was met in the pre-specified effect-size analysis, which is outside the family-wise control." |

**Error property of the last row.**
- Under the planning model, the H2b criterion alone falsely exceeds 0.10 with probability about 0.010 at its boundary (S17: 0.0097 at 0.025).
- A false "H2 supported" is therefore bounded by about 0.025 for H2-1 alone.
- It is not covered by the family-wise control over H2-3 and H2-4.

**Owner alternative (R4-18 V10a-alt).** Put H2b inside the confirmatory family (Holm m = 4), so that "H2 supported" is fully family-wise controlled. The cost is that H2b's power is near zero for plausible effects, and B2 enters the step-down.

### 2.4 Consistency across the documents and the final report

| Place | Required text | Status |
|---|---|---|
| RQ2 | unchanged: "Does bounded provenance-aware analysis improve correctness over simpler mappings?" | OK |
| Hypotheses (protocol Sec. 1) | the frozen H2 sentence, plus H2a and H2b as above | edit R4-07 Sec. 1 after approval |
| Decision rule (protocol Sec. 1 table) | the Sec. 2.3 table replaces "Paired McNemar …" as the H2 rule (V24) | edit after approval |
| Statistics (protocol Sec. 5; R4-02 Sec. 5–6) | V13 test, V20 guard, Holm F-B = {H2-1, H2-3, H2-4}, H2-2 outside | edit after approval |
| Abstract template | Sec. 2.5 | new |
| Results template | Sec. 2.5 | new |
| H2-3, H2-4 | ablation comparisons under RQ2. They are **not** part of "H2 supported"; reported as "evidence beyond receiver typing / beyond the method name improves complete-policy correctness" | new wording |

### 2.5 Reporting templates **[new wording]**

**Abstract sentence (choose the matching row of Sec. 2.3).** "In seven pre-registered test repositories, matching each method to the same number of migration recommendations per repository, the provenance-aware analysis made correct site-level decisions [more often than / not detectably more often than] method-and-argument analysis (difference x pp, one-sided 97.5% bound y pp). [The pre-registered 10-point improvement was / was not established.] Results describe these repositories only."

**Never in the abstract:**
- "recommendation accuracy" for the matched difference;
- any generalisation beyond the 7 repositories;
- "H2 supported" unless Sec. 2.3's last row applies.

**H2 results table (one row per comparison):**

| Field | Field |
|---|---|
| comparison | arms and thresholds |
| K (repositories with n_r ≥ 1) | Σ n_r (common evaluable) |
| failures | pooled matched coverage |
| gate | g and guard |
| δ̃ (repository-balanced) | δ̃ (site-weighted) |
| one-sided 97.5% bound | raw p |
| guarded p | Holm-adjusted p |
| decision | matched precision F / M |
| natural δ | ranking-free δ̃ |
| 100-seed range | S-F1 |

## 3. The consolidated coverage-matching procedure (verified)

| Requirement | Specification | Verified by |
|---|---|---|
| matching separately within each repository | `match_repository` per (comparison, repository) | `test_repositories_are_matched_independently`; worked example |
| count determined without labels | k_r = min(R_F,r, R_M,r) from actions only | `test_matching_ignores_labels`; production hashes the matching output before scoring |
| lowest evidence tiers withdrawn first | ascending T0 < T1 < T2 < T3 (frozen ordinal); SHA-256 within a tier | `test_lowest_tier_withdrawn_first_and_highest_kept`; bootstrap check in every resample |
| frozen scoring after withdrawal | withdrawn RECOMMEND → ABSTAIN → `pqscan.bench.judge.judge` | `test_withdrawn_recommendation_scored_as_abstain_by_frozen_judge`; `results/scoring_table_v4.md` |
| full denominator preserved for evaluable sites | n_r = \|C_r\|: every primary-set eligible site where both arms ran, whatever its action | R4-12; `test_execution_partition_and_common_set` |
| exact tie-averaged point estimate | δ̃_r = E over permitted tie orders, closed form O(n) | `test_tie_average_equals_brute_force_over_all_orders` |
| randomised tie-breaking inside every bootstrap resample | fresh uniform keys per resample (RK) | `test_bootstrap_resamples_match_exactly_in_every_replicate`; R4-13 |
| registered primary seed | **20261113**: the sampler seed (v1.0.3), the bootstrap generator, and the SHA-256 seed of the per-site illustration table. **The point estimate itself has no tie seed.** | R4-03a Sec. 8 |
| 100 sensitivity seeds | `20261113-S001` … `S100`, fixed; reported as the distribution of the seeded estimate and of the site-level McNemar p | `matching_ref_v4.SENSITIVITY_SEEDS` |

**Estimand.** For comparison c and repository r:
- E_A,r is arm A's expected complete-policy correctness per common evaluable site, after its recommendations are matched to k_r (expectation over sites drawn at random from r's primary-set frame, and over tie orders).
- δ_r = E_F,r − E_M,r, and δ = (1/K) Σ_r δ_r over the K = 7 fixed repositories.
- **Estimate:** δ̃ = (1/K) Σ_r δ̃_r.
- **Recommendation precision** (correct RECOMMENDs / k_r, tie-averaged) is a separate descriptive quantity. It is never substituted for δ̃.

**Wording rule [new].**
- Always write "equal recommendation **volume** (count) per repository".
- Never write "on the same sites", "identical recommendations" or "the same accepted sites".
- Every table shows "recommended by both / full only / comparator only".

## 4. Guard, bootstrap and the testing sequence

### 4.1 Guard (verified in code and tests)

- **Gap:** g = C_full − C_comparator = (1/K) Σ_r (R_F,r − R_M,r)/n_r, an exact fraction on the common evaluable sets.
- **Doubling when g < 0.10:** p → min(1, 2p). This covers negative gaps, zero, and 0 < g < 0.10.
- **No doubling when g ≥ 0.10,** including exactly 0.10.
- **Order:** the doubling happens **before** Holm. Tests: `test_guard_boundaries` (7 cases, including exactly 0.10 and unequal denominators), `test_guarded_p_doubles_and_caps`.

### 4.2 Exact family-wise sequence (F-B)

For each c in {H2-1, H2-3, H2-4}:
1. Build C_r; report failures; assert concordant failures (R4-12).
2. Compute R_F,r, R_M,r and k_r from tool outputs only. Hash the matching output.
3. Compute g_c (exact) and the feasibility gate G_c (Sec. 5), both label-free.
4. Join labels. Score with the frozen judge. Compute δ̃_r and δ̃_c.
5. Run the bootstrap (Sec. 4.3) → raw p_c, and the one-sided 97.5% bound L_c.
6. Monte Carlo rule: if p_c is within 3·√(p(1 − p)/B) of the Holm threshold it is compared to, re-run with B = 100,000 and the same seed.
7. Guard: p*_c = min(1, 2·p_c) if g_c < 1/10, else p_c.

Then:

8. **Holm** on {p*_H2-1, p*_H2-3, p*_H2-4} at α = 0.025:
   - order the guarded p ascending;
   - compare them with 0.025/3, 0.025/2 and 0.025;
   - stop at the first non-rejection.
9. **Claim.** Hypothesis c is *claimable* iff it is Holm-rejected **and** G_c passes. Otherwise its row in Sec. 2.3 applies.
10. **H2-2 (exploratory):** H2b is met iff L_H2-1 > 0.10. Reported whatever step 8 shows.
11. **Secondary and exploratory analyses:** R4-14 Sec. 2. None of them alters steps 8–10.

### 4.3 How the bootstrap produces the p-value

The method is a **stratified, re-matching, percentile** bootstrap.
- **Resampling.** For b = 1..B (B = 10,000; numpy PCG64, seed 20261113), within each fixed repository it draws n_r common evaluable sites with replacement. Each site carries both arms' natural actions and tiers, and its frozen-judge correctness for "kept" and for "withdrawn".
- **Recomputation.** In each resample it recomputes R_F*, R_M* and k_r*, withdraws lowest tier first with fresh uniform tie keys, re-scores, and forms δ*_b (repository-balanced).
- **The p-value is not a null-imposed distribution.** The bootstrap approximates the *sampling distribution of the estimator* around its own centre. The p-value is the inversion of the one-sided percentile interval: p = (1 + #{δ*_b ≤ d0}) / (B + 1), with d0 = 0 for H2a and 0.10 for H2b. H0 is rejected at level a when the (1 − a) lower percentile bound exceeds d0.
- **Why it can fail, and why the guard exists.** This works when the estimator is smooth. min(·) is not smooth at equal coverage, which is why the guard exists (Sec. 4.4).

### 4.4 Latest calibration (R4-13; 7 repositories × 30 sites; planning model)

| Check | Data sets | Worst result | MC SE |
|---|---|---|---|
| 17 fixed-repository null scenarios, a/3, a/2, a | 20,000 each | 0.0061 / 0.0093 / 0.0191 (nominal 0.0083 / 0.0125 / 0.025) | ≤ 0.0010 |
| previous failure case (equal natural coverage) | 20,000 | 0.0191 with the guard (0.0420 without) | 0.0010 |
| 8 near-equal-coverage gaps | 10,000 each | 0.0092 at a/3 (+1.0 SE above 0.0083); 0.0125 at a/2; 0.0213 at a | ≤ 0.0014 |
| family F-B, 8 configurations (global and partial nulls, ρ up to 0.9, inverted coverage, low coverage, heterogeneity) | 10,000 each | **FWER at most 0.0121** with the guard (0.0237 without) | ≤ 0.0011 |
| margin boundary (H2b, d0 = 0.10) | 20,000 | 0.0097 at 0.025 | 0.0007 |
| generalisation (random repositories) | 20,000 | 0.0415 (**not valid**; not used for inference) | 0.0014 |
| power, δ ≈ +0.05, 18 scenarios, gate passing | 4,000 each | 0.11–0.34 at a; 0.05–0.19 at a/3 | ≤ 0.008 |
| power with Holm at δ = +0.08 per false null | 10,000 | 0.28–0.60 | ≤ 0.005 |

**Limits of the simulation assumptions.**
- One generative family: three site truth classes; tier-dependent correctness; a copula for between-arm dependence.
- Sites are random within repositories; labels are error-free; arms are deterministic.
- n ≈ 30 and K = 7.
- Effects are capped at about 0.12 per repository by the model.
- With-replacement resampling of a without-replacement sample (conservative).

**Empirical calibration ≠ mathematical guarantee.**
- The figures show the procedure behaved at or below nominal in every tested configuration, with one +1-SE excursion at a single Holm step.
- They are not a proof of error control for data outside the model.
- The guard's factor 2 is empirically sized.

### 4.5 Independent check of the production implementation (before F1)

This is hand-off item 10 (R4-19); acceptance is required before F1.
- **Differential tests.** The production module must reproduce the reference implementation **exactly** (`scripts/matching_ref_v4.py`) on:
  - the worked example;
  - the three-repository example;
  - the pilot tables;
  - 1,000 random property cases: withdrawal sets, δ̃_r, g, the gate, guarded p, and Holm, all compared.
- **Bootstrap.** Same distribution for the same seed and inputs.
- **Re-calibration.** `calib_v12pp.py` and `sim_family_v12pp.py` are re-run with the production module substituted. The results must match the R4-13 tables within 3 MC-SE, and are recorded in the F1 record.
- **Independence.** The reference and production code are kept separate. The production code is written from R4-03a, not copied, and the differential test is what links them.

## 5. Execution failures and feasibility (confirmed)

| Requirement | Status | Source |
|---|---|---|
| File-level failures affect the relevant arms consistently | **yes, by construction** for the Module C arms: one parse, shared by all arms (`pqscan/bench/run.py` `judge_ours`). Production asserts it; a discordant failure stops the run. | R4-12 Sec. 1 |
| Every failed site reported | yes: per repository, per arm, by reason, library and scope; the failed-file list is published | R4-12 Sec. 5 |
| Primary denominator precisely defined | n_r = \|C_r\|: primary-set eligible sites of r where both arms ran; per-arm frozen rates use n_exec | R4-12 Sec. 3 |
| Failure sensitivity pre-registered | S-F1 (failures not correct, full \|E_r\|), S-F2 (bounds); wording triggers at 5% / 10% | R4-12 Sec. 4 |
| No repository silently removed | yes: every repository is in every table; one with n_r = 0 is listed, and K is printed with the estimate | R4-03a Sec. 7 |
| Zero- and low-coverage repositories reported | yes: k_r, matched coverage, the feasibility flag, δ̃_r and its decomposition | R4-14 Sec. 3 |
| Gate evaluated without correctness labels | yes: it uses only k_r and n_r (tool outputs and eligibility), computed in step 3 before labels are joined | Sec. 4.2 |

**Pooled matched-coverage formula when the denominators differ:**
- **Gate (site-weighted):** c_pool = Σ_r k_r / Σ_r n_r, as an exact fraction, with n_r the common evaluable count. It measures how many recommendations the comparison rests on.
- **Also reported (repository-balanced):** c̄ = (1/K) Σ_r k_r / n_r.
- **Gate rule:** c_pool ≥ 1/5 **and** #{r : k_r ≥ 5} ≥ 5.

**Eligibility is a label, but not a correctness label.** It defines the common evaluable set before any tool's correctness is computed, exactly as the frozen sampler's stopping rule does.

## 6. Hypotheses and comparison families (reconciled)

### 6.1 Identifier rule **[V23]**

- **B1-algorithm, B1-dual, B2-method-args, B3-full-noabst, B4-full-T2** remain **code baseline variants only** (`pqscan/baselines/simple.py`).
- **Hypotheses and comparisons** use **H#**: H1a, H1b, H2-1, H2-2, H2-3, H2-4, H2-S, F-A, H3, H4.
- **Mapping:**
  - H2-1 = `B3-full-noabst` vs. `B2-method-args`;
  - H2-S = `B4-full-T2` vs. `B2-method-args`;
  - H2-3 and H2-4 need T0 arms for method+args+recv and method-only (hand-off item 8).
- **Superseded labels:** the revision-4 labels B1, B2, B3, B4 map to H2-1, H2-2, H2-3, H2-4 in that order. ("H2-1 margin" in R4-15 is H2-2.)

### 6.2 Table

| ID | Arms (threshold) | Primary outcome | H0 / H1 | Test | α | Family | Status |
|---|---|---|---|---|---|---|---|
| H1a | — (labels) | share of eligible real sites needing evidence beyond the method/algorithm name | rule: ≥ 25% | Wilson 95% CI, decision rule | — | none | confirmatory decision rule (v1.0.3, unchanged) |
| H1b | each baseline (as run) | harmful + undecided + unjustified rate | rule: ≥ 10% for every baseline | Wilson 95% CI, decision rule | — | none | as above |
| **H2-1 (H2a)** | `full` T0 vs. `method+args` T0 | complete-policy correctness at equal recommendation volume, δ | δ ≤ 0 / δ > 0 | re-matching percentile bootstrap (RK), guard, gate | one-sided 0.025 (family) | **F-B** (m = 3) | **confirmatory** |
| H2-2 (H2b) | same as H2-1 | same | δ ≤ 0.10 / δ > 0.10 | one-sided 97.5% lower bound from the same bootstrap | 0.025, not family-controlled | none | **exploratory, pre-specified** |
| H2-3 | `full` T0 vs. `method+args+recv` T0 | as H2-1 | δ ≤ 0 / δ > 0 | as H2-1 | family | **F-B** | confirmatory |
| H2-4 | `full` T0 vs. `method-only` T0 | as H2-1 | δ ≤ 0 / δ > 0 | as H2-1 | family | **F-B** | confirmatory |
| H2-S | `full` T2 vs. `method+args` T0 | as H2-1 | δ ≤ 0 / δ > 0 | as H2-1 | none | — | secondary |
| Exp. B, natural | the ablation ladder (method-only → +args → +recv → full), T0 | correct-per-eligible at natural coverage | no difference | exact McNemar on common sites | — | — | secondary (v1.0.3 Experiment B) |
| F-A | proposed system (`full` T2) vs. each baseline that ran (≤ 8) | correct-per-eligible, natural coverage | δ ≤ 0 / δ > 0 | pooled exact McNemar on both-ran sites | one-sided 0.025 (family) | **F-A** (Holm, m ≤ 8) | confirmatory (separate family) |
| H3 | `full` at T2 vs. always-recommend and random withholding | harmful rate at coverage ≥ 70% | v1.0.3 rule | risk–coverage, AURC with bootstrap CI, comparisons at 70/80/90% | v1.0.3 | v1.0.3 | unchanged |
| H4 | per operator, per tool | invariance or flip rate on Dataset A | v1.0.3 rule | Wilson CI, base–variant pairs | — | none | unchanged |

**Decisions reconciled:**

| Decision | Role |
|---|---|
| V10a | H2a/H2b wording |
| V10b | F-B family and claim rule |
| V12 | matching and estimand |
| V13 | test |
| V17 | α |
| V18 | arms and thresholds |
| V20 | guard |
| V21 | gate |
| V22 | failures |
| V23 | identifiers |
| V24 | v1.0.3 amendments |

No two of these conflict (R4-18).

## 7. Integration status (R4-16, 26 rows)

All 26 rows are either OK or have a specified edit. Two edits change frozen protocol text, under V24 and the amendments listed in R4-18:
- H2's McNemar becomes secondary;
- the cluster-by-repository CI becomes exploratory.

The earlier revision-4 decisions V1, V2, V3′, V15 and V16′ also need amendments to v1.0.3 Sec. 2–3 (single investigator; 13 repositories; intra-rater reliability). These are listed with their decisions in R4-18, so that no amendment is silent.

## 8. Remaining issues

**Critical: none. Major: none.**

**Minor** (each resolved by approval plus mechanical edits; no redesign):
1. **The H2 wording must be fixed by decision V10a** (Sec. 2). Without it, "H2 supported" is ambiguous.
2. **Production T0 arms** for method+args+recv and method-only do not yet exist in `simple.py` (hand-off item 8).
3. **One +1-SE excursion.** At exactly equal coverage, the strictest Holm step sits at nominal within Monte Carlo error (0.0092 against 0.0083). This is disclosed; it is not a defect, because the family-wise error stays at or below 0.0121.
4. **Mechanical documentation edits** after approval: R4-02, R4-05, R4-06, R4-07, R4-09, R4-10, and v1.0.4 itself, per R4-16.

**Known limitations (not defects; disclosed):**
- a single human annotator;
- an AI-assisted review that is not independent human validation;
- 7 purposive repositories, with no generalisation;
- an assumed calibration model;
- low power for small complete-policy effects;
- a near-untestable 10-point margin;
- a circular pilot.

## 9. Final verdict

**READY FOR OWNER APPROVAL.** The complete H2 methodology is consistent across documents once R4-18 is approved:
- the arms, thresholds, estimand, test, guard, gate, failure handling, family, α and wording;
- it has been calibrated under its stated model, at all Holm levels and for the full family;
- it is backed by 82 passing tests and a reference implementation.

The next step is implementation (R4-19), not further design.
