# R4-02 H2 statistical design — PROPOSED, NOT ADOPTED (revision 4)

Evidence comes from scripts in `scripts/`, with outputs in `results/`: 27 unit and cross-check tests pass (`results/unit_tests.txt`); the Type I and power grids are in `results/h2_type1.csv` and `results/h2_power.csv`; family-wise error is in `results/fwer.md`; coverage-matching validity is in `results/matching.md`. **All figures are simulated planning figures under stated assumptions, not results.**

## 1. Why revision 3 is not adopted as written

1. **Selection.** Revision 3 made a repository-level t test (df = 6) confirmatory. That test treats the 7 test repositories as a random sample from a population of projects. They were selected **purposively**: named candidates were filtered by mechanical criteria (`docs/benchmark/repository_split.md` Sec. 2; `candidate_verification*.md`). No random sampling of repositories took place, so the t test's population model is not supported by the design.
2. **Sites are randomly sampled.** Within each repository, sites *are* sampled at random (seeded order per stratum; R4-05). Inference about the **7 selected repositories** therefore has a design basis. Generalisation beyond them does not.
3. **Arm thresholds were unspecified.** The method+args arm can only produce tiers T0 and T1 (`docs/dev/roles_on_pilot.md`: T0 = 2, T1 = 28 on the pilot), so at τ = T2 it never recommends. Equal coverage with the full arm at T2 would then force both arms to zero coverage. The arms' thresholds must be fixed (V18).
4. **Matching changes the variance.** Coverage matching within a repository makes site outcomes dependent. The simulated variance of the matched difference is about 0.49× the multinomial variance the score test assumes. That makes the score test valid but very conservative (rejection rate 0.0025 at nominal 0.025). A re-matching bootstrap is needed (Sec. 5).

## 2. Primary estimand

**δ** is the repository-balanced difference in correct-per-eligible-site between the provenance-aware arm and the method+args arm, after within-repository coverage matching (R4-03), over the primary-set eligible sites of the **7 frozen test repositories**:

δ = (1/7) Σ_r δ_r, where δ_r = P_r(X = 1) − P_r(Y = 1)

- X and Y are the frozen-scoring CORRECT indicators of the two arms after matching.
- P_r is taken over the repository's primary-set eligible sites (R4-05), a finite population from which the sampler draws at random.
- With equal quotas (30 per repository), the repository-balanced and site-weighted estimates coincide. If a repository falls short, the repository-balanced estimate is primary and the site-weighted one is reported alongside.
- **Arms (V18):** the provenance-aware arm is Module C `full`; the comparator is `method+args`. Both use policy v1.1's role-to-target mapping with **no tier gate (threshold T0)**: UNKNOWN roles abstain and every other role is recommended. Coverage is then matched (R4-03).
  - This isolates the effect of evidence from the effect of the abstention policy, which RQ3 covers.
  - The proposed system (full at τ = T2, "B4") against the same comparator is reported as secondary.

## 3. Hypotheses, at one-sided α = 0.025 as the family level (V17)

| ID | Contrast | Null | Alternative | Status (recommended) |
|---|---|---|---|---|
| B1 | full vs. method+args | δ ≤ 0 | δ > 0 | confirmatory (family F-B) |
| B3 | full vs. method+args+recv | δ ≤ 0 | δ > 0 | confirmatory (family F-B) |
| B4 | full vs. method-only | δ ≤ 0 | δ > 0 | confirmatory (family F-B) |
| B2 | full vs. method+args | δ ≤ 0.10 | δ > 0.10 | **pre-specified, exploratory** (V10a‴); alternative: confirmatory within Holm m = 4 (Sec. 6) |

**Why the margin (B2) is recommended as exploratory.** With 7 × 30 sites, inference about the 7 repositories and no matching, simulated power for B2 is:

| True δ | Power at α = .025 | Power at α/3 | Power at α/4 |
|---|---|---|---|
| 0.15 | 0.17–0.43 | 0.08–0.27 | 0.07–0.24 |
| 0.20 | 0.58–0.99 | 0.40–0.97 | 0.36–0.97 |
| 0.25 (discordance 0.3–0.4 only; infeasible at 0.2) | 0.96–1.00 | — | 0.88–0.98 |

There is no non-circular estimate of the true effect: the development check (40 pp on the pilot) was made on code pqscan was tuned on. Confirmatory inference on the margin is adequately powered only if δ is at least about 20–25 pp. The protocol therefore states in advance that **H2's 10-point magnitude is estimated (point estimate with a one-sided 97.5% lower bound) and tested as an exploratory, pre-specified analysis**. The confirmatory claim is the direction: B1 under Holm.

## 4. Decision categories

| Outcome | Condition | Statement allowed |
|---|---|---|
| H2 direction supported | B1 rejected by Holm in F-B | "the provenance-aware arm is more often correct than the method+args arm at equal coverage in the 7 test repositories" |
| H2 magnitude established (exploratory) | additionally, the B2 lower 97.5% bound > 0.10 | "the estimated improvement exceeds 10 pp (exploratory, pre-specified)" |
| H2 direction supported, magnitude not established | B1 rejected, B2 bound ≤ 0.10 | "positive, but a ≥ 10 pp improvement is not established" (point estimate and bound reported) |
| H2 not supported | B1 not rejected | "no evidence of an improvement at equal coverage" |

**The H2 wording can stay unchanged**, but the protocol must state that the confirmatory test addresses H2's direction and the magnitude is exploratory. If the owner prefers the alternative (confirmatory margin, m = 4), "supported" means B2 rejected under Holm, with the low power stated.

## 5. Test statistics

