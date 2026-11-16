# Coverage matching: validity simulation and worked example (PROPOSED rev4; not results)

Population (200,000 sites, assumed generative model in the script): matched coverage 0.441 for both arms; matched difference delta_true = +0.0200.

Samples: 4000 x (7 repositories x 30 sites), matching within each repository.

- mean estimate +0.0214 vs delta_true +0.0200 (bias +0.0014)
- empirical variance / mean multinomial variance estimate = 0.486 (<= 1 means the test's variance is not understated)
- rejection rate of Tango H0: delta <= delta_true at one-sided 0.025: 0.0025 (MC SE about 0.0025)

## Worked example (hypothetical; 10 sites, one repository)

| site | indeterminate | F action (tier) | F withdrawn | F correct (matched) | M action (tier) | M correct | pair (F,M) |
|---|---|---|---|---|---|---|---|
| s1 | no | REC (T3) | - | 1 | REC (T1) | 1 | (1,1) |
| s2 | no | REC (T3) | - | 1 | ABSTAIN | 0 | (1,0) |
| s3 | no | REC (T2) | - | 1 | REC (T1) | 0 | (1,0) |
| s4 | no | REC (T2) | yes | 0 | ABSTAIN | 0 | (0,0) |
| s5 | no | REC (T2) | yes | 0 | REC (T0) | 1 | (0,1) |
| s6 | yes | ABSTAIN | - | 1 | ABSTAIN | 1 | (1,1) |
| s7 | no | REC (T3) | - | 1 | ABSTAIN | 0 | (1,0) |
| s8 | no | REC (T2) | yes | 0 | REC (T1) | 1 | (0,1) |
| s9 | no | ABSTAIN | - | 0 | ABSTAIN | 0 | (0,0) |
| s10 | yes | REC (T2) | yes | 1 | ABSTAIN | 1 | (1,1) |

Natural coverage: F 8/10, M 4/10. k = 4; F withdraws 4 recommendation(s), lowest tier first (all T2; seeded tie-break), so both cover 4/10.
Matched correctness: F 6/10, M 5/10, delta = +0.10; discordant pairs b = 3, c = 2.
Natural-coverage correctness (secondary): F 7/10, M 5/10, delta = +0.20.
Numerator = sites judged CORRECT; denominator = all 10 eligible sites, for both arms (abstentions stay in the denominator).

- stratified re-matching bootstrap: P(lower 97.5% bound > delta_true) = 0.0145 (2000 data sets x 400 resamples; MC SE about 0.0035)
