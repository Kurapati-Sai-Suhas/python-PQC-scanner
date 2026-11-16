# V12'' complete-procedure calibration (PROPOSED, NOT ADOPTED; simulated planning figures, not results)

`scripts/calib_v12pp.py`; B = 1000; Type I 20000 data sets per scenario, near-kink 10000, power 4000; 7 repositories x 30 sites; run time 35.1 min. Procedure: script docstring. Holm levels for m = 3: a/3 = 0.00833, a/2 = 0.0125, a = 0.025.

Two bootstrap variants were run on the **same** resamples of every data set; the point estimate is the exact tie-average in both:
- **RK** (recommended primary): re-matching bootstrap with fresh uniform tie keys inside each resample (ties averaged in distribution), percentile p, coverage-gap guard (p -> 2p if g < 0.10). **RK claim** = RK rejection that also passes the feasibility gate.
- **TA** (rejected alternative): re-matching bootstrap of the exact tie-averaged estimate itself, percentile p, same guard.

## A. Type I error, scenarios S00-S17 (population delta = d0 exactly; S00 tests its own delta_true)

| id | scenario | P(guard on) | P(gate) | RK a/3 | RK a/2 | RK a (MC SE) | RK claim a | RK unguarded a | TA a/3 | TA a (MC SE) |
|---|---|---|---|---|---|---|---|---|---|---|
| S00 | rev4 model (sim_matching_v4.py) reproduced; H0: delta <= delta_true | 0.000 | 1.000 | 0.0046 | 0.0076 | 0.0173 (0.0009) | 0.0173 | 0.0173 | 0.0068 | 0.0211 (0.0010) |
| S01 | base: F cov 0.69, M cov 0.40, rho 0.5, 15% indeterminate | 0.000 | 1.000 | 0.0032 | 0.0047 | 0.0113 (0.0007) | 0.0113 | 0.0113 | 0.0048 | 0.0175 (0.0009) |
| S02 | low natural coverage (F 0.34, M 0.17) | 0.003 | 0.077 | 0.0019 | 0.0034 | 0.0092 (0.0007) | 0.0001 | 0.0092 | 0.0033 | 0.0135 (0.0008) |
| S03 | high natural coverage (F 0.80, M 0.70) | 0.663 | 1.000 | 0.0027 | 0.0032 | 0.0065 (0.0006) | 0.0065 | 0.0118 | 0.0031 | 0.0092 (0.0007) |
| S04 | equal natural coverage (kink of min) | 1.000 | 1.000 | 0.0061 | 0.0093 | 0.0191 (0.0010) | 0.0191 | 0.0420 | 0.0086 | 0.0267 (0.0011) |
| S05 | comparator has the higher coverage (M withdraws; coarse T0/T1 tiers) | 1.000 | 1.000 | 0.0019 | 0.0027 | 0.0056 (0.0005) | 0.0056 | 0.0133 | 0.0050 | 0.0134 (0.0008) |
| S06 | very low matched coverage (M cov about 0.05; k_r often 0-2) | 0.000 | 0.000 | 0.0054 | 0.0080 | 0.0168 (0.0009) | 0.0000 | 0.0168 | 0.0080 | 0.0219 (0.0010) |
| S07 | two repositories with zero comparator coverage (k_r = 0), five base | 0.000 | 0.993 | 0.0024 | 0.0046 | 0.0124 (0.0008) | 0.0121 | 0.0124 | 0.0046 | 0.0176 (0.0009) |
| S08 | flat tiers: all F recommendations T2 (withdrawal is pure tie-break) | 0.000 | 1.000 | 0.0034 | 0.0061 | 0.0135 (0.0008) | 0.0135 | 0.0135 | 0.0098 | 0.0293 (0.0012) |
| S09 | steep tiers: F T0-T3 equally likely, strong tier gradient, F's indeterminate recs at T0 | 0.000 | 1.000 | 0.0011 | 0.0019 | 0.0046 (0.0005) | 0.0046 | 0.0046 | 0.0016 | 0.0060 (0.0005) |
| S10 | high indeterminate share (35%) | 0.000 | 1.000 | 0.0021 | 0.0032 | 0.0088 (0.0007) | 0.0088 | 0.0088 | 0.0034 | 0.0120 (0.0008) |
| S11 | low discordance (rho 0.9) | 0.000 | 1.000 | 0.0031 | 0.0047 | 0.0115 (0.0008) | 0.0115 | 0.0115 | 0.0050 | 0.0178 (0.0009) |
| S12 | high discordance (rho 0, arms independent given truth) | 0.000 | 1.000 | 0.0040 | 0.0057 | 0.0143 (0.0008) | 0.0143 | 0.0143 | 0.0059 | 0.0191 (0.0010) |
| S13 | heterogeneous repositories, fixed, tau 0.05 (mean delta_r 0) | 0.000 | 1.000 | 0.0032 | 0.0050 | 0.0113 (0.0007) | 0.0113 | 0.0113 | 0.0050 | 0.0169 (0.0009) |
| S14 | heterogeneous repositories, fixed, tau 0.08 (mean delta_r 0; delta_r from -0.12 to +0.12) | 0.000 | 1.000 | 0.0027 | 0.0047 | 0.0118 (0.0008) | 0.0118 | 0.0118 | 0.0046 | 0.0177 (0.0009) |
| S15 | heterogeneous coverage across repositories (F 0.5-0.95, M 0.2-0.8 on T) | 0.000 | 0.999 | 0.0019 | 0.0028 | 0.0081 (0.0006) | 0.0081 | 0.0081 | 0.0027 | 0.0115 (0.0008) |
| S16 | random repositories (superpopulation): delta_r ~ N(0, 0.08^2) truncated at +-0.12, redrawn per data set | 0.000 | 1.000 | 0.0169 | 0.0238 | 0.0415 (0.0014) | 0.0415 | 0.0415 | 0.0236 | 0.0537 (0.0016) |
| S17 | margin boundary: delta_r = 0.10 everywhere, H0: delta <= 0.10 (B2, exploratory) | 0.000 | 1.000 | 0.0022 | 0.0037 | 0.0097 (0.0007) | 0.0097 | 0.0097 | 0.0036 | 0.0141 (0.0008) |

