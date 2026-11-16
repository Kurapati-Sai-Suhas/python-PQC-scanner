# Owner workload (ASSUMED parameters; not measured)

| Item | low | expected | high |
|---|---|---|---|
| dev_val: candidates | 378 | 468 | 618 |
| dev_val: primary h | 8 | 13 | 23 |
| dev_val: AI review h | 3 | 9 | 23 |
| dev_val: adjudication h | 2 | 6 | 19 |
| dev_val: intra-rater h | 2 | 2 | 4 |
| test: candidates | 511 | 630 | 833 |
| test: primary h | 11 | 18 | 31 |
| test: AI review h | 5 | 12 | 31 |
| test: adjudication h | 3 | 8 | 25 |
| test: intra-rater h | 2 | 3 | 5 |
| frame_audit h | 3 | 5 | 8 |
| pilot h | 2 | 3 | 4 |
| synthetic h | 2 | 3 | 5 |
| spec_review h | 2 | 4 | 8 |
| eval_reporting h | 8 | 16 | 32 |
| TOTAL h | 52 | 102 | 216 |

Parameters (low / expected / high):

- yield_S1: (0.5, 0.4, 0.3)
- overshoot_per_repo: (3, 5, 9)
- b0_per_repo: (10, 10, 10)
- min_ineligible: (0.75, 1.0, 1.5)
- min_eligible: (2.0, 3.0, 4.0)
- s2_yield: (0.05, 0.1, 0.2)
- min_ai_handling: (0.5, 1.0, 2.0)
- disagree_rate: (0.1, 0.2, 0.3)
- min_adjudicate: (3.0, 4.0, 6.0)
- min_relabel: (2.0, 2.5, 3.5)
- h_frame_audit: (3, 5, 8)
- h_pilot: (2, 3, 4)
- h_synthetic: (2, 3, 5)
- h_spec_review: (2, 4, 8)
- h_eval_reporting: (8, 16, 32)
