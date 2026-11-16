# R4-03b Worked example of equal-coverage matching — PROPOSED, NOT ADOPTED

Hypothetical data for illustration, not results. The example extends R4-03's 10-site example with two sites:
- s11, a FLAG_NO_TARGET on an inventory site;
- s12, a comparator-only recommendation.

It also gives every site a real ground-truth label, so that the **frozen judge** scores it, not a hand-typed 0/1. Every number below was calculated by hand and then reproduced by `scripts/worked_example_v4.py` (output `results/worked_example_v4.md`; asserted in `test_worked_example_numbers` and `test_tie_average_equals_mean_over_all_tie_orders`).

Comparison `H2-1`: F = `full` at T0, M = `method+args` at T0. One repository, 12 eligible sites, primary tie-break seed `20261113`.

## 1. Inputs

| site | ground truth | expected class | F output | M output |
|---|---|---|---|---|
| s1 | SIGN, determinate | SIG | REC SIG, T3 | REC SIG, T1 |
| s2 | SIGN, determinate | SIG | REC SIG, T3 | ABSTAIN |
| s3 | KEY_ESTABLISHMENT, determinate | KEM | REC KEM, T2 | REC SIG, T1 |
| s4 | VERIFY, determinate | SIG | REC KEM, T2 | ABSTAIN |
| s5 | SIGN, determinate | SIG | REC SIG, T2 | REC SIG, T0 |
| s6 | UNKNOWN, indeterminate | ABSTAIN | ABSTAIN | ABSTAIN |
| s7 | PK_ENCRYPT, determinate | KEM | REC KEM, T3 | ABSTAIN |
| s8 | SIGN, determinate | SIG | REC SIG, T2 | REC SIG, T1 |
| s9 | SIGN, determinate | SIG | ABSTAIN | ABSTAIN |
| s10 | UNKNOWN, indeterminate | ABSTAIN | REC SIG, T1 | ABSTAIN |
| s11 | KEY_MATERIAL_ONLY, determinate | NONE | FLAG_NO_TARGET | ABSTAIN |
| s12 | VERIFY, determinate | SIG | ABSTAIN | REC SIG, T1 |

## 2. Natural (unmatched) judgments

Scored with the frozen table (`results/scoring_table_v4.md`):

**F, 8 of 12 correct:**
- CORRECT: s1, s2, s3, s5, s7, s8; s6 (ABSTAIN on an indeterminate site); s11 (FLAG on an expected NONE).
- Not correct:
  - s4: INCORRECT, ROLE_INCOMPATIBLE (KEM on VERIFY);
  - s9 and s12: UNASSESSABLE;
  - s10: UNJUSTIFIED (a single target on an indeterminate site).

**M, 6 of 12 correct:**
- CORRECT: s1, s5, s8, s12; s6 and s10 (ABSTAIN on indeterminate sites).
- Not correct:
  - s3: INCORRECT, ROLE_INCOMPATIBLE;
  - s2, s4, s7, s9 and s11: UNASSESSABLE.

δ_nat = (8 − 6)/12 = **+0.1667**.

## 3. Matching

1. **RECOMMEND counts:**
   - R_F = 8 (s1, s2, s3, s4, s5, s7, s8, s10);
   - R_M = 5 (s1, s3, s5, s8, s12).

   Natural coverage: F 8/12 = 0.667, M 5/12 = 0.417. FLAG and ABSTAIN are not coverage.
2. **Target:** k = min(8, 5) = 5. F is the withdrawing arm, with e = 3.
3. **F's recommendations by tier:**
   - T1 = {s10};
   - T2 = {s3, s4, s5, s8};
   - T3 = {s1, s2, s7}.
4. **Withdrawal order.** s10 goes first (T1). Then 2 of the 4 tied T2 sites, ordered by SHA-256 of `20261113|H2-1|example|<site>`:
   - s3 `1060a263…`
   - s5 `260cd8b7…`
   - s4 `c50676aa…`
   - s8 `d015979c…`

   So **s10, s3 and s5 are withdrawn**. The boundary tier is T2, where 2 of 4 tied recommendations are withdrawn.
5. **Matched coverage:** F 5/12 = M 5/12 = 0.417.
6. **Recommended sites after matching:**
   - by both: s1, s8;
   - F only: s2, s4, s7;
   - M only: s3, s5, s12.

   **Equal counts, different sites:** only 2 of the 5 recommendations of each arm fall on the same sites.

## 4. Matched judgments

