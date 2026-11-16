# R4-21 Pre-implementation consistency audit — PROPOSED, NOT ADOPTED

> **ADOPTION NOTICE (2026-11-16).** **ADOPTED** (C1–C6 approved by the owner). Incorporated into protocol v1.0.4, `phase3_analysis_plan.md` and `phase3_decisions.md`. The body below is unchanged history.


Prepared 16 Nov 2026. This addendum answers four specific questions about R4-17 to R4-20. **It is not a methodology revision.**
- The procedures, tests, thresholds and calibration are unchanged, except for one consistency fix (Sec. 3.3: the coverage-gap guard also applies to the H2b bound).
- Every other correction is wording or an explicit edge-case rule.
- All existing R4 files are kept as written. The corrections take effect through the amendments in Sec. 6, approved together with R4-18.

**Safeguards for this audit:** no production code changes, no commits or pushes, no test-repository access, no annotation, F1, F2 or E, and no change to protocol v1.0.3.

**Verdict: READY WITH SMALL CORRECTIONS.** No substantive blocker was found. The recommendation is to approve R4-18 **as amended by Sec. 6**, then proceed to R4-19.

## 1. Sampling strata and the H2 estimand

### 1.1 What the sampler actually produces

In each repository r, the protocol's sampler (v1.0.3 as fixed by V6/V11) works per stratum h ∈ {S1-app, S1-nonapp}:
- it puts the candidates of h in a seeded uniformly random order;
- it issues them in batches: 7 app plus min(3, cap − eligible non-app so far) non-app, with non-app issuance never past the remaining cap;
- it stops on counts of adjudicated **eligibility only**. Tool output and correctness never enter.

S2 and annotator-added sites are outside the primary set.

**Lemma (stratified simple random sample).** Fix a stratum h. Under a uniform random order, the 0/1 eligibility sequence of the issued candidates is independent of *which* eligible unit occupies each eligible position. The stopping time depends only on the 0/1 sequences. Therefore, conditional on the number m_r,h of eligible sites drawn, the eligible sites sampled from h are a uniformly random m_r,h-subset of that stratum's eligible frame U_r,h. That is, a simple random sample without replacement.

The repository sample is therefore a **stratified simple random sample with an outcome-independent, design-driven allocation**:
- non-app is limited to at most quota/3 eligible sites;
- app makes up the rest, at least 2/3 of the counted quota.

### 1.2 Two different estimands

