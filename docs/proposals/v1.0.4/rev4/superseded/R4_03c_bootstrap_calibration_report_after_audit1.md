# R4-03c Calibration of the stratified re-matching bootstrap — PROPOSED, NOT ADOPTED

**All figures are simulated planning figures under an assumed generative model. They are not results and not estimates of the tools' behaviour.**

Raw tables:
- `results/calib_matching.md` / `.csv`: 18 scenarios × 20,000 data sets × B = 1,000; a B = 5,000 check; power; tie variability.
- `results/calib_nearkink.md` / `.csv`: 8 coverage gaps × 10,000 data sets.

Scripts: `scripts/calib_matching_v4.py` (27.7 min, 16 processes) and `scripts/calib_nearkink_v4.py` (4.3 min). Environment: `results/environment.txt`. Seeds: numpy `default_rng([20261113, stream, scenario index])`.

## 1. What is resampled and what is recomputed

- **Resampled:** sites, with replacement, **within each repository**. Each site carries both arms' natural outputs (action, tier) and its frozen correctness under both "kept" and "withdrawn".
- **Not resampled:** repositories. They are fixed: the estimand concerns the 7 frozen repositories.
- **Recomputed in every resample:**
  1. R_F* and R_M*;
  2. k_r* = min;
  3. which arm withdraws;
  4. the lowest-tier-first withdrawal;
  5. ties, broken by fresh uniform keys from the bootstrap generator;
  6. scoring, with withdrawn sites given the ABSTAIN judgment;
  7. δ_r*, then δ* = mean over r.
