# Near-kink calibration of the percentile re-matching bootstrap (PROPOSED, NOT ADOPTED; simulated, not results)

`scripts/calib_nearkink_v4.py`; 10000 data sets per row, B = 1000; base model of `calib_matching_v4.py` with the comparator's coverage set below the full arm's (or above it: negative d) by the population gap d; population delta = 0 exactly. MC SE about 0.0016 at 0.025. Run time 4.3 min.

Guard (label-free, pre-registered): if the pooled natural-coverage gap G = (sum R_F - sum R_M) / N is below 0.10, every Holm threshold for that comparison is halved. The per-repository diagnostic (any |R_F - R_M| <= 3) is shown for comparison only.

| gap d | cov F | cov M | bias of estimate | P(guard on) | P(per-repo diag.) | rej a/3 | rej a/2 | rej a | at half level: a/6 | a/4 | a/2 | with guard: a/3 | a/2 | a |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| +0.00 | 0.693 | 0.693 | +0.0097 | 1.000 | 1.000 | 0.0127 | 0.0180 | 0.0388 | 0.0062 | 0.0103 | 0.0180 | 0.0062 | 0.0103 | 0.0180 |
| +0.03 | 0.693 | 0.662 | +0.0016 | 0.993 | 1.000 | 0.0075 | 0.0110 | 0.0230 | 0.0038 | 0.0052 | 0.0110 | 0.0038 | 0.0052 | 0.0111 |
| +0.07 | 0.693 | 0.622 | -0.0065 | 0.824 | 1.000 | 0.0017 | 0.0031 | 0.0075 | 0.0007 | 0.0012 | 0.0031 | 0.0009 | 0.0015 | 0.0037 |
| +0.10 | 0.693 | 0.593 | -0.0099 | 0.474 | 0.998 | 0.0017 | 0.0023 | 0.0064 | 0.0010 | 0.0012 | 0.0023 | 0.0012 | 0.0014 | 0.0051 |
| +0.15 | 0.693 | 0.543 | -0.0122 | 0.060 | 0.951 | 0.0010 | 0.0017 | 0.0041 | 0.0001 | 0.0002 | 0.0017 | 0.0008 | 0.0015 | 0.0036 |
| +0.20 | 0.693 | 0.492 | -0.0059 | 0.002 | 0.764 | 0.0017 | 0.0028 | 0.0067 | 0.0005 | 0.0010 | 0.0028 | 0.0017 | 0.0028 | 0.0067 |
| -0.07 | 0.693 | 0.763 | +0.0065 | 1.000 | 1.000 | 0.0138 | 0.0203 | 0.0397 | 0.0077 | 0.0108 | 0.0203 | 0.0077 | 0.0108 | 0.0203 |
| -0.11 | 0.693 | 0.805 | +0.0036 | 1.000 | 0.995 | 0.0092 | 0.0139 | 0.0307 | 0.0044 | 0.0069 | 0.0139 | 0.0044 | 0.0069 | 0.0139 |