## B. Type I error near equal natural coverage (population gap d = cov_F - cov_M)

| cell | P(guard on) | RK a/3 | RK a/2 | RK a (MC SE) | RK unguarded a/3 | RK unguarded a | TA a/3 | TA a/2 | TA a (MC SE) |
|---|---|---|---|---|---|---|---|---|---|
| near-kink gap d = +0.00 | 1.000 | 0.0092 | 0.0125 | 0.0213 (0.0014) | 0.0151 | 0.0418 | 0.0115 | 0.0160 | 0.0278 (0.0016) |
| near-kink gap d = +0.03 | 0.993 | 0.0035 | 0.0049 | 0.0089 (0.0009) | 0.0059 | 0.0181 | 0.0048 | 0.0064 | 0.0117 (0.0011) |
| near-kink gap d = +0.07 | 0.820 | 0.0015 | 0.0020 | 0.0057 (0.0008) | 0.0025 | 0.0116 | 0.0020 | 0.0032 | 0.0073 (0.0009) |
| near-kink gap d = +0.10 | 0.473 | 0.0011 | 0.0024 | 0.0055 (0.0007) | 0.0018 | 0.0064 | 0.0020 | 0.0031 | 0.0064 (0.0008) |
| near-kink gap d = +0.15 | 0.057 | 0.0012 | 0.0015 | 0.0037 (0.0006) | 0.0012 | 0.0038 | 0.0016 | 0.0024 | 0.0056 (0.0007) |
| near-kink gap d = +0.20 | 0.002 | 0.0019 | 0.0032 | 0.0066 (0.0008) | 0.0019 | 0.0066 | 0.0031 | 0.0044 | 0.0093 (0.0010) |
| near-kink gap d = -0.07 | 1.000 | 0.0065 | 0.0096 | 0.0200 (0.0014) | 0.0128 | 0.0402 | 0.0108 | 0.0154 | 0.0283 (0.0017) |
| near-kink gap d = -0.11 | 1.000 | 0.0052 | 0.0076 | 0.0154 (0.0012) | 0.0096 | 0.0339 | 0.0073 | 0.0117 | 0.0227 (0.0015) |

## C. Power, the same 18 scenarios with the population delta at about +0.05

(S00: its own delta_true, tested against 0; S13/S14: heterogeneous pattern + 0.05 capped at 0.12; S16: superpopulation mean about +0.05 (truncation); S17: delta 0.12 against d0 = 0.10.)

| id | pop. delta | P(guard on) | P(gate) | RK power a/3 | RK power a | RK claim power a | RK unguarded power a | TA power a |
|---|---|---|---|---|---|---|---|---|
| S00+ | +0.0217 | 0.000 | 1.000 | 0.025 | 0.067 | 0.067 | 0.067 | 0.097 |
| S01+ | +0.0500 | 0.000 | 1.000 | 0.136 | 0.268 | 0.268 | 0.268 | 0.328 |
| S02+ | +0.0500 | 0.003 | 0.081 | 0.200 | 0.361 | 0.025 | 0.362 | 0.431 |
| S03+ | +0.0500 | 0.666 | 1.000 | 0.095 | 0.189 | 0.189 | 0.246 | 0.218 |
| S04+ | +0.0500 | 1.000 | 1.000 | 0.170 | 0.308 | 0.308 | 0.420 | 0.355 |
| S05+ | +0.0500 | 1.000 | 1.000 | 0.115 | 0.216 | 0.216 | 0.312 | 0.312 |
| S06+ | +0.0500 | 0.000 | 0.000 | 0.507 | 0.681 | 0.000 | 0.681 | 0.713 |
| S07+ | +0.0500 | 0.000 | 0.994 | 0.185 | 0.341 | 0.338 | 0.341 | 0.403 |
| S08+ | +0.0500 | 0.000 | 1.000 | 0.169 | 0.320 | 0.320 | 0.320 | 0.452 |
| S09+ | +0.0500 | 0.000 | 1.000 | 0.046 | 0.114 | 0.114 | 0.114 | 0.138 |
| S10+ | +0.0500 | 0.000 | 1.000 | 0.077 | 0.161 | 0.161 | 0.161 | 0.197 |
| S11+ | +0.0500 | 0.000 | 1.000 | 0.171 | 0.322 | 0.322 | 0.322 | 0.397 |
| S12+ | +0.0500 | 0.000 | 1.000 | 0.110 | 0.226 | 0.226 | 0.226 | 0.271 |
| S13+ | +0.0493 | 0.000 | 1.000 | 0.131 | 0.255 | 0.255 | 0.255 | 0.307 |
| S14+ | +0.0414 | 0.000 | 1.000 | 0.087 | 0.188 | 0.188 | 0.188 | 0.227 |
| S15+ | +0.0500 | 0.000 | 0.999 | 0.103 | 0.215 | 0.215 | 0.215 | 0.262 |
| S16+ | +0.0439 | 0.000 | 1.000 | 0.143 | 0.251 | 0.251 | 0.251 | 0.292 |
| S17+ | +0.1200 | 0.000 | 1.000 | 0.020 | 0.055 | 0.055 | 0.055 | 0.067 |
