# Phase 3 analysis plan for H2 and Experiment A (v1.0.1; v1.0 adopted 2026-11-16, corrected 2026-11-18)

**Status.** Normative companion of `evaluation_protocol.md` v1.0.5. v1.0 was adopted by owner decision (R4-18 as amended by R4-21 Sec. 6), before any test-split access. v1.0.1 (18 Nov 2026, before any labelling and any test-split access) applies the owner-approved pre-F1 decision register (`docs/audit/owner_decision_register_v1.0.5.md`); see the Changelog. The v1.0 text is kept in `docs/specification/archive/v1.0.4/phase3_analysis_plan.md`.

**Sources.** It consolidates, without methodological change:
- R4-03a (matching specification);
- R4-12 (execution failures);
- R4-14 (metrics);
- R4-17 Sec. 2–5 (sequence, reporting);
- R4-21 corrections C1–C6;
- the owner's edge-case rules A–D of 16 Nov 2026.

The proposal history is in `docs/proposals/v1.0.4/`.

**Implementation.**
- **Production:** `pqscan/bench/` (implementation hand-off R4-19).
- **Independent reference:** `docs/proposals/v1.0.4/rev4/scripts/matching_ref_v4.py`, which must stay separate.
- **Scoring:** always by the frozen `pqscan.bench.judge.judge` (scoring policy v1.0).

## 1. Comparisons

| ID | Provenance-aware arm F | Comparator M | Status | Family |
|---|---|---|---|---|
| H2-1 | `full`, threshold T0 | `method+args`, T0 | confirmatory (H2a) | F-B |
| H2-2 | the same pair | | exploratory (H2b, margin 0.10) | none |
| H2-3 | `full`, T0 | `method+args+recv`, T0 | confirmatory | F-B |
| H2-4 | `full`, T0 | `method-only`, T0 | confirmatory | F-B |
| H2-S | `full`, T2 | `method+args`, T0 | secondary | none |
| F-A(j) | `full`, T2 (proposed system) | baseline j as run | confirmatory | F-A |

**Arm rules (H2):**
- **UNKNOWN roles abstain.**
- **Shared evidence:** all arms of a comparison are derived from **the same per-file evidence** (one parse per file).

## 2. Study population and estimand (R4-21 C2)

**Sampling.** Within each repository r and S1 stratum h ∈ {app, nonapp}:
- the sampler issues candidates in a seeded uniformly random order;
- it stops on eligibility counts only.

Conditional on the number m_r,h of eligible sites drawn, they are a simple random sample of that stratum's eligible frame U_r,h. Reason: under a uniform order, the 0/1 eligibility sequence is independent of which eligible unit occupies each eligible position.

**Estimand A (adopted; the design mixture; denominator corrected in v1.0.1, F04).** With m_r = Σ_h m_r,h = |E_r| (the sampled primary set, Sec. 3):
- w_r,h = m_r,h / m_r;
- P_r^A = Σ_h w_r,h · Uniform(U_r,h);
- δ_r^A = Ψ(P_r^A), where Ψ is the matched complete-policy functional of Sec. 4–5;
- δ^A = (1/7) Σ_r δ_r^A.

v1.0 wrote the weights as m_r,h / n_r. With n_r = |C_r| (Sec. 3) those weights add up to m_r / n_r ≥ 1 whenever a site fails; the intended denominator is m_r.

