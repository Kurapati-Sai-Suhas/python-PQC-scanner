# Pilot (development) demonstration of matching — development data, circular, NOT a result

PROPOSED, NOT ADOPTED. Source: `docs/dev/pilot_harness/judgments.csv` (30 eligible pilot sites; pqscan was developed on them, so every figure is circular). F = `pqscan:B3-full-noabst` (full, T0); M = `pqscan:B2-method-args` (method+args, T0): exactly the V18 arms of hypothesis B1.

## paramiko (17 eligible sites)

- R_F = 14, R_M = 7, k = 7 (matched coverage 0.412); F withdraws 7 (P07, P04, P01, P08, P05, P06, P02), boundary tier T2 (7 of 9 tied).
- Natural M recommendations are a subset of natural F recommendations: True.
- Natural: F 17/17, M 8/17 (delta_nat +0.529).
- Matched: F 10/17, M 8/17 (delta +0.118; tie-average +0.118); b = 6, c = 4.
- Matched recommendations correct: F 7/7, M 7/7.
- Decomposition (F correct, M correct): REC (7, 7); WITHDRAWN (0, 0); FLAG (3, 1); ABSTAIN (0, 0); NO_FINDING (0, 0)

## python-jose (13 eligible sites)

- R_F = 9, R_M = 6, k = 6 (matched coverage 0.462); F withdraws 3 (J04, J12, J11), boundary tier T2 (3 of 6 tied).
- Natural M recommendations are a subset of natural F recommendations: True.
- Natural: F 13/13, M 10/13 (delta_nat +0.231).
- Matched: F 10/13, M 10/13 (delta +0.000; tie-average +0.000); b = 3, c = 3.
- Matched recommendations correct: F 6/6, M 6/6.
- Decomposition (F correct, M correct): REC (6, 6); WITHDRAWN (0, 0); FLAG (0, 0); ABSTAIN (4, 4); NO_FINDING (0, 0)

## Pooled (site-weighted)

- Natural coverage F 23/30 = 0.767, M 13/30 = 0.433; matched coverage 13/30 = 0.433.
- Natural correct-per-eligible: F 30/30, M 18/30, delta_nat = +0.400.
- Matched correct-per-eligible: F 20/30, M 18/30, delta = +0.067.
- Matched decomposition (F, M correct): REC (13, 13); WITHDRAWN (0, 0); FLAG (3, 1); ABSTAIN (4, 4); NO_FINDING (0, 0).

**Reading.** On the pilot both arms' recommendations are all correct, so at equal recommendation count their recommendation parts are identical. The whole matched difference comes from non-recommendation actions (F's correct FLAG_NO_TARGET on KEY_MATERIAL_ONLY sites, where M abstains and is UNASSESSABLE). The large natural difference is a coverage effect, which matching removes by design.

On the pilot, method-only and method+args+recv make the same role decisions as method+args (they differ only in tiers; `docs/dev/roles_on_pilot.csv`), and the comparator never withdraws, so B3 and B4 would give the same matched outcomes as B1 here.

Check (roles_on_pilot.csv): method-only, method+args and method+args+recv roles identical on all 30 sites: True.
