# R4-13 Calibration of the complete V12″ procedure — PROPOSED, NOT ADOPTED

**Status of these figures.** Every figure is a simulated planning figure under the assumed generative model of `scripts/calib_matching_v4.py`. None is a result or an estimate of any tool's behaviour. Empirical calibration across tested scenarios is **not** a mathematical proof of error control.

This report supersedes R4-03c for the decision. R4-03c is kept in place and also preserved as `superseded/R4_03c_bootstrap_calibration_report_after_audit1.md`.

| Run | Content | Script | Output |
|---|---|---|---|
| single comparison | 18 scenarios × 20,000 data sets; 8 near-kink cells × 10,000; power: 18 scenarios × 4,000; B = 1,000 | `scripts/calib_v12pp.py` (35.1 min) | `results/calib_v12pp.md` / `.csv` |
| three-comparison family | 8 configurations × 10,000 data sets; B = 1,000; Holm m = 3 | `scripts/sim_family_v12pp.py` | `results/family_v12pp.md` |
| first run (TA variant only) | kept for the record | — | `superseded/results_ta_first_run/` |

Seeds: numpy `default_rng([20261113, 21 | 31, task, chunk])`.

**Monte Carlo SE at the nominal levels:**

| Data sets | at 0.025 | at 0.0125 | at 0.00833 |
|---|---|---|---|
| 20,000 | 0.0011 | 0.0008 | 0.0006 |
| 10,000 | 0.0016 | 0.0011 | 0.0009 |

## 1. The procedure tested (every step, on every data set)

1. **Natural coverage** per repository on the common evaluable set: R_F,r and R_M,r.
2. **Signed gap** g = (1/K) Σ_r (R_F,r − R_M,r)/n_r, as an exact fraction. The guard is active iff g < 1/10.
3. **Matching:** k_r = min(R_F,r, R_M,r) in each repository.
4. **Withdrawal:** lowest tier first.
5. **Ties.** Point estimate: the exact tie-average δ̃. Bootstrap: two variants on the **same** resamples:
   - **RK**: fresh uniform tie keys inside each resample.
   - **TA**: the exact tie-average inside each resample.