**What the primary estimator describes when execution failures exist (v1.0.1; owner decision F04, Option 1).** Let U^ev_r,h ⊆ U_r,h be the sites where both arms run, ρ_r,h = |U^ev_r,h| / |U_r,h| and π_r = Σ_h w_r,h ρ_r,h. Then:
- P_r^ev = Σ_h (w_r,h ρ_r,h / π_r) · Uniform(U^ev_r,h), δ_r^ev = Ψ(P_r^ev) and δ^ev = (1/7) Σ_r δ_r^ev;
- the **primary estimate δ̃_r, computed on C_r, estimates δ_r^ev**: the design mixture over the **commonly evaluable** sites, with stratum weights c_r,h / n_r, where c_r,h = |C_r ∩ stratum h|;
- **S-F1 (Sec. 6) is a separate sensitivity analysis over the sampled primary set E_r**, under the rule that a site where both arms fail (a concordant execution failure) is incorrect for both arms. It estimates π_r · δ_r^ev, which is δ_r^A under that rule (failed sites carry no recommendation for either arm, so matching is unchanged; for H2, S-F1 = (n_r / m_r) · δ̃_r);
- **the two coincide** for repository r if and only if no eligible site fails (π_r = 1; then C_r = E_r and c_r,h = m_r,h). **They differ whenever a site fails:** within a repository by the factor π_r; across repositories δ^A = (1/7) Σ_r π_r δ_r^ev reweights repositories, so the pooled sign and the H2b margin can differ; the stratum mix also shifts when failures differ between strata;
- the primary C_r estimate is **never** described as measuring the full design mixture when failures exist, and the two are never claimed identical then. When any failure exists, the primary value, S-F1 and S-F2 are reported side by side;
- no estimator, bootstrap, matching rule or calibration changes: the calibration (Sec. 11) simulated no failures (π_r = 1).

**Estimand B (frame-proportional).** Weights N_r,h / N_r. It is **not** estimated or claimed.

**Required reporting:**
- per repository: m_r,app and m_r,nonapp, and the S1-app and S1-nonapp pool sizes;
- per repository and stratum (v1.0.1): m_r,h (sampled primary set) next to c_r,h (common evaluable set), and the execution failures by stratum and partition (F only, M only, neither);
- descriptive per-stratum results: δ̃ matched within (repository × stratum), for app and non-app separately.

**Bootstrap.** Resampling sites within repositories, ignoring strata, is conservative for A: its variance adds the between-stratum term Σ_h m_h (μ_h − μ)²/n². It is the adopted bootstrap, subject to the two-stratum acceptance check (Sec. 11). The pre-specified fallback is resampling within (repository × stratum) cells, with matching still done per repository.

## 3. Inputs and the common evaluable set

For comparison c and repository r:
- **E_r:** the primary-set eligible sites of r, with owner-final labels.
- **Per site and arm:** `action` ∈ {RECOMMEND, FLAG_NO_TARGET, ABSTAIN, NO_FINDING, EXECUTION_FAILURE}, `rec_class` and `evidence_tier` ∈ {T0, T1, T2, T3}.
- **C_r:** the sites of E_r where **both** arms ran (common evaluable set); n_r = |C_r| and m_r = |E_r|.

**Validation (any failure stops the run):**
- duplicate site_id;
- an action outside the list;
- a RECOMMEND without a tier in T0–T3;
- a RECOMMEND with rec_class NONE;
- an ineligible site;
- for the Module C arms of H2, a **discordant** EXECUTION_FAILURE (one arm failed, the other ran on the same site). That is treated as a software defect.

## 4. Matching (V12), label-free

For each comparison, each repository, on C_r:
1. R_F,r and R_M,r are the RECOMMEND counts. k_r = min(R_F,r, R_M,r).
2. If they differ, the arm with more RECOMMENDs withdraws the excess:
   - ascending evidence tier (T0 < T1 < T2 < T3);
   - within a tier, ascending SHA-256 of `"<seed>|<comparison>|<repository>|<site_id>"` (UTF-8, lowercase hex).
3. A withdrawn RECOMMEND becomes ABSTAIN (rec_class NONE, tier kept for the record) and is judged by the frozen judge. No other action and no other arm is changed.
4. Assert that both arms then have exactly k_r RECOMMENDs.
5. The matching output (everything except the judgments) is hashed **before** labels are joined.

**Equal volume ≠ same sites.** Equal recommendation **counts** per repository never mean identical recommended sites. Every table shows "recommended by both / F only / M only".

## 5. Estimators

