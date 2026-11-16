# V12'' family-wise error, confirmatory family {H2-1, H2-3, H2-4} (PROPOSED, NOT ADOPTED; simulated, not results)

`scripts/sim_family_v12pp.py`; 10000 data sets per configuration, B = 1000; 7 repositories x 30 sites; Holm m = 3 at one-sided family alpha 0.025; run time 6.5 min. MC SE at 0.025 about 0.0016.

FWER = P(at least one true null hypothesis rejected). **V12''** = guarded p-values into Holm (proposed). **no guard** = raw p into Holm. **claims** = V12'' rejections that also pass the feasibility gate (what may be claimed).

| config | description | true nulls (H2-1, H2-3, H2-4) | FWER V12'' (MC SE) | FWER no guard | FWER claims | rejection rate per hypothesis (V12'') | P(guard on) per hypothesis | P(gate passes) per hypothesis |
|---|---|---|---|---|---|---|---|---|
| C1 | global null; comparator coverages 0.40 / 0.58 / 0.36; rho 0.5 | null, null, null | 0.0066 (0.0008) | 0.0067 | 0.0066 | 0.003 / 0.001 / 0.004 | 0.000 / 0.244 / 0.000 | 1.000 / 1.000 / 1.000 |
| C2 | global null; H2-3 comparator at equal natural coverage (guard on for H2-3) | null, null, null | 0.0128 (0.0011) | 0.0203 | 0.0128 | 0.004 / 0.006 / 0.004 | 0.000 / 1.000 / 0.000 | 1.000 / 1.000 / 1.000 |
| C3 | global null; strong dependence (rho 0.9 for all three) | null, null, null | 0.0078 (0.0009) | 0.0078 | 0.0078 | 0.005 / 0.001 / 0.005 | 0.000 / 0.183 / 0.000 | 1.000 / 1.000 / 1.000 |
| C4 | partial null: H2-1 null; H2-3 and H2-4 true delta +0.08 | null, alt, alt | 0.0109 (0.0010) | 0.0111 | 0.0109 | 0.011 / 0.340 / 0.661 | 0.000 / 0.244 / 0.000 | 1.000 / 1.000 / 1.000 |
| C5 | partial null: H2-3 null at equal coverage (guard); H2-1 and H2-4 true delta +0.08 | alt, null, alt | 0.0192 (0.0014) | 0.0370 | 0.0192 | 0.653 / 0.019 / 0.681 | 0.000 / 1.000 / 0.000 | 1.000 / 1.000 / 1.000 |
| C6 | global null; low comparator coverage (gate often fails) | null, null, null | 0.0095 (0.0010) | 0.0095 | 0.0005 | 0.002 / 0.004 / 0.005 | 0.000 / 0.000 / 0.000 | 0.001 / 0.114 / 0.000 |
| C7 | global null on average; fixed repository heterogeneity tau 0.015 (delta_r -0.0225 to +0.0225; larger is not reachable for every comparator in this model), different pattern per comparison | null, null, null | 0.0071 (0.0008) | 0.0072 | 0.0071 | 0.004 / 0.000 / 0.003 | 0.000 / 0.249 / 0.000 | 1.000 / 1.000 / 1.000 |
| C8 | partial null with H2-1 comparator above the full arm's coverage (guard on); others +0.08 | null, alt, alt | 0.0182 (0.0013) | 0.0339 | 0.0182 | 0.018 / 0.344 / 0.664 | 1.000 / 0.239 / 0.000 | 1.000 / 1.000 / 1.000 |
