# V12'' family-wise error, confirmatory family {H2-1, H2-3, H2-4} (PROPOSED, NOT ADOPTED; simulated, not results)

`scripts/sim_family_v12pp.py`; 10000 data sets per configuration, B = 1000; 7 repositories x 30 sites; Holm m = 3 at one-sided family alpha 0.025; run time 14.0 min. MC SE at 0.025 about 0.0016.

FWER = P(at least one true null hypothesis rejected). **RK** = random-key re-matching bootstrap, guarded p into Holm (recommended primary). **TA** = bootstrap of the exact tie-averaged estimate, guarded (rejected alternative). **no guard** = raw p into Holm. **claims** = rejections that also pass the feasibility gate. Both variants use the same resamples.

| config | description | true nulls (H2-1, H2-3, H2-4) | FWER RK (MC SE) | FWER RK no guard | FWER RK claims | FWER TA | FWER TA no guard | rejection rate per hypothesis (RK) | P(guard on) per hypothesis | P(gate passes) per hypothesis |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | global null; comparator coverages 0.40 / 0.58 / 0.36; rho 0.5 | null, null, null | 0.0044 (0.0007) | 0.0045 | 0.0044 | 0.0074 | 0.0074 | 0.003 / 0.000 / 0.002 | 0.000 / 0.246 / 0.000 | 1.000 / 1.000 / 1.000 |
| C2 | global null; H2-3 comparator at equal natural coverage (guard on for H2-3) | null, null, null | 0.0072 (0.0008) | 0.0115 | 0.0072 | 0.0136 | 0.0194 | 0.002 / 0.004 / 0.002 | 0.000 / 1.000 / 0.000 | 1.000 / 1.000 / 1.000 |
| C3 | global null; strong dependence (rho 0.9 for all three) | null, null, null | 0.0028 (0.0005) | 0.0028 | 0.0028 | 0.0055 | 0.0055 | 0.002 / 0.000 / 0.002 | 0.000 / 0.182 / 0.000 | 1.000 / 1.000 / 1.000 |
| C4 | partial null: H2-1 null; H2-3 and H2-4 true delta +0.08 | null, alt, alt | 0.0059 (0.0008) | 0.0059 | 0.0059 | 0.0107 | 0.0107 | 0.006 / 0.281 / 0.578 | 0.000 / 0.245 / 0.000 | 1.000 / 1.000 / 1.000 |
| C5 | partial null: H2-3 null at equal coverage (guard); H2-1 and H2-4 true delta +0.08 | alt, null, alt | 0.0121 (0.0011) | 0.0237 | 0.0121 | 0.0175 | 0.0339 | 0.569 / 0.012 / 0.598 | 0.000 / 1.000 / 0.000 | 1.000 / 1.000 / 1.000 |
| C6 | global null; low comparator coverage (gate often fails) | null, null, null | 0.0059 (0.0008) | 0.0059 | 0.0001 | 0.0087 | 0.0087 | 0.003 / 0.001 / 0.003 | 0.000 / 0.000 / 0.000 | 0.001 / 0.113 / 0.000 |
| C7 | global null on average; fixed repository heterogeneity tau 0.015 (delta_r -0.0225 to +0.0225; larger is not reachable for every comparator in this model), different pattern per comparison | null, null, null | 0.0037 (0.0006) | 0.0038 | 0.0037 | 0.0071 | 0.0071 | 0.002 / 0.000 / 0.002 | 0.000 / 0.240 / 0.000 | 1.000 / 1.000 / 1.000 |
| C8 | partial null with H2-1 comparator above the full arm's coverage (guard on); others +0.08 | null, alt, alt | 0.0115 (0.0011) | 0.0223 | 0.0115 | 0.0174 | 0.0337 | 0.011 / 0.281 / 0.588 | 1.000 / 0.253 / 0.000 | 1.000 / 1.000 / 1.000 |