| Quantity | Definition | Role |
|---|---|---|
| δ̃_r | exact expectation of (ΣX − ΣY)/n_r over all permitted tie orders: each boundary-tier recommendation of the withdrawing arm is withdrawn with probability j/m (closed form, O(n)) | primary, per repository |
| δ̃ | (1/K_e) Σ_{r ∈ estimable} δ̃_r, repository-balanced. Confirmatory only when K_e = 7 (Sec. 7.4). | **primary point estimate** |
| δ̃_site | Σ n_r δ̃_r / Σ n_r. It equals δ̃ only if every n_r is equal. | secondary, always printed |
| seeded table | matching with seed string `20261113`: binary X/Y per site, b, c, site-level exact McNemar and Tango | secondary illustration |
| 100-seed distribution | δ for seeds `20261113-S001` … `20261113-S100`: minimum, median, maximum, histogram | sensitivity |
| ranking-free δ̃ | withdrawal uniformly at random over all RECOMMENDs of the withdrawing arm, tiers ignored; exact average (probability e/R) | sensitivity: primary minus ranking-free = value of the tier ranking |
| decomposition | δ̃ split by the final action: REC, WITHDRAWN, FLAG, ABSTAIN, NO_FINDING | required |
| matched precision | expected correct kept RECOMMENDs / k_r per arm (tie-averaged) | descriptive |
| natural precision; frozen recommendation correctness | correct RECOMMENDs / R_A; CORRECT / determinate sites with RECOMMEND | descriptive |
| natural δ | the same without matching | secondary |

**Repositories.**
- **Estimable:** n_r ≥ 1.
- **Counts:** K = 7 always; K_e = #estimable.

## 6. Execution failures (V22)

**Partition.** For each repository and comparison:
- both ran (= C_r);
- F only;
- M only;
- neither.

Per-arm failure rates use |E_r|.

**Frozen rules unchanged:**
- EXECUTION_FAILURE is its own judgment;
- per-arm rates use n_exec;
- paired analyses use both-ran sites.

**Sensitivity analyses:**
- **S-F1:** δ_S-F1,r = [n_r·δ̃_r + Σ_{F only} X − Σ_{M only} Y] / |E_r|. Each failed (site, arm) is scored not correct. For concordant failures this is a pure rescaling. **S-F1 describes the sampled primary set E_r, not the commonly evaluable set; it is a sensitivity analysis and never replaces the primary estimate (Sec. 2).**
- **S-F2 (bounds):** [… − |F_F,r|] / |E_r| to [… + |F_M,r|] / |E_r|.

**Reporting (never omitted):** per repository and arm, the failure counts by reason (unreadable, parse error, time limit, recursion, other), by library and by scope; the failed-file list; and the label distribution of failed sites.

**Wording trigger.** If the pooled failure share is > 5%, or > 10% in any repository, the H2 or F-A sentence says "on sites in files the analyser could parse (x% failed)" and S-F1 appears in the main table.

## 7. Inference (V13, V20, V21, V10b; C3, C5)

### 7.1 Bootstrap

- **Resampling.** For b = 1..B (B = 10,000; numpy `default_rng(20261113)`, one fresh generator per comparison; chunks of 2,000), for each estimable repository in ascending name order:
  - draw n_r indices with replacement from C_r;
  - draw n_r uniform tie keys for F, then n_r for M.
