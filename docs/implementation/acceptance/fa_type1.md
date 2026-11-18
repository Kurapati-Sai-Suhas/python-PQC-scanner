# F-A Type I error simulation

Procedure: one-sided exact McNemar per baseline on pooled both-ran discordant pairs; Holm at 0.025. Criterion: rate <= 0.025 + 3 * sqrt(0.025 * 0.975 / R).

**Overall: PASS**

| Configuration | R | Rejection rate | Limit | Design E[b-c] | Mean discordant | Result |
|---|---|---|---|---|---|---|
| S1-homogeneous: every stratum: discordance 0.20, exactly balanced | 20000 | 0.0089 | 0.0283 | -0.034 | 41.3 | pass |
| S2-repo-heterogeneous: repositories favour opposite arms (shares 0.8/0.2, 0.75/0.25, 0.7/0.3, 0.5), cancelling under the design | 20000 | 0.0084 | 0.0283 | -0.031 | 41.3 | pass |
| S3-stratum-heterogeneous: app favours the proposed system (d 0.15, share 0.7), non-app the baseline (d 0.30, share 0.3); small non-app frames (fractions up to 0.83) | 20000 | 0.0063 | 0.0283 | -0.001 | 41.5 | pass |
| S4-sparse: discordance 0.03 (about 6 discordant pairs per data set) | 20000 | 0.0018 | 0.0283 | -0.013 | 5.3 | pass |
| S5-failures-random: S2 with 10% execution failures independent of the outcome | 20000 | 0.0088 | 0.0283 | -0.028 | 37.2 | pass |
| S6-failures-by-stratum: S3-type heterogeneity with failures 5% (app) and 30% (non-app); null on the both-ran sites (estimand of plan Sec. 9 item 4) | 20000 | 0.0075 | 0.0283 | -0.009 | 34.0 | pass |

| Family configuration | R | FWER over null baselines | Limit | Mean corr(b) | Result |
|---|---|---|---|---|---|
| F1-all-null-correlated: 8 baselines, all null, shared discordant core 60% (correlated tests) | 10000 | 0.0030 | 0.0297 | 0.59 | pass |
| F2-half-alternative: baselines 1-4 favour the proposed system (share 0.75), 5-8 null; FWER over 5-8 | 10000 | 0.0046 | 0.0297 | 0.60 | pass |
| F3-all-null-failures: F1 with 10% execution failures | 10000 | 0.0047 | 0.0297 | 0.51 | pass |
| F4-all-null-sparse: F1 with discordance 0.05 | 10000 | 0.0004 | 0.0297 | 0.71 | pass |

Environment: {'python': '3.12.10', 'numpy': '2.5.4', 'scipy': '1.18.1', 'platform': 'Windows-11-10.0.26300-SP0'}; runtime 2.4 s.
This simulation checks error control under an assumed design and assumed outcome configurations. It says nothing about scanner accuracy.
