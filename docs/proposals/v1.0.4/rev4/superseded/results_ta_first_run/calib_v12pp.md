# V12'' complete-procedure calibration (PROPOSED, NOT ADOPTED; simulated planning figures, not results)

`scripts/calib_v12pp.py`; B = 1000; Type I 20000 data sets per scenario, near-kink 10000, power 4000; 7 repositories x 30 sites; run time 33.8 min. Procedure: script docstring. Holm levels for m = 3: a/3 = 0.00833, a/2 = 0.0125, a = 0.025.

Columns: **V12''** = exact tie-averaged re-matching bootstrap with the coverage-gap guard (the proposed primary); **unguarded** = the same without the guard; **random-key** = the earlier R4-03c variant (random tie keys), unguarded, on the same resamples; **claim** = V12'' rejection that also passes the feasibility gate.

## A. Type I error, scenarios S00-S17 (population delta = d0 exactly; S00 tests its own delta_true)

| id | scenario | P(guard on) | P(gate) | V12'' a/3 | V12'' a/2 | V12'' a (MC SE) | claim a | unguarded a/3 | unguarded a | random-key a |
|---|---|---|---|---|---|---|---|---|---|---|
| S00 | rev4 model (sim_matching_v4.py) reproduced; H0: delta <= delta_true | 0.000 | 1.000 | 0.0068 | 0.0102 | 0.0211 (0.0010) | 0.0211 | 0.0068 | 0.0211 | 0.0173 |
| S01 | base: F cov 0.69, M cov 0.40, rho 0.5, 15% indeterminate | 0.000 | 1.000 | 0.0048 | 0.0070 | 0.0175 (0.0009) | 0.0175 | 0.0048 | 0.0175 | 0.0113 |
| S02 | low natural coverage (F 0.34, M 0.17) | 0.003 | 0.077 | 0.0033 | 0.0062 | 0.0135 (0.0008) | 0.0003 | 0.0033 | 0.0135 | 0.0092 |
| S03 | high natural coverage (F 0.80, M 0.70) | 0.663 | 1.000 | 0.0031 | 0.0039 | 0.0092 (0.0007) | 0.0092 | 0.0042 | 0.0150 | 0.0118 |
| S04 | equal natural coverage (kink of min) | 1.000 | 1.000 | 0.0086 | 0.0134 | 0.0267 (0.0011) | 0.0267 | 0.0172 | 0.0516 | 0.0420 |
| S05 | comparator has the higher coverage (M withdraws; coarse T0/T1 tiers) | 1.000 | 1.000 | 0.0050 | 0.0070 | 0.0134 (0.0008) | 0.0134 | 0.0095 | 0.0256 | 0.0133 |
| S06 | very low matched coverage (M cov about 0.05; k_r often 0-2) | 0.000 | 0.000 | 0.0080 | 0.0115 | 0.0219 (0.0010) | 0.0000 | 0.0080 | 0.0219 | 0.0168 |
| S07 | two repositories with zero comparator coverage (k_r = 0), five base | 0.000 | 0.993 | 0.0046 | 0.0080 | 0.0176 (0.0009) | 0.0173 | 0.0046 | 0.0176 | 0.0124 |
| S08 | flat tiers: all F recommendations T2 (withdrawal is pure tie-break) | 0.000 | 1.000 | 0.0098 | 0.0143 | 0.0293 (0.0012) | 0.0293 | 0.0098 | 0.0293 | 0.0135 |
| S09 | steep tiers: F T0-T3 equally likely, strong tier gradient, F's indeterminate recs at T0 | 0.000 | 1.000 | 0.0016 | 0.0022 | 0.0060 (0.0005) | 0.0060 | 0.0016 | 0.0060 | 0.0046 |
| S10 | high indeterminate share (35%) | 0.000 | 1.000 | 0.0034 | 0.0052 | 0.0120 (0.0008) | 0.0120 | 0.0034 | 0.0120 | 0.0088 |
| S11 | low discordance (rho 0.9) | 0.000 | 1.000 | 0.0050 | 0.0081 | 0.0178 (0.0009) | 0.0178 | 0.0050 | 0.0178 | 0.0115 |
| S12 | high discordance (rho 0, arms independent given truth) | 0.000 | 1.000 | 0.0059 | 0.0091 | 0.0191 (0.0010) | 0.0191 | 0.0059 | 0.0191 | 0.0143 |
| S13 | heterogeneous repositories, fixed, tau 0.05 (mean delta_r 0) | 0.000 | 1.000 | 0.0050 | 0.0076 | 0.0169 (0.0009) | 0.0169 | 0.0050 | 0.0169 | 0.0113 |
| S14 | heterogeneous repositories, fixed, tau 0.08 (mean delta_r 0; delta_r from -0.12 to +0.12) | 0.000 | 1.000 | 0.0046 | 0.0072 | 0.0177 (0.0009) | 0.0177 | 0.0046 | 0.0177 | 0.0118 |
| S15 | heterogeneous coverage across repositories (F 0.5-0.95, M 0.2-0.8 on T) | 0.000 | 0.999 | 0.0027 | 0.0049 | 0.0115 (0.0008) | 0.0115 | 0.0027 | 0.0115 | 0.0081 |
| S16 | random repositories (superpopulation): delta_r ~ N(0, 0.08^2) truncated at +-0.12, redrawn per data set | 0.000 | 1.000 | 0.0236 | 0.0312 | 0.0537 (0.0016) | 0.0537 | 0.0236 | 0.0537 | 0.0415 |
| S17 | margin boundary: delta_r = 0.10 everywhere, H0: delta <= 0.10 (B2, exploratory) | 0.000 | 1.000 | 0.0036 | 0.0058 | 0.0141 (0.0008) | 0.0141 | 0.0036 | 0.0141 | 0.0097 |