- **In each resample:** recount, re-match (lowest tier first, ties by the uniform keys), re-score (withdrawn → the ABSTAIN judgment), and form δ*_b with the same pooling as the point estimate.
- **p-value:** p(d0) = (1 + #{δ*_b ≤ d0}) / (B + 1), with d0 = 0 for H2a, H2-3 and H2-4, and d0 = 0.10 for H2b.
- **The bootstrap of δ̃ itself (exact tie-averaging inside resamples) is not used.** It was shown to be liberal (R4-13).
- **Monte Carlo rule.** If |p − t| < 3·√(p(1 − p)/B) for the threshold t it is compared to, re-run with B = 100,000 and the same seed. That result is final.

### 7.2 Coverage-gap guard (V20; C3, C5)

- **Gap:** g = (1/K_e) Σ_{r ∈ estimable} (R_F,r − R_M,r)/n_r, held as an exact rational number.
- **Activation:** the guard is active iff **g < 1/10**. That covers negative gaps, zero and 0 < g < 0.10. At g = 1/10 exactly, or above, it is not active.
- **Effect:** when active, p* = min(1, 2p) for the direction tests (before Holm) **and** for the H2b margin criterion.
- **K_e = 0:** g is undefined.

### 7.3 Feasibility gate (V21), label-free

- **Feasible repository:** k_r ≥ 5. A repository with n_r = 0 has k_r = 0 and is not feasible.
- **Pooled matched coverage:** c_pool = Σ_r k_r / Σ_r n_r, an exact fraction over the estimable repositories. Also reported: c̄ = (1/K_e) Σ k_r / n_r.
- **The gate passes iff c_pool ≥ 1/5 AND #feasible ≥ 5.**

### 7.4 Assessability by K_e (C3; owner rules A and B)

| K_e | H2a, H2-3, H2-4 (confirmatory) | H2b | Estimable-repository average | Guard |
|---|---|---|---|---|
| 7 | assessable (subject to the gate) | assessable | is the primary estimate | g over the 7 repositories |
| 1–6 | **not assessable as pre-registered** | **not assessable for the original seven-repository estimand** | reported as **secondary only**: δ̃_e, with its own bootstrap p and bound over the K_e repositories, guard g_e | g_e over the estimable repositories |
| 0 | not assessable | not assessable | **does not exist** | undefined |

**Never:** zero imputation, carried-forward values, or silent removal. Every non-estimable repository is listed with its eligible count and failure reasons, and "K = 7; K_e = x (non-estimable: …)" is printed next to every pooled H2 figure.

### 7.5 Exact sequence (family F-B)

For each c in {H2-1, H2-3, H2-4}:
1. Build C_r, report failures, and assert concordance.
2. Compute the counts and k_r; hash the matching output.
3. Compute K_e, g_c and the gate G_c (label-free).
4. Join labels, score, and compute δ̃_c.
5. Bootstrap → p_c and the one-sided 97.5% lower bound L_c (a per-comparison bound, not adjusted for multiplicity; the Holm decision of step 8 is the confirmatory claim).
6. Apply the Monte Carlo rule.
7. Guard → p*_c.

Then:

8. **Holm** (m = 3) over the three p*_c at α = 0.025, with thresholds 0.025/3, 0.025/2 and 0.025 in ascending order of p*. Stop at the first non-rejection.
9. **Claim.** c is claimable iff K_e = 7, it is Holm-rejected, and G_c passes.
10. **H2b.** It is met iff K_e = 7 and p*_m ≤ 0.025, where p_m = p(0.10) for H2-1 and p*_m is guarded as in Sec. 7.2. Equivalently, the 97.5% lower bound exceeds 0.10 (the 98.75% bound when the guard is active). These bounds are per comparison and not multiplicity-adjusted.
11. **Secondary and exploratory analyses** (Sec. 10). None of them alters steps 8–10.

## 8. Outcome statements (C4) and templates

**For H2-1:**

| Condition | H2a statement | H2b statement |
|---|---|---|
| K_e < 7 | "not assessable as pre-registered" | "not assessable" |
| K_e = 7, gate fails | "not assessable at equal coverage (matched coverage too low)" | reported, labelled exploratory |
| gate passes, not Holm-rejected | "not supported" | met / not met (exploratory) |
| claimable | "supported" | met / not met (exploratory) |

**Statements for H2-3 and H2-4** are formed in the same way: "evidence beyond receiver typing / beyond the method name improves complete-policy correctness: supported / not supported / not assessable".

**Rules:**
- "H2 supported" is never used.
- The discussion sentence about the original 10-point H2 is allowed only when H2a is supported and H2b is met (protocol Sec. 1.1).

**Abstract template.** "In seven pre-registered test repositories, matching each method to the same number of migration recommendations per repository, the provenance-aware analysis made correct site-level decisions [more often than / not detectably more often than] method-and-argument analysis (difference x pp; per-comparison one-sided 97.5% bound y pp, not adjusted for multiplicity). [The 10-point improvement of the original hypothesis was / was not met in a pre-specified exploratory analysis.] Results describe these repositories only."

**Never in the abstract:**
- "recommendation accuracy" for the matched difference;
- any generalisation beyond the 7 repositories;
- "H2 supported" (never used anywhere).

**H2 results table (one row per comparison):**

| Field | Field |
|---|---|
| comparison, arms, thresholds | K, K_e |
| Σn_r | failures |
| c_pool | gate |
| g and guard | δ̃ (repository-balanced) |
| δ̃_site | one-sided 97.5% bound (per comparison, not multiplicity-adjusted) |
| raw p | guarded p |
| Holm-adjusted p | statement |
| matched precision F / M | natural δ |
| ranking-free δ̃ | 100-seed range |
| S-F1 | |

## 9. Experiment A (family F-A; C6 and owner rule D)

**Test.** For each baseline j that ran: a one-sided exact McNemar (proposed system better) on the pooled discordant pairs b_j and c_j over the sites where both ran, at natural coverage. Holm across j at α = 0.025.

**Assumptions** (must be printed with the results):
1. the 7 test repositories are fixed; inference concerns them only;
2. sites are stratified simple random samples with eligibility-only stopping (Sec. 2);
3. sites are drawn without replacement within strata, so the sampled pairs are not independent. Whether the pooled exact test keeps its level under this design is not asserted from theory: it was checked by the pre-F1 simulation of Sec. 11.6 (PASS; `docs/implementation/acceptance/fa_type1.md`), which covers the simulated configurations only;
4. the estimand of comparison j is the site-weighted difference over **its** both-ran sites.

In every simulated configuration (Sec. 11.6) the test was conservative: single-test rejection rates 0.0018–0.0089 and Holm family-wise errors 0.0004–0.0047 at nominal 0.025. This is evidence under the assumed configurations, not a proof, and the conservativeness costs power.

**Required for each j:**
- the both-ran denominator per repository and pooled;
- the site-weighted **and** repository-balanced differences (descriptive), with a within-repository bootstrap CI;
- S-F1 and S-F2;
- execution failures by reason;
- the limitation sentence: "7 purposively chosen repositories; no claim beyond them".

No guard is applied (there is no matching).

## 10. Secondary and exploratory analyses (pre-registered; none can create a confirmatory claim)

- **S1:** H2b (Sec. 7.5).
- **S2–S4:** matched precision, frozen recommendation correctness, natural precision.
- **S5:** natural-coverage comparison with exact McNemar.
- **S6:** the decomposition.
- **S7:** harmful, undecided and unjustified rates.
- **S8:** ranking-free matching.
- **S9:** the seeded table with site-level McNemar and Tango.
- **S10:** the 100-seed distribution.
- **S11:** fixed-target matching (target ⌊c_DV·n_r⌋). **c_DV (v1.0.1, F19)** is defined per comparison c as c_pool (Sec. 7.3: Σ_r k_r / Σ_r n_r, an exact fraction over the estimable repositories) computed on the Phase DV primary set (the 6 development and validation repositories) and recorded in the F1 evidence. Secondary only.
- **S12:** feasible repositories only.
- **S13:** failure sensitivities.
- **S14:** H2-S.
- **S15:** repository-level exploratory analyses: all δ̃_r, leave-one-out, one-sided t (df = K_e − 1), sign-flip, Wilcoxon.
- **S16:** the cluster bootstrap by repository, labelled "not a population CI".
- **S17:** strict scoring.
- **S18:** per-stratum results (Sec. 2).

**Per-repository report fields:**

| Field | Field |
|---|---|
| \|E_r\| | n_r |
| failures per arm and the partition | indeterminate counts |
| R_F, R_M | natural coverages |
| k_r and matched coverage | withdrawn per arm, boundary tier, withdrawn of tied |
| both / F only / M only recommended | correct and incorrect per arm (natural, matched) |
| δ̃_r | seeded δ_r |
| 100-seed minimum / median / maximum | ranking-free δ̃_r |
| natural δ_r | precisions |
| S-F1, S-F2 | feasibility flag |
| decomposition | stratum allocation |

## 11. Pre-F1 acceptance (C1; owner rule C)

Production code is accepted only if all of the following hold.

1. **Differential equality with the reference implementation.** On:
   - the worked examples;
   - the pilot tables;
   - 1,000 random property cases;

   the withdrawal sets, δ̃_r, g, the gate, guarded p, Holm and the K/K_e logic must be identical.
2. **Re-calibration on production code.** The 18 single-comparison scenarios, the 8 near-equal-coverage cells and the 8 family configurations must give:
   - every Type I cell ≤ nominal + 3 MC-SE;
   - every family-wise error ≤ 0.025 + 3 MC-SE.
3. **Two-stratum calibration (mandatory).** At least two configurations in which app and non-app sites differ in arm behaviour and in coverage:
   - allocation as the design produces (for example 20 app / 10 non-app per repository);
   - the null calibrated on the design-mixture functional Ψ(P^A);
   - ≥ 10,000 data sets per configuration, B = 1,000;
   - the unstratified bootstrap must satisfy criterion 2.
4. **Fallback.** If criterion 3 fails, the repository-by-stratum bootstrap (Sec. 2) is activated, and **all** of criteria 2–3 are re-run with it and must pass. If it also fails, work stops before F1. **F1 is not permitted after a failed calibration:** only a newly versioned procedure that passes every criterion of this section may proceed, and the owner decides which (v1.0.1, F20).
5. **Records.** The results, code version (commit SHA), seeds and the bootstrap variant in force are recorded in the F1 evidence.
6. **F-A Type I error simulation (v1.0.1; owner decision F05).** `scripts/fa_type1_simulation.py` simulates the unchanged F-A procedure (Sec. 9) under the design: 7 repositories; stratified sampling without replacement (20 app / 10 non-app per repository) from frames of very different sizes; heterogeneity between repositories and between strata; sparse discordance; random and stratum-dependent execution failures; 8 correlated baselines under Holm. Every configuration lies on the null boundary. Criterion: every single-test rejection rate ≤ 0.025 + 3 MC-SE and every Holm family-wise error ≤ 0.025 + 3 MC-SE, with MC-SE = √(0.025 · 0.975 / R), R = 20,000 (single) and 10,000 (family). **If any criterion fails, work stops and alternatives are presented to the owner; the method is never changed automatically.** Result on 18 Nov 2026: **PASS** (`docs/implementation/acceptance/fa_type1.{json,md}`). It says nothing about scanner accuracy.

## 12. Seeds

| Seed | Use |
|---|---|
| `20261113` | sampler order; bootstrap generator; the SHA-256 seed of the seeded per-site table |
| `20261113-S001` … `S100` | tie-break sensitivity only |
| `20261113:intra:<phase>`, `20261113:airepeat:<phase>`, `20261113:packet:<phase>` | reliability and packet-first samples |
| `20261113:withhold:001` … `20261113:withhold:100` (v1.0.1; frozen before F1) | H3 random withholding. Not fed to a random-number generator: the per-repository order is ascending SHA-256 (hexadecimal text) of UTF-8 `<seed>\|H3-withhold\|<repo>\|<site_id>`; the same order is used at 70%, 80% and 90% (nested subsets) |
| SHA-256 of `20261113\|H3-T2\|<repo>\|<site_id>` (v1.0.1) | H3: tie order within an evidence tier when the T2 policy is withdrawn to a fixed coverage |
| `20261113:fa-type1:<configuration>` (v1.0.1) | F-A Type I simulation: numpy default_rng(first 8 bytes, big-endian, of the SHA-256 of the string) |

**The primary point estimate has no tie seed. No seed is chosen for its result.**

## Changelog

- v1.0 (2026-11-16): adopted with protocol v1.0.4.
- v1.0.1 (2026-11-18, before any labelling and any test-split access; owner-approved pre-F1 decision register `docs/audit/owner_decision_register_v1.0.5.md`): estimand A's weight denominator corrected to m_r, and what the primary C_r estimate and S-F1 each describe when execution failures exist, with failures reported by stratum (F04); F-A assumption 3 restated and the F-A Type I error simulation added and passed (F05, Sec. 11.6); bounds labelled per comparison, not multiplicity-adjusted (F17); c_DV defined (F19); F1 never after a failed calibration (F20); H3 seeds (H-5). No estimator, test, threshold, family or calibration result changed.