**Primary (V13′; inference about the 7 repositories):** a stratified re-matching bootstrap.
1. Resample sites with replacement within each repository, carrying both arms' outputs and tiers.
2. Re-apply the matching rule in each resample.
3. Recompute δ*.
4. Use B = 10,000 resamples, seed 20261113.
5. One-sided p for H0: δ ≤ d0 is p = (1 + #{δ* ≤ d0}) / (B + 1).

Calibration under the assumed model (2,000 data sets × 400 resamples): P(97.5% lower bound > δ_true) = **0.0145**, compared with a nominal 0.025 and MC SE of about 0.0035. That is valid and moderately conservative. A larger calibration run is a pre-F1 engineering item (R4-06 checklist B5).

**Secondary (same estimand; valid, conservative under matching):**
- pooled site-level exact McNemar (d0 = 0) and Tango/Nam score test (d0 = 0.10) on the matched site-level pairs;
- the same tests without matching (natural coverage).

**Why site-level tests are valid here, and when they are not:**

| Mode | Site-level tests (worst Type I at nominal 0.025) | Repository-level t (worst Type I) |
|---|---|---|
| **Fixed repositories** (inference about the 7 repositories) | 0.0225 (boundary 0), 0.0300 (boundary 0.10; about 2 SE above nominal, so Tango is slightly liberal at n = 210) | 0.0278 / 0.0295 |
| **Random repositories** (generalisation) | up to **0.118 / 0.114** (invalid) | 0.0295 / 0.0293 |

Shapes covered: normal and skewed, τ ≤ 0.15, discordance 0.2–0.4.

Tango is applied **only to site-level paired binary outcomes**, never to repository aggregates. Its independence assumption holds for the fixed-repository estimand because sites are randomly sampled within each repository. It fails for the random-repository (generalisation) estimand.

**Exploratory generalisation (V13′):**
- repository-level one-sided t test (df = 6), labelled "model-based; repositories not randomly sampled";
- exact sign-flip and Wilcoxon signed-rank (both: smallest possible p = 1/128 = 0.0078, so neither can reject below α/4 = 0.00625, and both are descriptive under Holm);
- leave-one-repository-out estimates (7 values);
- **all seven δ_r values reported with per-repository CIs.**

## 6. Multiplicity (V10b″)

**Recommended F-B:** Holm over B1, B3, B4 (m = 3), at one-sided family-wise α = 0.025. "α = 0.025" is the **family level**; per-test thresholds come from Holm.

| Holm step | Compare | Threshold | Adjusted p |
|---|---|---|---|
| 1 | smallest p, p(1) | 0.025/3 = 0.00833 | min(1, 3·p(1)) |
| 2 | p(2) | 0.025/2 = 0.0125 | max(adj(1), min(1, 2·p(2))) |
| 3 | p(3) | 0.025 | max(adj(2), p(3)) |

Testing stops at the first non-rejection. Reject Hj when its adjusted p ≤ 0.025.

**Worked order (hypothetical p-values):** B4 0.0009, B1 0.0040, B3 0.0120.
- Adjusted: B4 0.0027, B1 0.0080, B3 0.0120.
- All three are ≤ 0.025, so all are rejected.
- Computed with `stats_v4.holm_adjust` (B3 and B4 fixed at 0.0120 and 0.0009):

  | B1 raw p | B1 adjusted | B3 adjusted | Outcome |
  |---|---|---|---|
  | 0.0100 | 0.0200 | 0.0200 | all rejected |
  | 0.0200 | 0.0240 | 0.0240 | all rejected |
  | 0.0300 | 0.0300 | 0.0240 | B1 **not** rejected; B3 and B4 rejected |

**Alternative F-B (m = 4, confirmatory margin):** Holm over B1, B2, B3, B4.
- **Gatekeeping:** H2's two stages need no separate fixed-sequence procedure. For the same data, the margin p-value is never smaller than the zero-margin p-value (tested in `test_margin_pvalue_never_below_zero_margin_pvalue`), so Holm's step-down never rejects B2 before B1.
- **Holm alone is sufficient.**

**Simulated family-wise error** (20,000 replicates; joint model with a shared full-arm outcome; 5 null configurations; `results/fwer.md`): ≤ 0.0185 for m = 3 and ≤ 0.0232 for m = 4 (fixed repositories, site-level tests); ≤ 0.0249 and ≤ 0.0231 (random repositories, repository-level t). Both procedures control FWER at 0.025.

**Caution:** testing B2 outside the family at the full α would push the combined error in configuration C2 to about 0.016 + 0.024. That is why B2 is labelled exploratory under m = 3.

**F-A (Experiment A):** a separate family. The proposed system (full, τ = T2) is compared with each baseline in the Experiment A list that produced results: algorithm-name mapping, method/argument-only mapping, pqcheck, pqc-audit, PostQuant, qsafe, QSA-regex, pqblocks-scan; m ≤ 8. CBOMkit is not run; Mehl is repository-level only.
- Contrast: δ > 0 in correct-per-eligible-site at **natural coverage**, since baselines have no tier ranking to match.
- Test: pooled site-level exact McNemar (fixed repositories).
- Holm at one-sided 0.025.

## 7. Limitations of the approximations

- The power and Type I figures come from a simple generative model: constant discordance per repository; normal or one-outlier heterogeneity; no matching (except `results/matching.md`).
- The matching model is assumed, not estimated.
- Tango is asymptotic and slightly liberal at n = 210 near the margin (0.030 at worst).
- Bootstrap calibration was checked on one assumed model with 2,000 data sets.
- Sampling without replacement from finite repository pools makes the with-replacement variance conservative.
- Label noise is not modelled (see revision 3, `R3_01` Sec. 7).
