# Pilot (development data, circular) — V12'' tables (PROPOSED, NOT ADOPTED; NOT results)

Source: `docs/dev/pilot_harness/judgments.csv` (30 eligible sites, labels and recorded full / method+args outputs) and `docs/dev/roles_on_pilot.csv` (roles and tiers of all four arms). pqscan was developed on these sites.

Derivation check: the derived full and method+args actions reproduce the recorded harness rows on 60 of 60 (site, arm) pairs.

## Evidence-tier distribution of RECOMMEND decisions (threshold T0)

| arm | RECOMMEND | T0 | T1 | T2 | T3 | FLAG_NO_TARGET | ABSTAIN |
|---|---|---|---|---|---|---|---|
| full | 23 | 0 | 0 | 15 | 8 | 3 | 4 |
| method+args | 13 | 1 | 12 | 0 | 0 | 1 | 16 |
| method+args+recv | 13 | 0 | 0 | 13 | 0 | 1 | 16 |
| method-only | 13 | 12 | 1 | 0 | 0 | 1 | 16 |

## H2-1: full vs method+args

| field | paramiko | python-jose |
|---|---|---|
| eligible sites | 17 | 13 |
| execution failures F / M | 0 / 0 | 0 / 0 |
| both ran / F only / M only / neither | 17 / 0 / 0 / 0 | 13 / 0 / 0 / 0 |
| common evaluable sites n_r | 17 | 13 |
| indeterminate sites (common) | 0 | 4 |
| natural RECOMMEND R_F / R_M | 14 / 7 | 9 / 6 |
| natural coverage F / M | 0.824 / 0.412 | 0.692 / 0.462 |
| matched count k_r (coverage) | 7 (0.412) | 6 (0.462) |
| withdrawn F / M (boundary tier, withdrawn of tied) | 7 / 0 (T2, 7 of 9) | 3 / 0 (T2, 3 of 6) |
| recommended after matching: both / F only / M only | 3 / 4 / 4 | 3 / 3 / 3 |
| correct F / M (primary-seed table) | 10 / 8 | 10 / 10 |
| incorrect (harmful) F / M | 0 / 0 | 0 / 0 |
| natural correct F / M | 17 / 8 | 13 / 10 |
| precision natural F | 14/14 = 1.000 | 9/9 = 1.000 |
| precision natural M | 7/7 = 1.000 | 6/6 = 1.000 |
| precision matched F (primary-seed table) | 7/7 = 1.000 | 6/6 = 1.000 |
| precision matched M (primary-seed table) | 7/7 = 1.000 | 6/6 = 1.000 |
| precision matched, tie-averaged F / M | 7.00/7 / 7.00/7 | 6.00/6 / 6.00/6 |
| **delta_r, exact tie-average (primary)** | **+0.1176** | **+0.0000** |
| delta_r, primary-seed table | +0.1176 | +0.0000 |
| delta_r over 100 seeds: min / median / max | +0.1176 / +0.1176 / +0.1176 | +0.0000 / +0.0000 / +0.0000 |
| delta_r ranking-free (tie-average) | +0.1176 | -0.0000 |
| delta_r natural coverage | +0.5294 | +0.2308 |
| failure sensitivity S-F1 (failures not correct, all eligible) | +0.1176 | +0.0000 |
| failure bounds S-F2 | [+0.1176, +0.1176] | [+0.0000, +0.0000] |
| matching-feasible (k_r >= 5) | yes | yes |

- Pooled repository-balanced tie-averaged delta = +0.0588; site-weighted +0.0667; ranking-free +0.0588; natural +0.3801.
- Coverage gap g = 0.3213 -> guard not active; matched coverage 13/30 = 0.433.

## H2-3: full vs method+args+recv