- **Statistic:** the percentile p = (1 + #{δ* ≤ d0}) / (B + 1).
- **Check:** the vectorised core is unit-tested against the per-site reference implementation (`test_vectorised_core_matches_reference_on_identity_resample`). Every resample is checked for exact equality and tier order (`test_bootstrap_resamples_match_exactly_in_every_replicate`).

## 2. Generative model (assumed)

| Element | Description |
|---|---|
| Repositories and sites | 7 repositories × 30 eligible sites |
| Site truth | target-bearing determinate (T), expected NONE (N) or INDETERMINATE (I); shared by both arms |
| Each arm | recommends with a category-specific probability |
| Recommendations | a tier from a category-specific distribution; correctness probability q(tier) on T sites; always not correct on N or I sites |
| Non-recommendations | FLAG_NO_TARGET (correct on N) or ABSTAIN (correct on I) |
| Arm dependence | a shared-uniform copula (ρ) |

- **Scoring:** this is the frozen table (`results/scoring_table_v4.md`) restricted to the actions Module C emits.
- **Population estimand:** δ_r = E_F(c*) − E_M(c*), with c* = min(p_F, p_M), computed analytically.
- **Null scenarios:** each is calibrated by bisection, so δ = d0 exactly.

## 3. Type I error of the specified test (percentile)

Nominal levels are the Holm steps for m = 3: 0.00833, 0.0125 and 0.025. Monte Carlo SE with 20,000 data sets: 0.0006 / 0.0008 / 0.0011.

| Scenario group | Scenarios | Worst a/3 | Worst a/2 | Worst a |
|---|---|---|---|---|
| Reproduction of revision 4's check | S00 | 0.0044 | 0.0069 | 0.0170 |
| Coverage levels | S01–S03, S05 | 0.0038 | 0.0062 | 0.0135 |
| Very low and zero matched coverage | S06, S07 | 0.0052 | 0.0074 | 0.0155 |
| Tier shapes | S08 (flat), S09 (steep) | 0.0037 | 0.0054 | 0.0134 |
| Indeterminate share, discordance | S10–S12 | 0.0028 | 0.0047 | 0.0129 |
| Fixed heterogeneity, mixed coverage | S13–S15 | 0.0034 | 0.0053 | 0.0126 |
| Margin boundary (d0 = 0.10) | S17 | 0.0029 | 0.0044 | 0.0106 |
| **Equal natural coverage** | **S04** | **0.0151** | **0.0216** | **0.0417** |
| Random repositories (generalisation) | S16 | 0.0181 | 0.0254 | 0.0422 |

**Reproduction.** Revision 4 reported 0.0145, from 2,000 × 400 resamples with an MC SE of about 0.0027. The independent re-implementation on the same model gives **0.0170** (SE 0.0009). The two agree within Monte Carlo error. The test is valid and conservative there.

**Number of resamples.** With B = 5,000 (4,000 data sets), S01 gives 0.0120, S04 0.0428, S06 0.0155 and S09 0.0030. These match the B = 1,000 figures. The production run uses B = 10,000.

## 4. Where the test fails, and the guard

**S04 inflates the error by about 1.7×.** In S04 the two arms have equal natural coverage: the kink of min(p_F, p_M). Two things go wrong at once:
- **The estimator is biased upward.** The bias is +0.0095, about 0.27 SD. In finite samples one arm always has more recommendations. When that arm is the full arm, its finer tier ranking drops recommendations that sit on indeterminate sites.
- **The bootstrap does not reproduce that bias.** Its centre is only +0.0022 above the estimate.

This is the known non-smoothness of min() for the bootstrap.

**Near-kink run (`results/calib_nearkink.md`).** The population coverage gap is d = cov_F − cov_M.

| d | Percentile at a | With guard at a | With guard at a/3 | P(guard on) |
|---|---|---|---|---|
| −0.11 (comparator higher) | 0.0307 | 0.0139 | 0.0044 | 1.000 |
| −0.07 | 0.0397 | 0.0203 | 0.0077 | 1.000 |
| 0.00 | 0.0388 | 0.0180 | 0.0062 | 1.000 |
| +0.03 | 0.0230 | 0.0111 | 0.0038 | 0.993 |
| +0.07 | 0.0075 | 0.0037 | 0.0009 | 0.824 |
| +0.10 | 0.0064 | 0.0051 | 0.0012 | 0.474 |
| +0.15 | 0.0041 | 0.0036 | 0.0008 | 0.060 |
| +0.20 | 0.0067 | 0.0067 | 0.0017 | 0.002 |

- **Guard (label-free, pre-registered).** If the pooled natural-coverage gap G = (ΣR_F − ΣR_M)/N is below 0.10, the comparison's p enters Holm as min(1, 2p).
- **Effect.** With the guard, every row is at or below nominal at every Holm level. The guard is almost never active when d ≥ 0.20, so it costs no power when the full arm clearly covers more.
- **Pilot expectation.** On the development pilot the gap is 0.767 − 0.433 = 0.33 (`results/pilot_matching_v4.md`).

A first per-repository diagnostic (any repository with |R_F − R_M| ≤ 3) fired in 76–100% of data sets even at d = 0.15–0.20. It cannot discriminate and was rejected.

## 5. The rejected alternative ("basic" bootstrap)

The reverse-percentile test on the seed-free tie-averaged estimate is liberal in several fixed scenarios:
- S01 0.0284;
- S09 0.0316;
- S10 0.0333 (SE 0.0012–0.0013, all against a nominal 0.025);
- S04 0.0495.

The reason: in most scenarios the bootstrap distribution centre lies below the estimate (−0.002 to −0.009 in S01–S03, S07 and S09–S17; near 0 in S05, S06 and S08; above it only in S04). The percentile method is therefore conservative and the basic method liberal. **The percentile test specified in R4-02 is kept.**

## 6. What the bootstrap supports

| Inferential target | Supported? | Evidence |
|---|---|---|
| The 7 fixed repositories (sites randomly sampled within each) | yes, with the guard | Sec. 3–4; worst guarded rate 0.0203 at a, 0.0077 at a/3 |
| Repositories as a sample from a wider population | **no** | S16: 0.0422 at a. Repositories are not resampled, and with K = 7 purposive repositories they cannot be (R4-04) |

The assumptions under which the figures hold:
1. **Fixed repositories.**
2. **Sites drawn at random within each repository.** With-replacement resampling of a without-replacement sample from a finite pool overstates the variance, which is conservative.
3. **Labels are treated as error-free.** Label noise is not modelled.
4. **Arm outputs and tiers are deterministic** functions of the code and the site.
5. **The repository count and size are as tested:** about 30 sites per repository and 7 repositories.
6. **The coverage gap guard is applied.**
7. **The generative model** is the one in Sec. 2.

No claim of universal validity is made. Rates below 0.025 in 17 scenarios do not prove validity in situations the model does not represent.

## 7. Power and matched coverage (B1-type contrast; 2,000 data sets per cell)

When the arms differ only in recommendation precision, the population δ equals **matched coverage × precision gap**.

| Precision gap | Matched coverage | δ | Power at a/3 | Power at a |
|---|---|---|---|---|
| 0.15 | 0.05 / 0.10 / 0.20 / 0.30 / 0.45 | 0.008 / 0.015 / 0.031 / 0.045 / 0.068 | 0.01 / 0.07 / 0.26 / 0.47 / 0.73 | 0.05 / 0.17 / 0.44 / 0.67 / 0.86 |
| 0.30 | the same | 0.015 / 0.031 / 0.061 / 0.089 / 0.135 | 0.13 / 0.52 / 0.91 / 0.99 / 1.00 | 0.28 / 0.71 / 0.97 / 1.00 / 1.00 |

**Implication.** The recommendation part of δ is bounded by the matched coverage: |δ_REC| ≤ c*. At the pilot's matched coverage of 0.43, the 10-point B2 margin would need a precision gap of about 23 points from recommendations alone.

## 8. Tie-break variability (null scenarios; 1,000 data sets × 100 tie seeds)

| Scenario | SD across tie seeds | SD of the tie-averaged estimate | Share of the variance from ties (approx.) |
|---|---|---|---|
| S01 base | 0.0102 | 0.0331 | 9% |
| S08 flat tiers | 0.0164 | 0.0296 | 23% |
| S09 steep tiers | 0.0064 | 0.0353 | 3% |
| S15 mixed coverage | 0.0085 | 0.0331 | 6% |

- **Point estimate.** Ties add noticeable noise to the *point estimate*, the more so the coarser the tiers. That is why the exact tie-average δ̃ is reported next to the seeded estimate.
- **Decision.** Ties cannot change the confirmatory decision: the bootstrap p does not depend on the observed tie-break seed (R4-03a Sec. 8; unit test).