## B. Type I error near equal natural coverage (population gap d = cov_F - cov_M)

| cell | P(guard on) | V12'' a/3 | V12'' a/2 | V12'' a (MC SE) | unguarded a/3 | unguarded a | random-key a |
|---|---|---|---|---|---|---|---|
| near-kink gap d = +0.00 | 1.000 | 0.0115 | 0.0160 | 0.0278 (0.0016) | 0.0199 | 0.0524 | 0.0418 |
| near-kink gap d = +0.03 | 0.993 | 0.0048 | 0.0064 | 0.0117 (0.0011) | 0.0077 | 0.0236 | 0.0181 |
| near-kink gap d = +0.07 | 0.820 | 0.0020 | 0.0032 | 0.0073 (0.0009) | 0.0034 | 0.0151 | 0.0116 |
| near-kink gap d = +0.10 | 0.473 | 0.0020 | 0.0031 | 0.0064 (0.0008) | 0.0024 | 0.0086 | 0.0064 |
| near-kink gap d = +0.15 | 0.057 | 0.0016 | 0.0024 | 0.0056 (0.0007) | 0.0016 | 0.0057 | 0.0038 |
| near-kink gap d = +0.20 | 0.002 | 0.0031 | 0.0044 | 0.0093 (0.0010) | 0.0031 | 0.0093 | 0.0066 |
| near-kink gap d = -0.07 | 1.000 | 0.0108 | 0.0154 | 0.0283 (0.0017) | 0.0198 | 0.0526 | 0.0402 |
| near-kink gap d = -0.11 | 1.000 | 0.0073 | 0.0117 | 0.0227 (0.0015) | 0.0158 | 0.0451 | 0.0339 |

## C. Power, the same 18 scenarios with every repository's population delta at +0.05

(S00: its own delta_true, tested against 0; S13/S14: heterogeneous pattern + 0.05 capped at 0.12; S16: superpopulation mean about +0.05 (truncation); S17: delta 0.12 against d0 = 0.10.)

| id | pop. delta | P(guard on) | P(gate) | V12'' power a/3 | V12'' power a | claim power a | unguarded power a |
|---|---|---|---|---|---|---|---|
| S00+ | +0.0217 | 0.000 | 1.000 | 0.042 | 0.097 | 0.097 | 0.097 |
| S01+ | +0.0500 | 0.000 | 1.000 | 0.183 | 0.328 | 0.328 | 0.328 |
| S02+ | +0.0500 | 0.003 | 0.081 | 0.252 | 0.431 | 0.028 | 0.432 |
| S03+ | +0.0500 | 0.666 | 1.000 | 0.118 | 0.218 | 0.218 | 0.279 |
| S04+ | +0.0500 | 1.000 | 1.000 | 0.212 | 0.355 | 0.355 | 0.473 |
| S05+ | +0.0500 | 1.000 | 1.000 | 0.194 | 0.312 | 0.312 | 0.415 |
| S06+ | +0.0500 | 0.000 | 0.000 | 0.544 | 0.713 | 0.000 | 0.713 |
| S07+ | +0.0500 | 0.000 | 0.994 | 0.237 | 0.403 | 0.400 | 0.403 |
| S08+ | +0.0500 | 0.000 | 1.000 | 0.278 | 0.452 | 0.452 | 0.452 |
| S09+ | +0.0500 | 0.000 | 1.000 | 0.058 | 0.138 | 0.138 | 0.138 |
| S10+ | +0.0500 | 0.000 | 1.000 | 0.099 | 0.197 | 0.197 | 0.197 |
| S11+ | +0.0500 | 0.000 | 1.000 | 0.231 | 0.397 | 0.397 | 0.397 |
| S12+ | +0.0500 | 0.000 | 1.000 | 0.145 | 0.271 | 0.271 | 0.271 |
| S13+ | +0.0493 | 0.000 | 1.000 | 0.168 | 0.307 | 0.307 | 0.307 |
| S14+ | +0.0414 | 0.000 | 1.000 | 0.116 | 0.227 | 0.227 | 0.227 |
| S15+ | +0.0500 | 0.000 | 0.999 | 0.134 | 0.262 | 0.261 | 0.262 |
| S16+ | +0.0439 | 0.000 | 1.000 | 0.176 | 0.292 | 0.292 | 0.292 |
| S17+ | +0.1200 | 0.000 | 1.000 | 0.028 | 0.067 | 0.067 | 0.067 |