6. **Scoring:** the frozen-model scoring (the frozen judgment table restricted to Module C's actions).
7. **Bootstrap:** stratified re-matching, sites within repositories; percentile p = (1 + #{δ* ≤ d0})/(B + 1).
8. **Guard:** p → min(1, 2p) when active.
9. **Holm:** m = 3 at one-sided family α = 0.025 (family runs); the single-comparison runs report the three Holm levels.

The feasibility gate is recorded on every data set. A "claim" is a rejection that also passes the gate.

## 2. Type I error, 18 scenarios (RK with guard = recommended procedure)

**Nominal levels:** a/3 = 0.00833, a/2 = 0.0125, a = 0.025. Each cell is the worst value in its group.

| Group (scenarios) | RK a/3 | RK a/2 | RK a | TA a (rejected variant) |
|---|---|---|---|---|
| reproduction of the rev4 model (S00) | 0.0046 | 0.0076 | 0.0173 | 0.0211 |
| coverage levels; comparator higher (S01–S03, S05) | 0.0032 | 0.0047 | 0.0113 | 0.0175 |
| **equal natural coverage (S04)** | **0.0061** | **0.0093** | **0.0191** | 0.0267 |
| very low / zero matched coverage (S06, S07) | 0.0054 | 0.0080 | 0.0168 | 0.0219 |
| **flat tiers (S08)** | 0.0034 | 0.0061 | 0.0135 | **0.0293** |
| steep tiers (S09) | 0.0011 | 0.0019 | 0.0046 | 0.0060 |
| indeterminate share, discordance (S10–S12) | 0.0040 | 0.0057 | 0.0143 | 0.0191 |
| fixed heterogeneity, mixed coverage (S13–S15) | 0.0032 | 0.0050 | 0.0118 | 0.0177 |
| margin boundary, d0 = 0.10 (S17) | 0.0022 | 0.0037 | 0.0097 | 0.0141 |
| *random repositories (S16): generalisation* | *0.0169* | *0.0238* | *0.0415* | *0.0537* |

**For the 17 fixed-repository scenarios, RK with the guard is at or below nominal at every Holm level.** The worst values are 0.0191 at a, 0.0093 at a/2 and 0.0061 at a/3. The previous failure case S04 drops from 0.0420 (RK unguarded) to 0.0191.

**The rejected variant (TA).** Bootstrapping the exact tie-averaged estimate itself is liberal:
- S08: 0.0293 at a, about 3.5 MC-SE above nominal, with the guard inactive;
- S04: 0.0267 at a, even with the guard.

Removing tie noise from the resamples makes the bootstrap distribution too narrow for this non-smooth estimator.

## 3. Type I error near equal coverage (8 cells, gap d = cov_F − cov_M)

| d | P(guard on) | RK a/3 | RK a/2 | RK a (MC SE) | RK unguarded a | TA a |
|---|---|---|---|---|---|---|
| −0.11 | 1.000 | 0.0052 | 0.0076 | 0.0154 (0.0012) | 0.0339 | 0.0227 |
| −0.07 | 1.000 | 0.0065 | 0.0096 | 0.0200 (0.0014) | 0.0402 | 0.0283 |
| 0.00 | 1.000 | **0.0092** | **0.0125** | 0.0213 (0.0014) | 0.0418 | 0.0278 |
| +0.03 | 0.993 | 0.0035 | 0.0049 | 0.0089 (0.0009) | 0.0181 | 0.0117 |
| +0.07 | 0.820 | 0.0015 | 0.0020 | 0.0057 (0.0008) | 0.0116 | 0.0073 |
| +0.10 | 0.473 | 0.0011 | 0.0024 | 0.0055 (0.0007) | 0.0064 | 0.0064 |
| +0.15 | 0.057 | 0.0012 | 0.0015 | 0.0037 (0.0006) | 0.0038 | 0.0056 |
| +0.20 | 0.002 | 0.0019 | 0.0032 | 0.0066 (0.0008) | 0.0066 | 0.0093 |

**At exactly equal coverage (d = 0) the guarded test sits at the nominal level of the stricter Holm steps:**
- 0.0092 against 0.0083 (+1.0 MC-SE);
- 0.0125 against 0.0125.

The earlier independent near-kink run gave 0.0062 and 0.0103 at the same cell (`results/calib_nearkink.md`). The guard therefore brings the worst case to nominal within Monte Carlo error; it does not make it comfortably conservative there.

**Why halving is a defensible correction.**
- **Label-free and pre-registered.** g uses only natural tool outputs. It never sees labels.
- **It can only remove rejections.** Doubling p shrinks the rejection region, so it can never increase any error rate.
- **Sized from the observed inflation.** The worst unguarded inflation is about 1.7× at a and 1.8× at a/3 at d = 0, so a factor-2 Bonferroni-type halving is sufficient in every tested cell.
- **It targets the known cause.** It acts where the matched functional min(p_F, p_M) is non-differentiable, the known failure region of the bootstrap.
- **Cost.** When the full arm's coverage clearly exceeds the comparator's (d ≥ 0.20), it is almost never active. On the pilot, g = 0.32 for all three comparisons (`results/pilot_v12pp.md`).
- **What it is not.** It is an empirically sized correction. There is **no proof** that the inflation never exceeds 2 in data unlike the model.

## 4. Power (population δ ≈ +0.05 in each of the 18 scenarios; 4,000 data sets)

Power is modest by design:
- RK power at a: **0.11–0.34** in the fixed scenarios where the gate passes (S01, S03–S05, S07–S15). It is 0.36 in S02 and 0.68 in S06, but there the gate mostly fails, so the claim power is only 0.03 and 0.
- RK power at a/3: **0.05–0.19** in the scenarios where the gate passes.

The guard costs power only where it is active:
- S03: 0.189 vs. 0.246 unguarded;
- S04: 0.308 vs. 0.420;
- S05: 0.216 vs. 0.312.

TA would have had more power (for example S01 0.328 vs. 0.268), but it is not valid (Sec. 2).

**Power against matched coverage** (R4-03c Sec. 7, same bootstrap family):

| Precision gap | Matched coverage | Power at a/3 |
|---|---|---|
| 15 points | 0.30 | about 0.47 |
| 15 points | 0.45 | about 0.73 |
| 30 points | ≥ 0.20 | ≥ 0.91 |

## 5. Family-wise error of {H2-1, H2-3, H2-4} under Holm

### 5a. Results

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


## 6. What is established and what is not

**Established (empirically, under the model).** The complete RK + guard + Holm procedure keeps:
- each comparison at or below nominal at all three Holm levels in 17 fixed-repository scenarios;
- the worst near-kink cell at nominal within MC error;
- the family-wise error at or below 0.025 in every tested configuration (Sec. 5a).

**Not established:**
- error control for data unlike the model: non-random sampling of sites, label error, or behaviour of real tools;
- control for generalisation beyond the 7 repositories. This is explicitly invalid: 0.0415;
- any mathematical guarantee.

The production implementation must re-run this calibration (checklist B5) and reproduce these tables before F1.
