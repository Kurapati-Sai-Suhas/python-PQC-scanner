# R4-03 Equal-coverage comparison — PROPOSED, NOT ADOPTED (revision 4, updated after the R4-03 audit)

The version the owner reviewed is preserved unchanged in `superseded/R4_03_coverage_matching_as_reviewed.md`. This update implements the recommendation of `R4_03_final_matching_audit.md` (V12″).

| Topic | Detail |
|---|---|
| Algorithm | R4-03a |
| Hand-checked example | R4-03b |
| Calibration | R4-03c |

## 1. Definitions (frozen sources)

- **Coverage** = RECOMMEND / eligible sites (`data_dictionary.md` Sec. 4). FLAG_NO_TARGET and ABSTAIN are not coverage.
- **Correct-per-eligible-site** = CORRECT / eligible sites, under the frozen scoring (`scoring_policy.md` v1.0, `pqscan.bench.judge`). The full action × truth table is in `results/scoring_table_v4.md`.
- **Paired set:** the primary-set eligible sites of a repository where both arms ran. Sites with EXECUTION_FAILURE in either arm are removed and listed (scoring policy Sec. 5).

## 2. Matching rule (V12″)

For each comparison and each test repository r:
- **H2-1:** full vs. method+args;
- **H2-3:** full vs. method+args+recv;
- **H2-4:** full vs. method-only;
- all at T0 (V18).

1. **Target.** k_r = min(R_F, R_M), the RECOMMEND counts on the paired set.
2. **Withdrawal.** The arm with more RECOMMENDs withdraws R − k_r of them:
   - lowest tier first;
   - within a tier, in SHA-256(`20261113|comparison|repository|site_id`) order.
3. **Scoring of withdrawals.** A withdrawn RECOMMEND becomes ABSTAIN and is scored by the frozen judge.
4. **Result.** Both arms then RECOMMEND on exactly k_r sites. The **counts** are equal; the **sites** usually differ.
5. **Labels.** Labels are never read. The matching output is hashed before scoring.

**Why output-adaptive and not a fixed target.** Abstentions cannot be forced into recommendations. A fixed target taken from Phase DV (V12-B) can therefore fail on test data. V12-B stays a secondary analysis.

**Why within-repository.** The estimand is repository-balanced. Global matching would leave coverage unequal inside repositories.

## 3. What the comparison measures

- **The question.** The matched difference answers: "with equal numbers of recommendations, whose complete set of site decisions is more often correct?" Site decisions are recommend, flag no target, or abstain.
- **What it is not.** It is not the accuracy of migration recommendations. Withdrawing a correct recommendation costs one correct site. Withdrawing a recommendation on an indeterminate site gains one.
- **Pilot evidence** (development data, circular): the matched difference is +0.067, against +0.400 unmatched, and its recommendation part is exactly 0 (`results/pilot_matching_v4.md`).
- **Required reports** for every comparison:
  - the decomposition by final action;
  - matched precision;
  - the frozen recommendation correctness;
  - harmful, undecided and unjustified rates.

  The audit, Sec. 3, explains why.

## 4. Feasibility

- **Repository flag:** a repository is matching-feasible if k_r ≥ 5.
- **Gate:** pooled matched coverage ≥ 0.20 and ≥ 5 of 7 repositories feasible.
- **If the gate fails:** the comparison cannot support an H2 claim. Repositories are never excluded from the estimand.
- **Phase DV check before F1:** audit Sec. 4.

## 5. Inference

- **Primary test:** the stratified re-matching percentile bootstrap (B = 10,000, seed 20261113). Sites are resampled within repositories, and every matching step is repeated in each resample.
- **Coverage-gap guard:** if (ΣR_F − ΣR_M)/N < 0.10, the p-value enters Holm as min(1, 2p).
- **Simulated error:**
  - worst 0.0170 at a nominal 0.025 across 16 of 17 fixed-repository scenarios;
  - **0.0417 without the guard at equal natural coverage;**
  - ≤ 0.0203 with the guard (R4-03c).
- **Site-level tests:** exact McNemar and Tango on matched pairs are secondary. They are valid but conservative under matching (variance ratio 0.486; `results/matching.md`).
- **Scope:** inference is about the 7 fixed repositories only.

## 6. Seeds

- **Primary:** tie-break seed `20261113` only.
- **Sensitivity:** seeds `20261113-S001` … `S100`, reported as median, minimum, maximum and distribution, plus the exact tie-average δ̃.
- **The Holm decision cannot depend on the tie-break seed.** The bootstrap draws its own tie keys.

## 7. Secondary analyses

- natural coverage;
- ranking-free withdrawal (SHA-256 order only);
- the fixed-target V12-B;
- feasible-repositories-only (descriptive);
- the proposed system (full at T2) vs. method+args, matched;
- RQ3 risk–coverage curves and AURC (unchanged).
