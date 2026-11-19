# G10 additional calibration of the signed coverage-gap guard

Procedure: production H2 single comparison via scripts/phase3_acceptance.py task_single (guard unchanged). B = 1000. Criterion: rate <= level + 3*sqrt(level*(1-level)/n) at a/3, a/2, a (plan Sec. 11.2). Seeds: numpy default_rng([20261113, 21, tid, chunk]); tid listed per scenario.

**Overall (null cells): PASS**

| id | kind | description | population repository gaps (F − M) | mean gap | n | a/3 | a/2 | a | P(guard on) | result |
|---|---|---|---|---|---|---|---|---|---|---|
| G10a | null | positive mean gap; two repositories near zero (kink) | +0.29, +0.29, +0.29, +0.29, +0.29, +0.00, +0.00 | +0.207 | 10000 | 0.0045 | 0.0080 | 0.0174 | 0.001 | pass |
| G10b | null | positive mean gap; one repository with a negative gap | +0.29, +0.29, +0.29, +0.29, +0.29, +0.29, -0.33 | +0.202 | 10000 | 0.0034 | 0.0051 | 0.0121 | 0.003 | pass |
| G10c | null | opposite-direction gaps that cancel (3 positive, 3 negative, 1 zero) | +0.29, +0.29, +0.29, -0.33, -0.33, -0.33, +0.00 | -0.015 | 10000 | 0.0020 | 0.0027 | 0.0062 | 0.999 | pass |
| G10d | null | plausible heterogeneous coverage (one negative, one zero gap) | +0.44, +0.33, +0.40, +0.07, -0.05, +0.25, +0.03 | +0.210 | 10000 | 0.0061 | 0.0090 | 0.0183 | 0.001 | pass |
| G10e | null | positive mean near the guard threshold (5 positive, 2 negative) | +0.29, +0.29, +0.29, +0.29, +0.29, -0.33, -0.33 | +0.114 | 10000 | 0.0023 | 0.0033 | 0.0092 | 0.327 | pass |
| G10a-power | power | positive mean gap; two repositories near zero (kink); delta_r = +0.04 everywhere (power; larger effects are unreachable by the qF tuning in some repositories of these patterns) | +0.29, +0.29, +0.29, +0.29, +0.29, +0.00, +0.00 | +0.207 | 2000 | 0.1060 | 0.1375 | 0.2175 | 0.000 | power |
| G10b-power | power | positive mean gap; one repository with a negative gap; delta_r = +0.04 everywhere (power; larger effects are unreachable by the qF tuning in some repositories of these patterns) | +0.29, +0.29, +0.29, +0.29, +0.29, +0.29, -0.33 | +0.202 | 2000 | 0.0665 | 0.0930 | 0.1580 | 0.001 | power |
| G10d-power | power | plausible heterogeneous coverage (one negative, one zero gap); delta_r = +0.04 everywhere (power; larger effects are unreachable by the qF tuning in some repositories of these patterns) | +0.44, +0.33, +0.40, +0.07, -0.05, +0.25, +0.03 | +0.210 | 2000 | 0.1030 | 0.1415 | 0.2190 | 0.000 | power |

Worst null rate at a = 0.025: 0.0183 (G10d).
Environment: {'python': '3.12.10', 'numpy': '2.5.4', 'scipy': '1.18.1', 'platform': 'Windows-11-10.0.26300-SP0'}; runtime 2.1 min.
Planning-model simulation: evidence about the procedure under assumed configurations, not about scanner accuracy.
