# Family-wise error of F-B procedures (simulated; PROPOSED rev4; not results)

20000 replicates; one-sided family alpha 0.025; Monte Carlo SE at 0.025 is about 0.0011.

| Mode / tests | Configuration | True nulls | FWER P3 (Holm B1,B3,B4) | P(B2 rejected) under P3-outside-family at 0.025 | FWER P4 (Holm B1-B4) |
|---|---|---|---|---|---|
| fixed repositories / site-level exact McNemar + Tango | C1 all zero | B1, B2, B3, B4 | 0.0153 | 0.0000 | 0.0118 |
| fixed repositories / site-level exact McNemar + Tango | C2 ma at margin, others zero | B2, B3, B4 | 0.0162 | 0.0236 | 0.0164 |
| fixed repositories / site-level exact McNemar + Tango | C3 ma 0.05, others zero | B2, B3, B4 | 0.0143 | 0.0006 | 0.0101 |
| fixed repositories / site-level exact McNemar + Tango | C4 ma at margin, others large | B2 | 0.0000 | 0.0232 | 0.0232 |
| fixed repositories / site-level exact McNemar + Tango | C5 ma zero, others large | B1, B2 | 0.0185 | 0.0000 | 0.0094 |
| random repositories / repository-level t | C1 all zero | B1, B2, B3, B4 | 0.0238 | 0.0001 | 0.0187 |
| random repositories / repository-level t | C2 ma at margin, others zero | B2, B3, B4 | 0.0199 | 0.0227 | 0.0212 |
| random repositories / repository-level t | C3 ma 0.05, others zero | B2, B3, B4 | 0.0176 | 0.0014 | 0.0135 |
| random repositories / repository-level t | C4 ma at margin, others large | B2 | 0.0000 | 0.0232 | 0.0231 |
| random repositories / repository-level t | C5 ma zero, others large | B1, B2 | 0.0249 | 0.0000 | 0.0121 |
