# R4-03a Equal-coverage matching: implementation specification — PROPOSED, NOT ADOPTED

Status: proposal for owner approval (V12″). **Updated after the final V12″ audit (R4-11).** The version before that audit is in `superseded/R4_03a_matching_implementation_spec_after_audit1.md`.

The changes in this update:
- **Point estimate.** The exact tie-average δ̃ is the primary point estimate.
- **Execution failures** follow R4-12.
- **Guard.** It is defined exactly, on the signed repository-balanced gap.
- **Bootstrap.** It keeps random tie keys inside each resample. Bootstrapping δ̃ itself was tested and rejected (R4-13).
- **Gate.** Its handling of repositories with no common sites is specified.

Production code (`pqscan/bench`, checklist items B4–B6) is written only after approval.
- **Reference implementation:** `scripts/matching_ref_v4.py`.
- **Tests:** 29 in `scripts/test_matching_ref_v4.py` and 26 in `scripts/test_v12pp.py`.

Protocol v1.0.3, guide v1.0 and scoring policy v1.0 are unchanged and remain in force.

## 1. Comparisons and identifiers

The hypothesis IDs B1–B4 in R4-02 collide with the baseline names in `pqscan/baselines/simple.py` (B1-algorithm, B2-method-args, B3-full-noabst, B4-full-T2). R4-02's B1 compares the code's B3-full-noabst with B2-method-args. This specification therefore uses comparison IDs:

| Comparison ID | R4-02 ID | Arm F (provenance-aware) | Arm M (comparator) | Thresholds |
|---|---|---|---|---|
| `H2-1` | B1 (direction) and B2 (margin) | Module C `full` | `method+args` | both T0 (V18) |
| `H2-3` | B3 | `full` | `method+args+recv` | both T0 |
| `H2-4` | B4 | `full` | `method-only` | both T0 |
| `H2-S` | secondary | `full` at T2 (proposed system, code `B4-full-T2`) | `method+args` at T0 | as stated |

## 2. Inputs

For each comparison and each test repository r:
- **Paired set = common evaluable set C_r (R4-12).** These are the primary-set eligible sites of r (R4-05 Sec. 1), with owner-final labels, where **both** arms ran.
  - Sites where either arm has `EXECUTION_FAILURE` are removed before matching, listed, and kept in the failure sensitivity analyses S-F1 and S-F2.
  - For the H2 arms, failures must be concordant (shared parser). A discordant failure stops the run.
  - Ineligible sites never enter.
- **Per site and arm:** `action` ∈ {RECOMMEND, FLAG_NO_TARGET, ABSTAIN, NO_FINDING}, `rec_class`, and `evidence_tier` ∈ {T0, T1, T2, T3}, from the tool result record (`data_dictionary.md` Sec. 2).
- **Matching reads only:** site_id, action and tier. Labels are read only afterwards, by the scorer.

**Validation.** Any failure stops the run; nothing is silently repaired.
- duplicate site_id;
- an action outside the list;
- `EXECUTION_FAILURE` still present;
- a RECOMMEND without a tier in T0–T3;
- a RECOMMEND with rec_class NONE;
- an ineligible site in the paired set.

## 3. Matching algorithm (per comparison, per repository; label-free)

1. R_F = number of RECOMMENDs of arm F on the paired set; R_M likewise. k_r = min(R_F, R_M).
2. If R_F = R_M, nothing is withdrawn. Otherwise the arm with more RECOMMENDs (the *withdrawing arm*) withdraws e = |R_F − R_M| of its RECOMMENDs.
3. **Withdrawal order:**
   - ascending evidence tier (T0 < T1 < T2 < T3);
   - within a tier, ascending `SHA-256("<seed>|<comparison ID>|<repository>|<site_id>")`, as lowercase hex, UTF-8.
   - The primary seed string is `20261113`.
   - The hash order does not depend on numpy or Python versions.
4. **A withdrawn RECOMMEND becomes `ABSTAIN`** with rec_class NONE. Its tier is kept for the record, and the site is flagged `matched_withdrawn = true`.
5. **Untouched actions:** FLAG_NO_TARGET, ABSTAIN and NO_FINDING are never changed. The other arm is never changed.
6. **Assertion:** after matching, both arms have exactly k_r RECOMMENDs in r.

**What is equal and what is not:**
- Recommendation **counts** are equal within every repository, and therefore pooled.
- The **identities** of the recommended sites generally differ. Example 2 (`results/worked_example_v4.md`): after matching, both arms recommend on 5 of 12 sites, but they share only 2 of them.
- No step reads ground-truth labels.
- Matching is done independently for each repository and for each comparison. The full arm's matched outputs can therefore differ between H2-1, H2-3 and H2-4.

## 4. Scoring