Let Ψ(P) be the matched complete-policy functional of R4-11/R4-17: the population δ for a distribution P of sites. It is defined for any distribution of (truth, both arms' actions, tiers).

| | Definition | Weights |
|---|---|---|
| **A. Design-mixture estimand** | δ_r^A = Ψ(P_r^A), where P_r^A = Σ_h (m_r,h / n_r) · Uniform(U_r,h) | the realised design allocation (app ≥ 2/3, non-app ≤ 1/3) |
| **B. Frame estimand** | δ_r^B = Ψ(P_r^B), where P_r^B = Σ_h (N_r,h / N_r) · Uniform(U_r,h), with N_r,h the number of eligible sites in stratum h | the frame's own composition |

- A = B if the allocation happens to be proportional, or if the two strata behave identically.
- Otherwise they differ. Test, example and vendored code may well behave differently from app code.
- Because Ψ involves within-repository matching across both strata, δ^A is **not** a simple weighted average of per-stratum deltas.

### 1.3 Which one the design estimates, and whether that was stated

The unweighted estimator δ̃_r on the sample is a plug-in estimate of **δ^A**. It does not estimate δ^B.

**The intended target is A.**
- The cap was introduced deliberately (owner decisions D2/D3, v1.0.3) so that the primary set is app-dominated rather than frame-proportional.
- R4-05 Sec. 1 defines the primary population as sites "sampled by the seeded sequential sampler".

**Two sentences describe the target inaccurately:**
- R4-02 Sec. 2: "a finite population from which the sampler draws at random";
- R4-17 Sec. 3: "expectation over sites drawn at random from r's primary-set frame".

Both read as estimand B. **This is a wording defect, not a design defect.** Correcting it does not change the population. It states the weighting the design has always implied.

### 1.4 Are stratum weights or stratified resampling necessary?

- **Stratum weights: no, for A.** The unweighted estimator is the plug-in for A. Weights (N̂_h/N̂)/(m_h/n) would be needed only for B. N_r,h is unknown (it would have to be estimated from pool sizes × observed eligibility rates), and reweighting a matched, count-based functional is not a small change. **B is not adopted as a confirmatory target.**
- **Stratified resampling: not required for validity. The current within-repository resampling is conservative for A.**
  - Linearise δ̃_r as a mean of site contributions with stratum means μ_h and variances σ_h².
  - Under the fixed allocation, Var_design = (1/n²) Σ_h m_h σ_h².
  - Resampling n sites with replacement, ignoring strata, gives Var_boot ≈ (1/n²) Σ_h m_h [σ_h² + (μ_h − μ)²] ≥ Var_design.
  - The bootstrap's centre is unchanged, because the resample's expected stratum shares equal m_h/n.
  - **So the unstratified bootstrap overstates the variance by the between-stratum term: valid and conservative.**
  - Without-replacement sampling from a finite frame adds further conservatism.
  - Away from equal coverage the matched functional is locally linear in the counts. At equal coverage the guard applies (R4-13).
- **Not proven by simulation yet.** R4-13's model had no strata. **Small correction C1** adds a two-stratum scenario to the production re-calibration (R4-19 item 17): app and non-app strata with different arm behaviour and coverage, allocation 20/10, null calibrated on Ψ(P^A). It must show the unstratified bootstrap at or below nominal.
  - Exact (repository × stratum) resampling is kept as the pre-specified fallback, if that scenario failed.
  - It is not adopted now, because it would change a calibrated procedure without evidence that it is needed.

### 1.5 Corrections (wording; C1, C2)

- **C1:** the re-calibration scenario above.
- **C2, estimand wording.** In R4-02 Sec. 2, R4-17 Sec. 3, R4-14 Sec. 1 and the V12 row, the estimand reads: "… expected complete-policy correctness over the **design mixture** of each repository's primary-set eligible sites: within each stratum (S1-app, S1-nonapp) a simple random sample of eligible sites, the strata combined in the sampler's realised allocation (at least two-thirds app by the pre-registered cap)."
- **Required reporting:**
  - per repository: m_r,app and m_r,nonapp, plus the stratum pool sizes;
  - descriptive per-stratum results (δ̃ matched within repository × stratum) for app and non-app separately, so readers can see whether strata differ.
- **Same weighting elsewhere.** The same design-mixture weighting already applies to every primary-set rate (H1a, H1b, H3, F-A). No hypothesis or metric changes. The results text names the design mixture once in the methods.

## 2. Repositories with zero common evaluable sites (n_r = 0)

**Current inconsistency.**
- R4-03a and R4-14 average over "repositories with n_r ≥ 1".
- R4-17 defines the estimand over 7 repositories.
- The guard formula divides by n_r. The reference `coverage_gap` raises an error for n_r = 0, deliberately.

**Exact rule (correction C3):**

| Element | Rule when one or more repositories have n_r = 0 |
|---|---|
| Definitions | K = 7 (the named test repositories, always reported). K_e = #{r : n_r ≥ 1}, the *estimable* repositories, always reported with their names. A repository with n_r = 0 is listed with its eligible count, failure counts and failure reasons. Nothing is imputed: no δ_r = 0, no carried-forward value. |
| Confirmatory assessability | The confirmatory estimand is the average over **all 7** repositories. If K_e < 7, it cannot be estimated as pre-registered, so **H2a, H2-3 and H2-4 are "not assessable as pre-registered"** for every comparison affected. This is stricter than the feasibility gate, deliberately. A repository can be infeasible (k_r < 5) and still estimable; it cannot be unestimable and still in the estimand. |
| Estimable-repository average | Reported **separately and labelled secondary**: δ̃_e = (1/K_e) Σ_{r: n_r ≥ 1} δ̃_r, with its bootstrap p and bound computed over the K_e repositories and the guard computed as below. Never presented as the confirmatory result. |
| Coverage-gap guard | g_e = (1/K_e) Σ_{r: n_r ≥ 1} (R_F,r − R_M,r)/n_r, an exact fraction over the estimable repositories (the same set the estimate uses); doubling iff g_e < 1/10. When K_e = 7, g_e = g. |
| Feasibility gate | unchanged. A repository with n_r = 0 has k_r = 0 and counts as not feasible. Pooled Σk/Σn is unaffected (it adds 0/0 to neither sum). |
| Bootstrap | resamples only repositories with n_r ≥ 1 (an empty repository cannot be resampled) |
| Reporting line | "K = 7; estimable K_e = x (non-estimable: <names, reasons>)" next to every pooled H2 figure |

**Likelihood and owner alternative.**
- n_r = 0 requires every sampled eligible site of a repository to lie in files the analyser cannot read or parse. This has **not** been checked for the test split (it has not been accessed, and the qualification records `docs/benchmark/candidate_verification*.md` contain no parseability check). It is improbable for maintained Python 3 projects, but unverified. The strict rule protects the estimand either way.
- The Phase DV run (R4-20 D6) shows the parse-failure rate on the 6 development and validation repositories before F1.
- **Owner alternative:** treat K_e ≥ 5 as confirmatory, with the claim restricted to the named estimable repositories. This is not recommended: the estimand would then be set after seeing a property of the test tools' behaviour.

**Implementation note (no change now).** The production `coverage_gap` and bootstrap take the estimable set explicitly. The reference raising on n_r = 0 stays as the guard against silent division (R4-19 items 11–12).

## 3. H2a / H2b reporting

### 3.1 Error properties of the current combined statement

R4-17 Sec. 2.3 allows "H2 supported" when A ∧ B holds:
- A: H2a is claimable (Holm-rejected in F-B, gate passed);
- B: the H2b lower bound L > 0.10.

- **H2-1 on its own.** For any true δ ≤ 0.10, P(A ∧ B) ≤ P(B). B on its own is a one-sided level-0.025 test of H0: δ ≤ 0.10 (calibrated: 0.0097 at the boundary, R4-13 S17). So the combined statement is protected at about 0.025 *for H2-1 on its own*.
- **Across the confirmatory family.** False claims can arise from F-B (H2-1, H2-3, H2-4) **or** from B. A union bound gives P(any false claim) ≤ 0.025 + 0.025 = **0.05**. That exceeds the family level V17 promises.
- **Conclusion.** The phrase "H2 supported" would put a confirmatory label on a statement partly outside family-wise control. It is **not adequately protected at the family level** and is withdrawn.

### 3.2 Revised wording (correction C4; replaces R4-17 Sec. 2.3)

Two statements are always reported separately, with their status.

| Statement | Values | Basis | Status words required |
|---|---|---|---|
| **H2a, direction** (comparison H2-1) | "supported", "not supported", or "not assessable (as pre-registered / at equal coverage)" | Holm-adjusted guarded p ≤ 0.025 and gate passed (Sec. 2 rules) | "confirmatory" |
| **H2b, 10-point criterion** (comparison H2-2) | "met" or "not met" | guarded one-sided lower bound > 0.10 (Sec. 3.3) | "exploratory, pre-specified; not under family-wise error control" |

- **The unqualified phrase "H2 supported" is not used** anywhere in results, abstract or conclusions.
- **Traceability to the frozen H2.** A fixed table in the methods: "Frozen H2 (v1.0.3) = H2a (direction, confirmatory) + H2b (≥ 10 points, exploratory)."
- **Discussion sentence** permitted only when H2a is supported **and** H2b is met: "The 10-point improvement stated in the original H2 was also met in the pre-specified exploratory analysis, which is not covered by the family-wise error control."
- **When only H2a is supported:** "H2a supported; the 10-point improvement of the original H2 was not established."
- **A significant H2a never yields a 10-point statement.**
- **Abstract template (R4-17 Sec. 2.5):** "[The pre-registered 10-point improvement was / was not established.]" becomes "[The 10-point improvement of the original hypothesis was / was not met in a pre-specified exploratory analysis.]"
- **Owner alternative (unchanged, V10a-alt).** Holm m = 4 including H2-2. Then "H2 supported" may be used when H2-1 and H2-2 are both Holm-rejected and the gate passes, at the cost of near-zero power for H2-2.

### 3.3 Consistency fix (correction C5): the guard also applies to H2b

- **The gap.** The guard exists because the percentile bootstrap is liberal near equal natural coverage. That applies equally to the margin bound, and R4-17 Sec. 4.2 step 10 omitted it.
- **Rule.** H2b uses the guarded margin p: p_m = (1 + #{δ* ≤ 0.10})/(B + 1), and H2b is met iff p*_m = min(1, 2·p_m) ≤ 0.025. Equivalently, when the guard is active the bound used is the one-sided **98.75%** lower bound; when inactive, the 97.5% bound.
- **Scope.** This only makes H2b stricter near equal coverage. It needs no new calibration: it is the same guard, on the same bootstrap, tested at S17 and in the near-kink cells.

## 4. Experiment A (F-A): pooled exact McNemar with Holm

**Setting.** For each baseline j (≤ 8), the proposed system (full at T2) is compared with j at **natural coverage**, with no matching:
- the paired set is the sites where both ran;
- the test is a one-sided exact McNemar on the pooled discordant pairs b_j, c_j;
- Holm is applied across j at family α = 0.025 (V17; R4-02 Sec. 6).

**Estimand.** δ_j = site-weighted difference in correct-per-eligible over the design-mixture sample of the 7 fixed repositories (Sec. 1), restricted to sites where both methods ran.

| Concern | Assessment |
|---|---|
| Seven fixed repositories | Inference concerns these repositories only (V13 scope). Repositories are fixed strata, not sampled units, so no between-repository variance enters the fixed-repository estimand. |
| Stratified / sequential sampling | By the Sec. 1.1 lemma, the sites are stratified simple random samples drawn with an outcome-independent stopping rule. Conditional on the allocation, the per-site pairs (X_i, Y_i) are independent draws within their stratum. |
| Within-repository site dependence | Sites that share code patterns are *population* structure. Under random sampling of sites, the sampled units are exchangeable draws, not a dependent series. Without-replacement sampling makes them weakly negatively correlated, which is conservative. Dependence would matter only for generalisation beyond the 7 repositories, which is not claimed. |
| Heterogeneity across repositories and strata | Under the pooled null E[b − c] = 0, the count of full-arm wins among D discordant pairs is Poisson-binomial with mean D/2. Its variance is at most the binomial variance McNemar assumes, so heterogeneity makes the exact test **conservative**, not liberal. This matches revision 4's simulations: worst site-level Type I 0.0225 at nominal 0.025 in the fixed-repository mode (R4-02 Sec. 5; `results/h2_type1.csv`). |
| Unequal evaluable denominators | Each comparison has its own both-ran set, so the estimands differ by baseline: "on sites where both ran". External tools fail on different files, and exclusion can favour a tool that crashes on hard files (R4-12 Sec. 2). **Required:** per-comparison denominators; the S-F1 and S-F2 failure sensitivities shown next to each F-A result; the repository-balanced difference reported alongside the site-weighted one. |
| Multiple baselines | Holm controls FWER under arbitrary dependence among the ≤ 8 tests. That is valid, though the common proposed-system outcome correlates them. |
| No matching | So none of the matching-induced dependence of H2 applies, and no guard is needed. |
| Effect-size intervals | v1.0.3's "cluster bootstrap by repo" is exploratory only (V13/V24). The F-A difference CI uses the stratified within-repository bootstrap (sites resampled within repositories). |

**Conclusion.** F-A's pooled exact McNemar with Holm **is defensible for the fixed-repository, design-mixture, both-ran estimand**, and conservative under heterogeneity. No method change is needed.

**Correction C6** documents the assumptions in the F-A row of R4-17 Sec. 6.2 and in protocol v1.0.4 Sec. 5:
1. fixed repositories;
2. stratified random sampling of sites with outcome-independent stopping;
3. independence of the sampled pairs;
4. the estimand restricted to both-ran sites;
5. mandatory failure sensitivities.

**Frozen hypotheses.** H1, H3 and H4 are untouched. Their rates are design-mixture quantities, stated once in the methods (Sec. 1.5); their thresholds and decision rules are unchanged.

## 5. Affected documents and sections

| Correction | Documents and sections (edited only after approval, with the R4-16 edits) |
|---|---|
| C1: two-stratum re-calibration scenario; stratified-resampling fallback | R4-19 item 17 acceptance; R4-20 D7 |
| C2: estimand = design mixture; stratum allocation and per-stratum descriptive reporting | R4-02 Sec. 2; R4-17 Sec. 3; R4-14 Sec. 1 and 3; R4-05 Sec. 1 (reporting line); protocol v1.0.4 Sec. 1 and 5 |
| C3: n_r = 0 rule (K, K_e, not assessable as pre-registered; estimable average secondary; g_e) | R4-03a Sec. 5 and 7; R4-12 Sec. 3; R4-14 Sec. 1; R4-17 Sec. 2.3, 2.5, 4.1, 5; R4-19 items 10–12 |
| C4: separate H2a / H2b statements; "H2 supported" withdrawn; traceability table; abstract template | R4-17 Sec. 2.3–2.5; R4-07 Sec. 1; R4-02 Sec. 4; protocol v1.0.4 Sec. 1 |
| C5: guarded H2b (98.75% bound when the guard is active) | R4-17 Sec. 4.2 step 10; R4-03a Sec. 6 item 8; R4-14 S1; R4-19 item 11 |
| C6: F-A assumptions and reporting | R4-17 Sec. 6.2; R4-02 Sec. 6 (F-A); R4-12 Sec. 4 (already mandates the sensitivities); protocol v1.0.4 Sec. 5 |

## 6. Does R4-18 need modification? Yes: wording-level amendments to five rows

Approve R4-18 **as amended here**. R4-18 itself stays as written; this table is the amendment record.

| R4-18 row | Amendment |
|---|---|
| **V10a** | Replace "'H2 supported' only if H2a is claimable AND H2b's 97.5% lower bound > 0.10" with: "H2a (confirmatory direction) and H2b (exploratory 10-point criterion) are always reported as two separate statements with their status. The unqualified phrase 'H2 supported' is not used. Traceability table and wording per R4-21 Sec. 3.2." The V10a-alt (m = 4) is unchanged. |
| **V10b** | Add: "H2b uses the guarded margin p (R4-21 Sec. 3.3)." Add the F-A assumptions sentence (R4-21 Sec. 4, C6). |
| **V12** | Estimand wording per C2 (design mixture). Add per-stratum allocation and descriptive per-stratum results to the reporting. |
| **V13** | Add: "Confirmatory estimation requires K_e = 7; otherwise not assessable as pre-registered, with the estimable-repository average reported as secondary (R4-21 Sec. 2)." Add C1 to the re-calibration requirement. |
| **V21 / V22** | Add the K / K_e reporting line; g_e over the estimable repositories; no imputation (R4-21 Sec. 2). |

**No other row changes.** None of these amendments changes a frozen hypothesis sentence, metric definition, threshold, α, arm, matching rule or test statistic. C5 makes one exploratory criterion stricter near equal coverage.

## 7. Verdict and recommendation

**READY WITH SMALL CORRECTIONS.** All six corrections:
- are wording, edge-case rules or one added calibration scenario (C1–C6);
- leave the target population, hypotheses, metrics and confirmatory test unchanged;
- add no new methodology revision.

**Recommendation:**
1. Approve R4-18 as amended by R4-21 Sec. 6.
2. Claude then:
   - writes protocol v1.0.4 and guide v1.1 (V24) including C1–C6;
   - proceeds to the R4-19 implementation in small, tested commits, each on your approval to commit.