| site | F matched | F judgment | X | M judgment | Y | pair |
|---|---|---|---|---|---|---|
| s1 | REC SIG T3 | CORRECT | 1 | CORRECT | 1 | (1,1) |
| s2 | REC SIG T3 | CORRECT | 1 | UNASSESSABLE | 0 | (1,0) |
| s3 | ABSTAIN (withdrawn) | UNASSESSABLE | 0 | INCORRECT | 0 | (0,0) |
| s4 | REC KEM T2 | INCORRECT | 0 | UNASSESSABLE | 0 | (0,0) |
| s5 | ABSTAIN (withdrawn) | UNASSESSABLE | 0 | CORRECT | 1 | (0,1) |
| s6 | ABSTAIN | CORRECT | 1 | CORRECT | 1 | (1,1) |
| s7 | REC KEM T3 | CORRECT | 1 | UNASSESSABLE | 0 | (1,0) |
| s8 | REC SIG T2 | CORRECT | 1 | CORRECT | 1 | (1,1) |
| s9 | ABSTAIN | UNASSESSABLE | 0 | UNASSESSABLE | 0 | (0,0) |
| s10 | ABSTAIN (withdrawn) | **CORRECT** | 1 | CORRECT | 1 | (1,1) |
| s11 | FLAG_NO_TARGET | CORRECT | 1 | UNASSESSABLE | 0 | (1,0) |
| s12 | ABSTAIN | UNASSESSABLE | 0 | CORRECT | 1 | (0,1) |

**F's correct count changes by:**
- s3 −1: a correct recommendation withdrawn on a determinate site becomes UNASSESSABLE;
- s5 −1: same reason;
- s10 +1: an UNJUSTIFIED recommendation withdrawn on an indeterminate site becomes CORRECT.

So F goes from 8 to 8 − 1 − 1 + 1 = **7/12**. M is unchanged at **6/12**.

## 5. Paired table and estimate

| | M correct | M not correct | total |
|---|---|---|---|
| F correct | 4 (s1, s6, s8, s10) | b = 3 (s2, s7, s11) | 7 |
| F not correct | c = 2 (s5, s12) | 3 (s3, s4, s9) | 5 |
| total | 6 | 6 | 12 |

δ = (7 − 6)/12 = (b − c)/n = (3 − 2)/12 = **+0.0833**.

## 6. What the matched difference is made of

| final action | F correct | M correct | contribution to δ |
|---|---|---|---|
| RECOMMEND (kept) | 4 of 5 (s4 wrong) | 4 of 5 (s3 wrong) | 0 |
| withdrawn → ABSTAIN | 1 (s10) | — | +1/12 |
| FLAG_NO_TARGET | 1 (s11) | — | +1/12 |
| ABSTAIN (own) | 1 (s6) | 2 (s6, s10) | −1/12 |
| total | 7 | 6 | +1/12 |

- **Matched precision** (correct recommendations / k) is 4/5 for both arms: a difference of 0.
- The frozen "recommendation correctness" (CORRECT / determinate sites with RECOMMEND) is also 4/5 for both.
- **The whole +0.0833 comes from a non-recommendation action.** At site level, b − c = (s2 + s7 + s11) − (s5 + s12):
  - the four pairs involving recommendations (s2, s7 against s5, s12) cancel;
  - the net difference is s11, F's correct FLAG_NO_TARGET on an inventory site.
- In the category table, the +1/12 for F's withdrawal on s10 and the −1/12 in the ABSTAIN row are the same site, where both arms end up correctly abstaining.

This is the central interpretive point of the audit (R4-03 final Sec. 3): the matched correct-per-eligible-site difference is a property of the complete decision policy. It is not the accuracy of migration recommendations.

## 7. Tie-break sensitivity in this example

Only the T2 boundary is tied. The 6 equally likely choices of 2 of {s3, s4, s5, s8} give:

| withdrawn T2 pair | F correct | δ |
|---|---|---|
| s3, s5 (primary seed) | 7 | +1/12 |
| s3, s8 | 7 | +1/12 |
| s5, s8 | 7 | +1/12 |
| s3, s4 | 8 | +2/12 |
| s4, s5 | 8 | +2/12 |
| s4, s8 | 8 | +2/12 |

- **Exact tie-average δ̃** = (3 · 1 + 3 · 2)/(6 · 12) = **+0.125**.
- **The 100 sensitivity seeds:** +0.0833 × 48 and +0.1667 × 52. Median +0.1667, minimum +0.0833, maximum +0.1667.
- **The primary seed gave the lower value.** The seed is fixed in advance and never chosen for its result. In a 12-site repository one tie decides a 1/12 swing; on 30-site repositories the tie variability is smaller but not negligible (R4-03c Sec. E).

## 8. Same example at the natural coverage

Without matching, F is 2/12 ahead. Matching removes F's coverage advantage:
- F recommended on 3 more sites than M, two of them correctly.

What remains after matching is F's correct FLAG on s11.
