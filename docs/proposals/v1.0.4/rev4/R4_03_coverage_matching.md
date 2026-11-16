# R4-03 Equal-coverage comparison for H2 — PROPOSED, NOT ADOPTED (final V12″ methodology)

**Earlier versions, preserved:**
- `superseded/R4_03_coverage_matching_as_reviewed.md`: the version the owner reviewed;
- `superseded/R4_03_coverage_matching_after_audit1.md`: the version after the first R4-03 audit.

This version implements R4-11 (final V12″ audit).

| Topic | Document |
|---|---|
| algorithm | R4-03a |
| execution failures | R4-12 |
| calibration | R4-13 |
| metrics | R4-14 |
| decisions | R4-15 |
| cross-document check | R4-16 |

## 1. Definitions (frozen; unchanged)

- **Coverage** = RECOMMEND / eligible sites. FLAG_NO_TARGET and ABSTAIN are not coverage.
- **Correct-per-eligible-site** = CORRECT / sites, under scoring policy v1.0 (`pqscan.bench.judge`). The full table is in `results/scoring_table_v4.md`.
- **Common evaluable set C_r:** the primary-set eligible sites of repository r where both arms ran (R4-12). Failures are listed and analysed in sensitivity analyses, never dropped from reporting.

## 2. Comparisons (V18′)

All arms run at threshold T0, with UNKNOWN roles abstaining:

| Comparison | Arms | Status |
|---|---|---|
| H2-1 | full vs. method+args | confirmatory direction; margin exploratory |
| H2-3 | full vs. method+args+recv | confirmatory |
| H2-4 | full vs. method-only | confirmatory |
| H2-S | full at T2 vs. method+args at T0 | secondary |

## 3. Matching (V12″)

Separately for each comparison and each repository, on C_r:
1. k_r = min(R_F,r, R_M,r).
2. The arm with more RECOMMENDs withdraws the excess: lowest evidence tier first, then SHA-256 order within a tier.
3. A withdrawn RECOMMEND becomes ABSTAIN and is judged by the frozen judge.
4. Recommendation **counts** become equal; the recommended **sites** generally differ.
5. No label is read. The matching output is hashed before scoring.

## 4. What is measured

**Primary endpoint:** complete-policy correctness at equal recommendation volume. Every site decision counts: recommend, flag no target, or abstain. A withdrawal on an indeterminate site becomes a correct abstention.

**Recommendation precision** (correct RECOMMENDs / k) is reported separately and never substituted for the primary endpoint (R4-14).

**Development pilot** (circular, not a result; `results/pilot_v12pp.md`):
- matched δ̃ is +0.059 (repository-balanced), against +0.380 unmatched;
- both arms' matched recommendations are 100% correct;
- the difference comes from FLAG_NO_TARGET.

## 5. Estimate

- **δ̃_r:** the exact expectation over all permitted tie orders. It is computed in closed form, O(n).
- **δ̃:** the repository-balanced mean of δ̃_r (primary).
- **Site-weighted mean:** secondary. It differs from δ̃ whenever the common n_r differ.
- **Seeded table:** the per-site table with tie seed `20261113` and the 100 sensitivity seeds are reported, but they do not drive the result.

## 6. Inference (V13″, V20, V10b‴)

- **Test:** the stratified re-matching percentile bootstrap (B = 10,000, seed 20261113). Sites are resampled within repositories, and every step is repeated in each resample, **with random tie keys inside each resample**.
- **Guard:** g = (1/K) Σ_r (R_F,r − R_M,r)/n_r. If g < 1/10, p → min(1, 2p).
- **Holm:** m = 3 over H2-1, H2-3 and H2-4 at one-sided family α = 0.025.
- **Monte Carlo rule:** if p is within 3 MC-SE of the threshold it is compared to, the run is repeated with B = 100,000.
- **Calibration (R4-13):** the procedure is at or below nominal in 17 fixed-repository scenarios at all Holm levels, and at nominal within MC error at exactly equal coverage. It is not valid for generalisation.

## 7. Feasibility (V21)

- **Feasible repository:** k_r ≥ 5.
- **Gate:** pooled matched coverage ≥ 0.20 and ≥ 5 of 7 repositories feasible.
- **If the gate fails:** the comparison cannot support an H2 claim; it is "not assessable at equal coverage".
- **Every repository stays in the estimand.** Zero-matched-coverage repositories contribute their non-recommendation difference.
- **Phase DV check:** before F1.

## 8. Secondary and sensitivity analyses

R4-14 Sec. 2:
- natural coverage;
- matched and natural precision;
- the decomposition;
- harmful, undecided and unjustified rates;
- ranking-free matching;
- the seeded tables and the 100-seed distribution;
- the fixed-target V12-B;
- feasible repositories only;
- the failure sensitivities;
- H2-S;
- repository-level exploratory analyses;
- the exploratory cluster-by-repository CI;
- strict scoring.