| field | paramiko | python-jose |
|---|---|---|
| eligible sites | 17 | 13 |
| execution failures F / M | 0 / 0 | 0 / 0 |
| both ran / F only / M only / neither | 17 / 0 / 0 / 0 | 13 / 0 / 0 / 0 |
| common evaluable sites n_r | 17 | 13 |
| indeterminate sites (common) | 0 | 4 |
| natural RECOMMEND R_F / R_M | 14 / 7 | 9 / 6 |
| natural coverage F / M | 0.824 / 0.412 | 0.692 / 0.462 |
| matched count k_r (coverage) | 7 (0.412) | 6 (0.462) |
| withdrawn F / M (boundary tier, withdrawn of tied) | 7 / 0 (T2, 7 of 9) | 3 / 0 (T2, 3 of 6) |
| recommended after matching: both / F only / M only | 4 / 3 / 3 | 3 / 3 / 3 |
| correct F / M (primary-seed table) | 10 / 8 | 10 / 10 |
| incorrect (harmful) F / M | 0 / 0 | 0 / 0 |
| natural correct F / M | 17 / 8 | 13 / 10 |
| precision natural F | 14/14 = 1.000 | 9/9 = 1.000 |
| precision natural M | 7/7 = 1.000 | 6/6 = 1.000 |
| precision matched F (primary-seed table) | 7/7 = 1.000 | 6/6 = 1.000 |
| precision matched M (primary-seed table) | 7/7 = 1.000 | 6/6 = 1.000 |
| precision matched, tie-averaged F / M | 7.00/7 / 7.00/7 | 6.00/6 / 6.00/6 |
| **delta_r, exact tie-average (primary)** | **+0.1176** | **+0.0000** |
| delta_r, primary-seed table | +0.1176 | +0.0000 |
| delta_r over 100 seeds: min / median / max | +0.1176 / +0.1176 / +0.1176 | +0.0000 / +0.0000 / +0.0000 |
| delta_r ranking-free (tie-average) | +0.1176 | -0.0000 |
| delta_r natural coverage | +0.5294 | +0.2308 |
| failure sensitivity S-F1 (failures not correct, all eligible) | +0.1176 | +0.0000 |
| failure bounds S-F2 | [+0.1176, +0.1176] | [+0.0000, +0.0000] |
| matching-feasible (k_r >= 5) | yes | yes |

- Pooled repository-balanced tie-averaged delta = +0.0588; site-weighted +0.0667; ranking-free +0.0588; natural +0.3801.
- Coverage gap g = 0.3213 -> guard not active; matched coverage 13/30 = 0.433.

## H2-4: full vs method-only

| field | paramiko | python-jose |
|---|---|---|
| eligible sites | 17 | 13 |
| execution failures F / M | 0 / 0 | 0 / 0 |
| both ran / F only / M only / neither | 17 / 0 / 0 / 0 | 13 / 0 / 0 / 0 |
| common evaluable sites n_r | 17 | 13 |
| indeterminate sites (common) | 0 | 4 |
| natural RECOMMEND R_F / R_M | 14 / 7 | 9 / 6 |
| natural coverage F / M | 0.824 / 0.412 | 0.692 / 0.462 |
| matched count k_r (coverage) | 7 (0.412) | 6 (0.462) |
| withdrawn F / M (boundary tier, withdrawn of tied) | 7 / 0 (T2, 7 of 9) | 3 / 0 (T2, 3 of 6) |
| recommended after matching: both / F only / M only | 4 / 3 / 3 | 3 / 3 / 3 |
| correct F / M (primary-seed table) | 10 / 8 | 10 / 10 |
| incorrect (harmful) F / M | 0 / 0 | 0 / 0 |
| natural correct F / M | 17 / 8 | 13 / 10 |
| precision natural F | 14/14 = 1.000 | 9/9 = 1.000 |
| precision natural M | 7/7 = 1.000 | 6/6 = 1.000 |
| precision matched F (primary-seed table) | 7/7 = 1.000 | 6/6 = 1.000 |
| precision matched M (primary-seed table) | 7/7 = 1.000 | 6/6 = 1.000 |
| precision matched, tie-averaged F / M | 7.00/7 / 7.00/7 | 6.00/6 / 6.00/6 |
| **delta_r, exact tie-average (primary)** | **+0.1176** | **+0.0000** |
| delta_r, primary-seed table | +0.1176 | +0.0000 |
| delta_r over 100 seeds: min / median / max | +0.1176 / +0.1176 / +0.1176 | +0.0000 / +0.0000 / +0.0000 |
| delta_r ranking-free (tie-average) | +0.1176 | -0.0000 |
| delta_r natural coverage | +0.5294 | +0.2308 |
| failure sensitivity S-F1 (failures not correct, all eligible) | +0.1176 | +0.0000 |
| failure bounds S-F2 | [+0.1176, +0.1176] | [+0.0000, +0.0000] |
| matching-feasible (k_r >= 5) | yes | yes |

- Pooled repository-balanced tie-averaged delta = +0.0588; site-weighted +0.0667; ranking-free +0.0588; natural +0.3801.
- Coverage gap g = 0.3213 -> guard not active; matched coverage 13/30 = 0.433.