Every matched output is scored by the frozen `pqscan.bench.judge.judge` (scoring policy v1.0). The pre-registered strict variant is scored by `strict_judgment`. The full action × ground-truth table, generated from `judge`, is in `results/scoring_table_v4.md`. The audit, R4-03 final Sec. 3, explains its consequences.

## 5. Estimators reported for each comparison

For repository r with n_r paired sites, X_i and Y_i are the frozen CORRECT indicators of F and M after matching.

| Quantity | Definition | Role |
|---|---|---|
| δ̃_r | exact expectation of (Σ X_i − Σ Y_i) / n_r over all permitted tie orders. Each boundary-tier recommendation of the withdrawing arm is withdrawn with probability j/m. `tie_average_delta`; O(n); exact because the difference is linear in the withdrawal indicators. | **primary per-repository estimate** |
| δ̃ | (1/K) Σ_r δ̃_r: repository-balanced over the repositories with n_r ≥ 1 | **primary point estimate** |
| δ̃_site | Σ n_r δ̃_r / Σ n_r. It equals δ̃ only when every common n_r is equal. | secondary |
| δ_r(seed) | (Σ X_i − Σ Y_i) / n_r with ties broken by the seed-`20261113` SHA-256 order | per-site table, b/c, McNemar (secondary) |
| decomposition | δ split by the final action each arm took: REC, WITHDRAWN, FLAG, ABSTAIN, NO_FINDING | required, every comparison |
| matched precision | CORRECT RECOMMENDs / k, per arm, pooled | "recommendation correctness at equal coverage" |
| frozen recommendation correctness | CORRECT / (eligible DETERMINATE sites with RECOMMEND), per arm (`data_dictionary.md` Sec. 4) | reported unchanged |
| natural δ | the same without matching | secondary |
| harmful, undecided, unjustified rates after matching | per scoring policy | secondary |

## 6. Confirmatory test (H2-1, H2-3, H2-4)

**Stratified re-matching bootstrap; repositories fixed; sites resampled within repositories (common evaluable sets).**

Inside each resample, ties are broken by fresh uniform keys. That averages over tie orders *in distribution*, and this randomisation is deliberate. A bootstrap of the exact tie-averaged estimate itself (no keys) was calibrated and **rejected**: it is liberal when tiers are flat (0.0293 at a nominal 0.025) and near equal coverage even with the guard (R4-13 Sec. B). The point estimate reported with the test is δ̃.

1. **Resampling.** For b = 1..B, for each repository r in ascending repository-name order:
   - draw n_r site indices with replacement;
   - then draw n_r uniform tie keys for arm F and n_r for arm M.
2. **Recomputation in each resample.** Each resample recomputes:
   - R_F*, R_M* and k_r*;
   - the withdrawal by tier, using the resample's uniform keys within a tier;
   - the frozen scores (withdrawn → the ABSTAIN judgment);
   - δ_r*.

   Then δ* = mean over r of δ_r*.
