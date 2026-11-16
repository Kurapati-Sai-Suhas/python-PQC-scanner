# R3-01 Statistical methodology for H2 (PROPOSED, revision 3 — not adopted)

Status: proposal. Frozen protocol v1.0.3 is unchanged. Simulated figures come from `scripts/power_rev3.py` and `scripts/power_by_n_rev3.py` (Monte Carlo, 4,000 replicates per cell, seed 20261113). The full grids are in `results/`. **Every power figure is a planning estimate under stated assumptions, not a result.** The tests in `scripts/test_stats_rev3.py` (13, all passing) check the implementations.

## 1. The claim and its estimand

H2 (frozen wording): "correct-per-eligible-site of the provenance-aware arm exceeds the method+argument arm by ≥ 10 percentage points at equal coverage."

- Paired binary outcome per eligible test site: X = 1 if the full arm is correct, Y = 1 if the method+args arm is correct, scored with the frozen `scoring_policy.md`.
- Discordant counts: b (full correct, method+args wrong) and c (the reverse).
- **Site-weighted estimand:** δ_site = P(X = 1) − P(Y = 1), estimated by (b − c)/n.
- **Repository-weighted estimand:** δ_repo = the mean over repositories of δ_r, where δ_r = (b_r − c_r)/n_r.
- Equal quotas of 30 eligible sites per test repository make the two estimands identical whenever every repository reaches its quota. Under a shortfall they differ, and both are reported. The primary estimand is δ_repo (Sec. 4).

## 2. Option A: positive difference plus an observed ≥ 10 pp criterion (revision 2)

- **Null and alternative:** H0: δ ≤ 0 vs. H1: δ > 0, by a one-sided exact McNemar test (site level).
- **Supported** if p ≤ α and δ̂ ≥ 0.10.
- **What a significant result establishes:** the true difference is positive (at level α, assuming independent sites).
- **What it does not establish:** that the true difference exceeds 10 pp. δ̂ ≥ 0.10 is a property of the sample; when the true δ is exactly 0.10, it holds about half the time. Simulated P(supported) at a true 10 pp is 0.47–0.54 at α = .025 in every scenario, and 0.43–0.54 at α/3.
- **Verdict:** it does not test the literal claim. Revision 2's V10a should be rejected.

## 3. Option B: the literal superiority margin

