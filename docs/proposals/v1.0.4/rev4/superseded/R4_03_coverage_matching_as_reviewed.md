# R4-03 Equal-coverage comparison — PROPOSED, NOT ADOPTED (revision 4)

## 1. Definitions (frozen sources)

- **Coverage** = RECOMMEND / eligible sites (`docs/specification/data_dictionary.md`). FLAG_NO_TARGET and ABSTAIN are not coverage.
- **Correctness** uses the frozen scoring (`scoring_policy.md` v1.0): an ABSTAIN is CORRECT on an INDETERMINATE site and UNASSESSABLE (not correct) on a DETERMINATE site.
- **The development example the owner cites:** the development harness (`docs/dev/pilot_harness/summary.md`, circular, not a result) shows method+args (B2, T0) with 12 of 30 abstained/unassessable and coverage 13/30, and full (B4, T2) with 0 abstentions and coverage 23/30. "Coverage" there is RECOMMEND/30. It is not 1 − abstentions, because FLAG_NO_TARGET actions exist.

## 2. Matching rule (V12′, recommended)

Applied separately for each F-B comparison and each repository r:

1. Let R_F and R_M be the numbers of RECOMMEND decisions of the two arms on r's primary-set eligible sites. Set k_r = min(R_F, R_M).
2. The arm with more RECOMMEND decisions withdraws R − k_r of them in increasing evidence tier (T0, T1, T2, T3). Within a tier, it uses a seeded random order of candidate IDs (seed 20261113, then the comparison name, then the repository).
3. A withdrawn decision becomes ABSTAIN and is scored by the frozen policy.
4. Both arms now RECOMMEND on exactly k_r sites, so coverage is equal **within each repository and therefore overall**.

**Pre-registered target.** The target is the rule k_r = min(R_F, R_M), computed only from the two arms' outputs, never from labels. It was fixed before any test access. Phase DV is used to:
- check that matching is feasible: both arms recommend on a non-trivial share;
- record the Phase DV matched coverage c_DV, which is also the fixed target of the sensitivity analysis below;
- test the implementation.

**Why not one fixed numeric target from Phase DV as primary.** If an arm's test coverage falls below a target fixed on Phase DV, it cannot be raised: abstentions cannot be forced into recommendations. Equal coverage would then fail. The output-adaptive rule always achieves equality without using labels.

**Alternative V12-B (fixed target):** each arm is trimmed to ⌊c_DV · n_r⌋ RECOMMEND decisions where possible. Where an arm has fewer, the comparison falls back to the primary rule and the shortfall is reported. Recommended as a **secondary** analysis.

**Global vs. within-repository matching.** Within-repository matching is chosen because the estimand is repository-balanced. Global matching could leave unequal coverage inside repositories.

**Verification on test data.**
- After matching, report per repository and pooled: R_F, R_M, k_r and coverage for each arm. Equality is exact by construction, and a script asserts it.
- Natural coverages are reported too.

## 3. Numerator, denominator and pairing

- **Numerator:** primary-set eligible sites judged CORRECT after matching.
- **Denominator:** all primary-set eligible sites of the repository. Abstentions, withdrawn decisions and FLAG_NO_TARGET actions stay in the denominator.
- **Pairing:** each site has one outcome per arm: X_i (full) and Y_i (comparator). The two arms may RECOMMEND on different subsets of sites, but every site still has a defined outcome under both, so the outcomes are paired on an identical denominator. That is what makes paired tests applicable.
- **Why McNemar is not used merely because the candidate set is shared:** pairing alone does not justify it. Matching makes outcomes dependent within a repository (k_r depends on all sampled sites). Simulated under an assumed model (`results/matching.md`):
  - the empirical variance of the pooled matched difference is **0.486×** the multinomial variance that McNemar and the score test assume;
  - the score test of H0: δ ≤ δ_true rejects **0.0025** of the time, against a nominal 0.025.

  The site-level tests therefore remain valid but very conservative, and the primary inference uses the **stratified re-matching bootstrap** (R4-02 Sec. 5). Its calibrated rate is **0.0145**, still conservative but much closer to nominal.

## 4. Worked example (hypothetical; output of `scripts/sim_matching_v4.py`)

10 sites in one repository. F = full arm at T0, M = method+args at T0.

| site | indeterminate | F action (tier) | F withdrawn | F correct | M action (tier) | M correct | pair |
|---|---|---|---|---|---|---|---|
| s1 | no | REC (T3) | – | 1 | REC (T1) | 1 | (1,1) |
| s2 | no | REC (T3) | – | 1 | ABSTAIN | 0 | (1,0) |
| s3 | no | REC (T2) | – | 1 | REC (T1) | 0 | (1,0) |
| s4 | no | REC (T2) | yes | 0 | ABSTAIN | 0 | (0,0) |
| s5 | no | REC (T2) | yes | 0 | REC (T0) | 1 | (0,1) |
| s6 | yes | ABSTAIN | – | 1 | ABSTAIN | 1 | (1,1) |
| s7 | no | REC (T3) | – | 1 | ABSTAIN | 0 | (1,0) |
| s8 | no | REC (T2) | yes | 0 | REC (T1) | 1 | (0,1) |
| s9 | no | ABSTAIN | – | 0 | ABSTAIN | 0 | (0,0) |
| s10 | yes | REC (T2) | yes | 1 | ABSTAIN | 1 | (1,1) |

- **Matching:** natural coverage is F 8/10 and M 4/10, so k = 4. F withdraws 4 recommendations, all at T2, chosen by the seeded order. Both arms now cover 4/10.
- **Matched correctness:** F 6/10, M 5/10, δ = +0.10; discordant pairs b = 3, c = 2.
- **Natural-coverage (secondary):** F 7/10, M 5/10, δ = +0.20.
- **Note s10:** F's recommendation on an indeterminate site was not correct. Withdrawing it makes it CORRECT under the frozen scoring. Matching can therefore raise as well as lower the withdrawing arm's correctness. That is a property of the frozen scoring, reported as such.

## 5. Secondary analyses

- comparison at natural coverage;
- the fixed-target V12-B variant;
- the proposed system (full at τ = T2) vs. method+args, matched;
- RQ3 risk–coverage curves and AURC (unchanged).

## 6. Seed sensitivity

Ties within a tier are broken by a seeded order. Matched results are also reported as the distribution over 100 tie-break seeds (median and range), so the primary seed cannot be suspected of being favourable.