3. **Random number generator.** numpy `default_rng(20261113)`, PCG64, one generator per comparison, created fresh. B = 10,000, drawn in chunks of 2,000 in the order above.
4. **p-value (percentile; as specified in R4-02 Sec. 5).** For H0: δ ≤ d0, p = (1 + #{δ* ≤ d0}) / (B + 1). The "basic" (reverse-percentile) variant was calibrated and rejected: it is liberal in several scenarios (`results/calib_matching.md` Sec. B; R4-03 final Sec. 6).
5. **Coverage-gap guard (pre-registered; label-free).**
   - **Signed gap.** g = C_full − C_comparator = (1/K) Σ_r (R_F,r − R_M,r) / n_r. It is computed on the natural outputs over the common evaluable sets, repository-balanced like the estimand, as an **exact rational number** (`coverage_gap`).
   - **Activation.** The guard is active iff **g < 1/10**:
     - negative g: active;
     - g = 0: active;
     - 0 < g < 0.10: active;
     - g = 0.10 exactly: **not** active;
     - g > 0.10: not active.
   - **Effect.** When active, the comparison's p-value enters Holm as min(1, 2p). That halves every Holm threshold for that comparison.
   - **Reason.** The percentile re-matching bootstrap is liberal when the comparator's natural coverage is close to, or above, the full arm's (R4-13 Sec. B).
6. **Holm.** The (guarded) p-values of H2-1, H2-3 and H2-4 enter Holm m = 3 at one-sided family α = 0.025 (R4-02 Sec. 6).
7. **Monte Carlo rule (pre-registered).** If |p − threshold| < 3·√(p(1 − p)/B) at the Holm step where p is compared, the bootstrap is re-run with B = 100,000 and the same seed. That result is final.
8. **Margin (H2-1 at d0 = 0.10; exploratory).** The same bootstrap distribution gives the one-sided 97.5% lower bound (the 2.5th percentile of δ*).
9. **Ranking-free sensitivity (pre-registered).** The whole analysis is repeated with withdrawal in SHA-256 order alone, ignoring tiers. This shows how much of the matched difference depends on the arms' own tier ranking (R4-03 final Sec. 5).

**Why repositories are not resampled.** The estimand concerns the 7 fixed repositories (R4-04). Resampling 7 purposively chosen repositories would target a population that does not exist in the design, and is unreliable at K = 7.

## 7. Feasibility gate (pre-registered; label-free)

Applied after matching on the test split, per comparison, before any label is joined to tool outputs:
- **Repository flag:** r is *matching-feasible* if k_r ≥ 5.
- **Gate:** passes if pooled matched coverage Σk_r / Σn_r ≥ 0.20 **and** at least 5 of the 7 repositories are matching-feasible.
- **Consequence if the gate fails:**
  - the comparison's bootstrap p-value is still computed and reported;
  - but it cannot support an H2 claim: R4-02 Sec. 4's "H2 direction supported" requires the gate to pass;
  - the result is reported as "H2 not assessable at equal coverage in these repositories (matched coverage too low)".
- **Never:**
  - repositories are not dropped from the confirmatory estimand;
  - no threshold is changed after test access.
- **Descriptive extra:** the same analysis restricted to matching-feasible repositories is reported.
- **Denominators.** n_r is the common evaluable count (R4-12).
- **A repository with n_r = 0:**
  - it counts as not feasible;
  - it is listed with its failure counts;
  - it cannot contribute δ_r: the repository-balanced mean is over the repositories with n_r ≥ 1, and this is printed with the estimate.
- **A repository with k_r = 0** contributes its δ̃_r (non-recommendation actions only) to the estimate and the bootstrap. It is reported as "matched coverage 0".

The thresholds, their justification and their Phase DV check are in the audit, R4-03 final Sec. 4.

## 8. Seeds

- **The primary analysis has no tie-break seed.**
  - The point estimate δ̃ is the exact expectation over all tie orders.
  - The p-value comes from the bootstrap, which draws its own tie keys from the bootstrap generator (seed 20261113).
  - Neither depends on any observed tie order (unit tests `test_bootstrap_p_does_not_depend_on_the_observed_tie_break_seed`, `test_tie_average_equals_brute_force_over_all_orders`).
- **Seed `20261113` (SHA-256 order)** is used only to build the binary per-site table: X/Y, b, c, site-level McNemar and Tango (secondary).
- **Sensitivity seeds `20261113-S001` … `S100`.** They are fixed in advance and reported only as the distribution of the seeded estimate δ(seed): median, minimum, maximum and the full histogram, per comparison and repository. The site-level McNemar p is reported alongside.
- **No seed is chosen for its result.** No seed can change the confirmatory decision.
- **The bootstrap seed** is fixed at 20261113. Its Monte Carlo error is controlled by the rule in Sec. 6.7, not by trying other seeds.

## 9. Outputs (written before labels are joined, then completed after scoring)

- `matched_<comparison>_<repo>.jsonl`, one record per paired site:
  - site_id;
  - for each arm: natural action, rec_class and tier;
  - matched action and `matched_withdrawn`;
  - withdrawal rank;
  - tie key;
  - then the judgments and X/Y after scoring.
- `matching_summary_<comparison>.md`, per repository:
  - n_r, R_F, R_M, k_r;
  - natural and matched coverage;
  - boundary tier, tied count and withdrawn count;
  - overlap (both / F only / M only);
  - the feasibility flag.

  Pooled: the gate result.
- **Hashing.** The label-free part (everything except judgments) is hashed and recorded before scoring, so the matching provably did not depend on labels.

## 10. Tests required for the production implementation

All behaviours tested in `scripts/test_matching_ref_v4.py`:
- equal counts and k = min;
- at most one arm withdraws;
- k = 0; both zero; equal counts;
- the comparator withdrawing;
- tier order;
- SHA-256 ties;
- seed changes the identities but not the count;
- input order invariance;
- label-freeness;
- only RECOMMEND is withdrawn;
- validation errors;
- ineligible sites rejected;
- withdrawn → ABSTAIN judgment through the frozen judge;
- δ = (b − c)/n;
- the decomposition sums;
- the worked example reproduced;
- the exact tie-average equals the brute-force mean;
- the vectorised core equals the reference;
- every bootstrap resample exactly matched with lowest-tier-first;
- bootstrap determinism and tie-seed invariance;
- identical arms give p = 1.

The production module must also reproduce `results/worked_example_v4.md` and `results/pilot_matching_v4.md` exactly.