- **Null and alternative:** H0: δ ≤ 0.10 vs. H1: δ > 0.10.
- **Method (site level):** the Tango/Nam score test for a paired difference of proportions with a non-zero margin (Tango 1998, *Stat Med* 17:891–908; Nam 1997, *Biometrics* 53:1422–1430). The restricted maximum-likelihood estimate of p21 under p12 = p21 + 0.10 solves 2n·q² + B·q + C = 0, where B = −b − c + (2n − b + c)·0.10 and C = −c·0.10·0.90. Re-derived from the paired multinomial likelihood in `stats_rev3.py`.
- **Why not McNemar:** an ordinary exact McNemar test cannot test this margin. It conditions on discordant pairs and tests P(b | discordant) = ½, which is δ = 0 only.
- **What a significant result establishes:** the true difference exceeds 10 pp (at level α, under the test's assumptions). This is the literal H2 claim.
- **What it does not establish:** anything about migration security, generalisation beyond the sampled repositories, or causality beyond the frozen arms.
- **Checked size:** at the boundary δ = 0.10 with independent sites, the simulated rejection rate is 0.022–0.027 at nominal 0.025. **With between-repository heterogeneity it inflates to 0.035–0.083** (τ = 0.05–0.10). The site-level test is therefore not valid as the confirmatory test with 7 repositories (Sec. 4).

## 4. Clustering: 7 test repositories

| Approach | Assumptions | Limitations with K = 7 | Simulated size at δ = 0.10, α = .025 |
|---|---|---|---|
| Site-level exact McNemar / score test | sites independent | ignores within-repository correlation; anti-conservative under heterogeneity | Tango: 0.022–0.027 (τ = 0) up to 0.069–0.083 (τ = 0.10) |
| Repository-clustered bootstrap CI | many clusters | with 7 clusters, bootstrap CIs under-cover (few-cluster problem); it is not a test correction | not used for inference |
| Cluster-adjusted McNemar (Durkalski et al. 2003) | asymptotic in the number of clusters | unreliable at K = 7 | not recommended |
| GEE or mixed models | asymptotic in K, or a correct random-effect model | unreliable at K = 7 without small-sample corrections; model-dependent | not recommended |
| **Repository-level one-sample t test on δ_r (df = 6)** | δ_r approximately normal (each is a mean of 30 sites); repositories independent | low df; power limited by between-repository variation | **0.021–0.026 in every scenario** |
| **Exact sign-flip randomization on δ_r − d0 (2⁷ = 128 patterns)** | δ_r − d0 symmetric about 0 under H0 | the smallest possible p is 1/128 = 0.0078, so at α/3 = 0.0083 rejection requires every repository to point the same way | 0.006–0.016 (conservative) |

**Recommendation (V13):** the confirmatory unit is the **repository**.
- **Primary test:** the repository-level one-sided t test (df = 6).
- **Robustness:** the exact sign-flip test.
- **Secondary (descriptive, assumes independence):** site-level exact McNemar and Tango.
- Repository-clustered bootstrap intervals are reported as descriptive only.
- **Seven clusters give weak inferential power whatever the number of sites.** 210 sites do not make this a large study.

## 5. Recommended H2 decision rule (V10a′; the H2 wording is unchanged)

**Fixed sequence within H2, at repository level, one-sided α = 0.025 (V17), Holm over family F-B:**

1. **Step 1:** H0: δ ≤ 0. Repository-level t test.
2. **Step 2** (only if step 1 rejects): H0: δ ≤ 0.10. Same test.

**Family F-B (V10b′)** has 4 hypotheses under Holm:
- H2-pos (full vs. method+args, δ > 0);
- H2-margin (full vs. method+args, δ > 0.10);
- full vs. method+args+recv, δ > 0;
- full vs. method-only, δ > 0.

Holm over all four controls the familywise error under any dependence, and keeps the frozen phrase "Holm-corrected across arms". Within it, H2-margin can only be rejected after H2-pos, which holds automatically because its p-value is never smaller.

**Outcome categories:**
- **Supported:** H2-margin rejected. The true difference exceeds 10 pp, which is the literal claim.
- **Partially supported:** H2-pos rejected, H2-margin not. A positive difference is established; the 10 pp margin is not. The point estimate and CI are reported, and a point estimate ≥ 10 pp is described as "consistent with, but not establishing" the margin.
- **Not supported:** H2-pos not rejected.

**Planning power (7 × 30, t test; worst Holm step α/4 to best α):**

| True δ | Discordance | τ | P(step 1) α/4 – α | P(step 2, margin) α/4 – α |
|---|---|---|---|---|
| 0.10 | 0.20–0.40 | 0–0.10 | 0.12–0.79 | = size, ≤ 0.026 |
| 0.15 | 0.20 | 0 / 0.05 / 0.10 | 0.91–0.99 / 0.77–0.95 / 0.49–0.74 | 0.11–0.30 / 0.08–0.22 / 0.04–0.12 |
| 0.15 | 0.40 | 0 / 0.10 | 0.56–0.83 / 0.32–0.60 | 0.06–0.17 / 0.04–0.12 |
| 0.20 | 0.20 | 0 / 0.10 | 1.00 / 0.76–0.93 | 0.56–0.88 / 0.15–0.34 |
| 0.20 | 0.40 | 0 / 0.10 | 0.85–0.98 / 0.57–0.84 | 0.25–0.53 / 0.14–0.34 |

**More sites per repository do not rescue the margin step.** At a true 15 pp, 30% discordance and τ = 0.05, power at α/3 goes 0.08 → 0.12 → 0.17 for 30 → 60 → 100 sites per repository (`results/power_by_n_rev3.md`). The margin is realistically establishable only if the true effect is about 25 pp or more with low heterogeneity. Example: 0.48–0.84 at α/3 with 30 sites per repository, for τ = 0.10–0.

**Honest planning statement for the protocol:** with 7 test repositories, the study can probably show a positive difference (step 1) if the true effect is 15–20 pp and repositories behave similarly. It is unlikely to establish the literal 10 pp margin unless the effect is much larger (about 25 pp or more). A "partially supported" outcome is the most likely positive outcome under moderate effects. This is stated before any test data exist.

## 6. Genuine defect: "at equal coverage" (V12)

The frozen scoring scores an abstention on a determinate site as UNASSESSABLE (not correct). The two arms abstain at different rates: in the circular development check, method+args abstained on 12 of 30 sites and full on none. A plain per-eligible-site comparison is therefore **not** "at equal coverage". The wording cannot be honoured without a defined procedure.

Options:

| Option | Procedure | Strength | Weakness |
|---|---|---|---|
| **(c) coverage-matched (recommended)** | Let the arm with higher coverage withdraw recommendations from its lowest evidence tier upward until both arms make decisions on the same number of eligible sites. Ties are broken by a seeded order (20261113). Withdrawn decisions are scored as abstentions under the frozen scoring. The H2 test then runs on these outcomes | implements the literal wording; deterministic; uses the frozen tiers | new code before F1; changes what "correct" means for the higher-coverage arm |
| (a) natural coverage | compare the arms at their own coverage | simple; matches the development harness | does not honour "at equal coverage"; the H2 wording would be misdescribed |
| (b) common-decided subset | only sites where both arms decide | equal coverage by construction | conditions on a post-treatment selection; biased |

**Recommendation:** (c) as primary; (a) reported as secondary. The H2 wording stays unchanged. RQ3's risk–coverage analysis is unaffected.

## 7. Label noise

Revision 2's figures stand as approximations. For errors spread over many classes and unrelated to the arms, a true difference shrinks roughly by (1 − e); (1 − 2e) is a binary-flip bound. Systematic, builder-related bias is not reduced by more sites. It is addressed only by the sensitivity analyses and the limitations section.

## 8. Other statistics (H1, H3, H4, reliability)

Unchanged in method. Wilson intervals for H1 rates are reported per tool, with a note that sites cluster in 7 repositories. H3 risk–coverage and AURC use the repository-level bootstrap, labelled descriptive with K = 7. Reliability statistics: `R3_03`.
