# Evaluation protocol (v1.0.4, pre-registered)

Project: Post-quantum crypto scanner for Python projects. Base paper: Lei Zhang 2026, ICSE-Companion '26, DOI 10.1145/3774748.3795653.

**History.**
- Written 12 Nov 2026, after the H1 pilot and before any benchmark construction or analyzer code.
- Version 1.0.4 was **adopted on 16 Nov 2026, before any test-split access**, by owner decision: R4-18 as amended by R4-21 Sec. 6, including corrections C1–C6. The decision record is `docs/specification/phase3_decisions.md`.
- The superseded v1.0.3 is kept unchanged in `docs/specification/evaluation_protocol_v1.0.3.md` and in git history.

**Normative companions (hashed in the adoption record and at F1):**
- `docs/specification/phase3_analysis_plan.md`: the exact H2 and F-A procedures, estimands, failure handling and reporting rules;
- `docs/benchmark/annotation_guide.md` v1.1;
- `docs/specification/scoring_policy.md` v1.0 and `data_dictionary.md` v1.0, both unchanged.

**What did not change in v1.0.4:**
- The wording of RQ1–RQ4 and H1–H4.
- The H1, H3 and H4 decision rules and thresholds.
- Every metric definition in `scoring_policy.md` and `data_dictionary.md`.
- τ = T2 for the proposed system.
- The repository and baseline manifests.

## 1. Research questions and pre-registered hypotheses

| RQ | Hypothesis | Pre-registered decision rule |
|---|---|---|
| RQ1 How accurately do existing Python scanners give role-appropriate PQC recommendations per call site? | H1a: ≥ 25% of eligible real sites require evidence beyond the method/algorithm name. H1b: every baseline has harmful + undecided + unjustified rate ≥ 10% on eligible real sites. | Report rates with Wilson 95% CIs per tool. If H1a or H1b fails on the full real set, the recommendation framing is weakened and the paper is re-centred on N3 (robustness); this was stated in advance. Pilot values: 51.7% (15/29) and 7–31% (see `docs/pilot/h1_pilot_summary.md`). The thresholds were set *before* the full-set labelling. |
| RQ2 Does bounded provenance-aware analysis improve correctness over simpler mappings? | H2: correct-per-eligible-site of the provenance-aware arm exceeds the method+argument arm by ≥ 10 percentage points at equal coverage. *(Frozen sentence, unchanged. Operationalised in v1.0.4 as H2a and H2b below.)* | **[v1.0.4]** Sec. 1.1 and `phase3_analysis_plan.md`. This replaces "Paired McNemar on per-site correctness (same sites), Holm-corrected across arms; report difference with bootstrap CI clustered by repo" (Sec. 5.5). |
| RQ3 Does evidence-based withholding reduce harmful recommendations at comparable coverage? | H3: at coverage ≥ 70%, the harmful rate of the τ = T2 policy is lower than "always recommend" and than random withholding at the same coverage. | Risk–coverage curves; AURC with bootstrap CI; comparison at fixed coverages 70/80/90%. |
| RQ4 Which transformations change classification or recommendation? | H4: at least one operator (predicted: `loaded-key`, `cross-function`) flips ≥ 30% of base cases for every baseline; the proposed analyzer is invariant under `alias-import` and `wrapper-function` for ≥ 90% of base cases. | Per-operator invariance rate with Wilson CI; pairs (base, variant) are the unit. |

A negative result on any hypothesis is reported as such.

### 1.1 Operationalisation of H2 (v1.0.4)

**Identifiers (V23):**
- Hypotheses and comparisons use H-numbers.
- The names B1-algorithm, B1-dual, B2-method-args, B3-full-noabst and B4-full-T2 refer **only** to the code baseline variants in `pqscan/baselines/simple.py`.

**Comparisons (V18).** Every arm is a Module C analysis arm with the role-to-target policy at the stated evidence threshold. UNKNOWN roles always abstain.

| ID | Provenance-aware arm | Comparator arm | Status |
|---|---|---|---|
| H2-1 | `full` at T0 (code: B3-full-noabst) | `method+args` at T0 (code: B2-method-args) | confirmatory (H2a) |
| H2-2 | the same pair | — | exploratory effect size (H2b) |
| H2-3 | `full` at T0 | `method+args+recv` at T0 | confirmatory (RQ2 ablation) |
| H2-4 | `full` at T0 | `method-only` at T0 | confirmatory (RQ2 ablation) |
| H2-S | `full` at T2, the proposed system (code: B4-full-T2) | `method+args` at T0 | secondary |

**Operational hypotheses (V10a as amended by R4-21 C4):**
- **H2a (confirmatory; comparison H2-1).** In the seven test repositories, at equal recommendation volume within each repository, the complete-policy correctness per eligible site of `full` (T0) is higher than that of `method+args` (T0): δ > 0.
- **H2b (pre-specified exploratory effect-size analysis; comparison H2-2).** The same difference is at least 10 percentage points: δ ≥ 0.10. It is outside the family-wise error control.

**Traceability.** The frozen H2 (v1.0.3) corresponds to H2a (direction, confirmatory) together with H2b (≥ 10 points, exploratory).

**Reporting statements (R4-21 C4).** Two statements are always reported separately, each with its status:
- "H2a (confirmatory): supported / not supported / not assessable [as pre-registered | at equal coverage]";
- "H2b (exploratory, pre-specified; not under family-wise error control): 10-point criterion met / not met / not assessable".

**Wording rules:**
- The unqualified phrase "H2 supported" is **never** used.
- A significant H2a never yields a 10-point statement.
- The sentence "The 10-point improvement stated in the original H2 was also met in the pre-specified exploratory analysis, which is not covered by the family-wise error control" is allowed only in the discussion, and only when H2a is supported **and** H2b is met.
- When only H2a is supported: "H2a supported; the 10-point improvement of the original H2 was not established."

**Estimand (V12, R4-21 C2).** For each comparison:
- δ = (1/7) Σ_r δ_r over the seven test repositories.
- δ_r is the difference in expected complete-policy correctness per common evaluable site, after within-repository matching to equal recommendation volume.
- The expectation is over the **design mixture** of the repository's primary-set eligible sites: within each stratum (S1-app, S1-nonapp), a simple random sample of eligible sites, with the strata combined in the sampler's realised allocation (at least two-thirds app, by the pre-registered cap; Sec. 2).
- **Equal volume ≠ same sites.** "Equal recommendation volume" means equal **counts** per repository, never identical recommended sites.
- **Precision is separate.** Recommendation precision is a separate, descriptive quantity.

**Inference.** Summarised in Sec. 5.3; normative text in the analysis plan.

## 2. Datasets

**Dataset A (synthetic).** ~60 base cases × up to 7 variants (`identity`, `alias-import`, `wrapper-function`, `class-method`, `loaded-key`, `cross-function`, `dict-dispatch`), ≈ 400 instances.
- **Coverage:** both libraries; all roles; generated and loaded keys; negatives (padding constants, unrelated `.sign(` methods, `pqcrypto`-like names, comments).
- **Seeding:** base cases are seeded from idioms observed in the pilot and the development repos.
- **Clustering:** variants are correlated with their base case, so all statistics cluster on `base_case`.
- **`loaded-key`** is an **evidence-condition change**, not a semantics-preserving transformation. It is analysed separately from the invariance operators.

**Dataset B (real). [v1.0.4]**
- **Repositories (V15):** 13 repositories (4 development, 2 validation, 7 test), as frozen in `benchmark/real/manifest.json`. This replaces the planning range "8–12".
- **Labelling (V1):** every site is labelled by the owner (the single investigator) blind to tool outputs, reviewed by a separately conducted, isolated, blind AI-assisted review, and adjudicated by the owner. This replaces "double-annotated" (Sec. 3).
- **Unchanged from v1.0.3:**
  - selection criteria: public GitHub, OSI licence, ≥ 100 stars or a security-relevant purpose, uses pyca and/or PyCryptodome for RSA/EC, ≥ 10 candidate sites by regex over-approximation;
  - stratification by library and domain;
  - the development / validation / **test (frozen, never inspected for tuning)** split;
  - the exclusion of repositories in any baseline's own tuning corpus from the test split;
  - the pilot repositories are development repositories.

**Candidate discovery** is the union of the regex over-approximation, every baseline's findings and pqscan Module A, followed by manual source reading. The scanner's own output is never the sole source.

**Quotas and targets (V2).**

| Split | Repositories | Eligible quota per repository | Primary-set eligible sites |
|---|---|---|---|
| test | 7 | 30 | 210 |
| development | 4 | 25 | 100 |
| validation | 2 | 25 | 50 |
| **total** | 13 | | **360** |

- **Minimums:** ≥ 300 primary-set eligible sites in Dataset B, and ≥ 150 in the test split.
- **Shortfalls** are reported. Quotas are never moved between repositories.
- **No pooling across splits.** Development and validation sites are never pooled with test sites in any reported metric. Experiment E uses only test-split sites.
- **Tested constant.** The sampler's quota constant is tested against this table.

**Analysis sets (V14):**
- **Primary set:** every adjudicated-eligible S1 site (app and non-app), including overshoot. It is the only set counted toward quotas and targets, and the only set in primary metrics.
- **S2 set** (B0, 10 per repository): reported separately; excluded from quotas, targets and primary metrics.
- **Annotator-added sites:** reported separately, as "missed by every candidate source".
- **Unresolved sites:** excluded, listed and bounded (Sec. 5.6).
- **Tool false-positive profile:** per tool, findings on adjudicated-ineligible candidates, by category.
- **Sensitivity "all eligible":** primary ∪ eligible S2 ∪ annotator-added.

Every report states: "Results are limited to RSA/EC/Ed/X public-key call sites in files importing pyca or PyCryptodome within the candidate frame of the 13 frozen repositories."

**Sampling rule (v1.0.4; V5, V6, V11; implemented in `pqscan/bench/candidates.py`).**

*Pool:* per repository, the union above, deduplicated by enclosing statement.

*Scope classes (V5):* the first class that matches, in this order, on the path relative to the repository root:
1. **vendored:** a directory `vendor`, `_vendor` or `third_party`;
2. **test:** a directory `test`, `tests` or `testing`, or a file `test_*.py`, `*_test.py`, `test.py`, `tests.py`, `tests_*.py`, `tests-*.py` or `conftest.py`;
3. **example:** a directory `example`, `examples`, `demo`, `demos` or `demo*`;
4. **app:** otherwise.

*Strata (V11), none of which depends on any tool:*
- S1-app: files importing pyca or PyCryptodome, of class app;
- S1-nonapp: the same, of class test, example or vendored;
- S2: all other candidates.

*Issuance:*
- **Order:** each stratum is put in a seeded random order (seed 20261113).
- **Opaque IDs:** candidates carry opaque IDs, `C-` plus 12 hex digits of SHA-256(seed | repository | file | line). They reveal no stratum, tool or rank.
- **B0:** the first 10 S2 candidates, issued once, before B1.
- **B1, B2, …:** 10 candidates each: 7 S1-app and min(3, cap − eligible S1-nonapp so far) S1-nonapp. Empty slots are filled from the other S1 list, but **non-app issuance never exceeds the remaining cap**.
- **Cap:** quota // 3 (10 of 30, 8 of 25).
- **Counted** = eligible S1-app + min(eligible S1-nonapp, cap). Unresolved eligibility counts as not eligible.
- **Stopping:** counted ≥ quota, or 4 × quota S1 candidates issued, or S1 exhausted. The last two are reported as shortfalls.

*Stopping depends only on adjudicated eligibility,* never on any tool's output or correctness.

*Integrity (V6):*
- Every annotated site is kept.
- The issuance ledger is append-only and hash-chained, holds hashes only, and is committed and pushed after every step.
- All label files pass strict validation.

*Annotator-added sites* are eligible RSA/EC sites noticed in the same function but absent from the candidate list. They are recorded as `annotator_added` and reported separately.

**Design-mixture statement (R4-21 C2).**
- Within each S1 stratum, the order is uniformly random and stopping depends only on eligibility. Each repository's primary set is therefore a **stratified simple random sample** of eligible sites, with an outcome-independent allocation that is at least two-thirds app by the cap.
- **Every primary-set metric** (H1, H2, H3, F-A) is a design-mixture quantity, not a frame-proportional one.
- **Reported per repository:** the stratum allocation (eligible S1-app and S1-nonapp counts, plus pool sizes).
- **Reported descriptively:** per-stratum results (`phase3_analysis_plan.md` Sec. 2).

**Frame audit (V7), descriptive.** On the 6 development and validation repositories, the owner reads crypto-importing files in a seeded round-robin order until ≥ 60 eligible sites have been audited and every repository has contributed ≥ 1 file. Pool membership is then checked at statement level.
- **It can estimate:** the share of eligible sites in such files that the pool misses, with a file-level cluster bootstrap interval.
- **It cannot estimate:** recall in files importing no supported library, recall in the test split, recall in Python projects generally, or errors shared by the owner and the pool.

**Reporting by scope.** Results are reported pooled (primary) and per scope class.

## 3. Annotation [v1.0.4: replaced; V1, V3, V8, V9, V16]

**Primary annotator.** The owner labels every issued candidate, following annotation guide v1.1:
- from the full repository at the pinned commit;
- with every tool output hidden;
- each label carrying role-specific evidence lines and a rationale.

`meta.context_used` (`packet_sufficient` or `extended`, with the extra file:line ranges) is recorded in the primary file **before** the AI review (V16).

**AI-assisted review (V8).** A separately conducted, isolated, blind review:
- **Session:** one fresh isolated ChatGPT Temporary Chat per batch, with custom instructions, memory and history reference, Projects, connectors, file library and browsing all off. Alternatively, the API with a pinned model identifier and the owner's own key. The existing project conversation is never used.
- **Inputs:** guide v1.1's decision procedure and field definitions, the fixed hashed prompt, and the packet only.
- **Records:** the interface and model as displayed (or the API model ID) and the date and time in UTC, recorded before the first review. The verbatim response and the conversation export are archived.

**The AI review is never ground truth and is never called an annotation.**

**Fields labelled, compared and adjudicated:** `eligible`, `gt_role`, `assessability`, `possible_roles`, `hybrid_component`, `obvious_from_name`, `evidence_needed`, `key_provenance`.

**Order:** primary → validate → hash → ledger push → AI review → compare → hash → ledger push → adjudicate → hash → ledger push.

**Adjudication (V1, V9).** For each disputed field the owner records:
- the final value and the reason;
- a category: `kept`, `adopted_ai`, `third_value` or `unresolved`;
- a `context_difference` tag.

Unresolved cases are recorded before F2.

**Record envelope:** `{"site": <frozen-schema record>, "meta": {...}}`, with JSON booleans required. The frozen benchmark schema is unchanged; a meta schema is added.

**Reliability (V3).** Three statistics, never called inter-annotator reliability:
- **owner intra-rater consistency** (re-label ≥ 14 days later);
- **owner–AI agreement;**
- **AI repeat-run consistency.**

How they are run:
- **Phases:** DV (development and validation together) and T (test).
- **Intra-rater sample:** n = max(50, ⌈0.10·N⌉) per phase, seed `20261113:intra:<phase>`, stratified by repository (≥ 3 each) and by eligibility.
- **AI repeat-run sample:** n = max(30, ⌈0.10·N_AI⌉), seed `20261113:airepeat:<phase>`.
- **Reported per field:** n, raw agreement, Cohen's κ with a within-repository bootstrap 95% CI (2,000 resamples), the confusion table, per-class specific agreement (classes with ≥ 5 items) and prevalence.
- **Rule:** if the κ(gt_role) point estimate is < 0.60 → Phase DV: revise the guide and re-label Phase DV before F1; Phase T: all test results are labelled exploratory.

**Packet-first subset (V16).** A seeded 10% per phase (≥ 50; seed `20261113:packet:<phase>`) is first labelled from the packet alone (P-label), then normally (F-label).

**Synthetic subset, pilot and specification review.** These follow the same loop. The specification review is "ChatGPT review with owner sign-off".

**Publication:** all primary labels, AI reviews, comparisons, adjudications and ledgers, after F2 for the test split.

**Reporting language:** "single-investigator labels with a separately conducted AI-assisted review and investigator adjudication". Never "double-annotated", "independent annotators", "inter-annotator agreement" or "independent human validation".

## 4. Experiments

- **A. Baseline recommendation correctness.** Simple algorithm-name mapping, method/argument-only mapping, pqcheck 0.1.0, pqc-audit 0.4.1, PostQuant 0.7.0, qsafe 1.1.0 (pqc-posture), the Quantum-Safe Auditor regex stage, pqblocks-scan 0.1.0, CBOMkit, Mehl's scanner, and ours.
  - **CBOMkit is not run** (owner decision D4 = A). It is an inventory tool without migration advice and is never scored on recommendations. It is reported as not run in every table.
  - **Mehl's scanner** is a results-only artefact, repository-level, reported separately.
  - **Outputs:** outcome classes per site; harmful, undecided, unjustified and missed rates; detection precision and recall.
  - **[v1.0.4] Confirmatory family F-A:** the proposed system (`full` at T2) against each baseline that ran (Sec. 5.4).
- **B. Provenance ablation.** method-only → +arguments → +receiver → +provenance → +downstream usage.
  - **Same sites; McNemar at natural coverage:** a secondary analysis. It reports which evidence resolves which sites.
  - **[v1.0.4]** The matched comparisons H2-3 and H2-4 are confirmatory in family F-B (Sec. 1.1).
- **C. Abstention.** Always-recommend; tier gate τ ∈ {T1, T2, T3}; random withholding at matched coverage (100 seeds). Risk–coverage, AURC.
- **D. Robustness.** Dataset A operators; invariance per operator per tool; failure taxonomy.
- **E. Generalisation.** Test split only, run once after the Phase 3 freeze.

## 5. Statistics

### 5.1 General

- Wilson intervals for proportions.
- Exact McNemar for paired binary outcomes on the same sites.
- Holm correction within each family of comparisons.
- Effect sizes (risk differences) always reported with CIs; p-values are secondary.
- When a comparison involves different site sets (for example a tool that crashed on some files), the paired test uses only the sites where both methods ran, and the reason is stated (scoring policy Sec. 5).
- **[v1.0.4] Significance level (V17).** One-sided family-wise α = 0.025 for the confirmatory families F-B and F-A. Per-test thresholds come from Holm.

### 5.2 Comparison families

| Family | Members | Procedure |
|---|---|---|
| **F-B** (confirmatory) | H2-1, H2-3, H2-4 | Holm (m = 3) over the **guarded** p-values at one-sided α = 0.025. A result can be claimed only if it is Holm-rejected **and** its feasibility gate passes. |
| — (exploratory) | H2-2 (H2b) | outside every family; guarded margin criterion (Sec. 5.3) |
| **F-A** (confirmatory) | the proposed system vs. each baseline that ran (≤ 8) | Holm at one-sided α = 0.025 (Sec. 5.4) |
| others | H1, H3, H4; Experiment B natural-coverage McNemar; H2-S | as in v1.0.3, or descriptive/secondary |

### 5.3 H2 inference (V12, V13, V20, V21, V22; R4-21 C1, C3, C5)

The normative text and the order of steps are in `phase3_analysis_plan.md` Sec. 3–7. In summary:

1. **Paired set:** the common evaluable set C_r of each repository: primary-set eligible sites where both arms ran.
2. **Matching:** label-free. k_r = min(R_F,r, R_M,r) RECOMMENDs per repository. The arm with more RECOMMENDs withdraws its lowest-evidence-tier recommendations first (SHA-256 order within a tier). A withdrawn RECOMMEND is scored as ABSTAIN by the frozen judge.
3. **Point estimate:** δ̃, the exact tie-average over all permitted tie orders, repository-balanced. The site-weighted value is also reported.
4. **Test:** a stratified re-matching percentile bootstrap. Sites are resampled within repositories, and **fresh random tie keys are drawn in every resample**. B = 10,000, seed 20261113. If p falls within 3 Monte Carlo SE of a threshold, the bootstrap is re-run with B = 100,000.
5. **Coverage-gap guard:**
   - g = (1/K_e) Σ_r (R_F,r − R_M,r)/n_r, an exact fraction;
   - if g < 1/10, p → min(1, 2p) before Holm;
   - the guard also applies to the H2b margin criterion (C5).
6. **Feasibility gate (label-free):**
   - a repository is feasible iff k_r ≥ 5;
   - the gate passes iff Σk_r / Σn_r ≥ 1/5 **and** ≥ 5 of the 7 repositories are feasible;
   - otherwise the comparison is "not assessable at equal coverage".
7. **Repositories without common evaluable sites (C3):**
   - K = 7 is always reported, together with K_e, the number of estimable repositories;
   - if K_e < 7, H2a, H2-3 and H2-4, **and H2b**, are "not assessable as pre-registered";
   - if 1 ≤ K_e ≤ 6, the estimable-repository average is reported as secondary only;
   - if K_e = 0, no average exists, the coverage gap is undefined, and every H2 result is "not assessable";
   - no difference is ever imputed and no repository is silently dropped.
8. **Calibration (C1):** under the planning model, before F1. A two-stratum scenario is a mandatory acceptance criterion. If the unstratified bootstrap fails it, the pre-specified repository-by-stratum bootstrap replaces it, before F1.

### 5.4 Experiment A family F-A (R4-21 C6)

**Test.** A pooled one-sided exact McNemar per baseline j, on the sites where both the proposed system and j ran, at natural coverage, with Holm across the baselines.

**Assumptions under which this is valid** (and conservative under heterogeneity):
1. the 7 repositories are fixed (inference concerns these repositories only);
2. sites are stratified random samples with eligibility-only stopping;
3. the sampled pairs are independent;
4. the estimand is restricted to the both-ran sites of each comparison.

**Required with every F-A result:**
- the per-baseline both-ran denominators;
- the site-weighted **and** repository-balanced differences (descriptive);
- the execution-failure sensitivities S-F1 and S-F2;
- a CI from the within-repository bootstrap.

**Stated limitation:** the 7 purposively chosen repositories support no claim beyond them.

### 5.5 Amendments of v1.0.3 Sec. 1 and 5 (V24)

- **H2's test.** The v1.0.3 H2 rule ("Paired McNemar … clustered by repo") is replaced by Sec. 5.3. Exact McNemar and Tango on the matched site pairs (primary-seed table) are kept as **secondary**.
  - *Consequence:* McNemar on matched pairs is valid but conservative under matching; McNemar at natural coverage tests a different estimand, not "at equal coverage".
- **Cluster bootstrap by repository** (1,000 resamples) is kept **only as an exploratory** interval, labelled "7 purposively chosen repositories; not a population CI".
  - *Consequence:* no population-level CI is claimed.
  - Differences for Dataset A keep the cluster bootstrap by `base_case`, unchanged.
- **Execution-failure handling:** `phase3_analysis_plan.md` Sec. 6. The frozen n_exec and paired-set rules are unchanged; the sensitivity analyses are added.

### 5.6 Secondary label analyses (V4) and unresolved bounding (V9)

- **Consensus subset:** sites where the owner's primary label equals the AI review on `eligible`, `gt_role`, `assessability` and `hybrid_component`.
- **AI-label sensitivity:** where the AI fields are definite.
- **Unresolved bounding:** H2 and H3 are recomputed with unresolved sites set to the owner's primary label, to the AI's label and to INDETERMINATE, and the range is reported. More than 5% unresolved among eligible test sites is flagged as a major limitation.

## 6. Freeze procedure: two stages (structure unchanged since v1.0.1)

**Stage F1: pre-test methodological and code freeze.** It must be complete before any test-split repository is fetched. The freeze record `docs/freeze/pretest_freeze.json` is committed and the commit is tagged `phase3-pretest-freeze`. It contains:
1. the git commit SHA and the source-tree fingerprint (`scripts/tree_hash.py`);
2. SHA-256 of the role taxonomy, the recommendation policy (YAML and text), the scoring policy, this protocol, `phase3_analysis_plan.md`, `phase3_decisions.md`, the data dictionary, annotation guide v1.1, the benchmark schema and the meta schema;
3. τ and every threshold and decision rule (Sections 1, 4 and 5; `scoring_policy.md`; the analysis plan);
4. the baseline manifest, with tool versions, commit SHAs and measured failure profiles;
5. the sampling frame: the test entries of `benchmark/real/manifest.json`, the candidate-pool procedure and the sampling rule with its seed and the quota table;
6. hashes of the frozen development and validation labels, the ledger heads and the synthetic dataset (Dataset A);
7. the hypotheses and planned comparisons with their families (Sections 1 and 5);
8. the experiment commands for Stages F1→F2 and E;
9. **[v1.0.4]:**
   - the AI interface and model identity, and the prompt-template and packet-rule hashes;
   - the Phase DV reliability results;
   - the frame-audit result;
   - the specification-review record;
   - the Phase DV feasibility check (c_DV, k_r per repository);
   - the production statistical code hashes with their test results;
   - the differential-test report;
   - **the calibration evidence, with code version and seeds:** the single-comparison, two-stratum (C1) and family-wise runs, and which bootstrap variant is in force.

After F1, no change to code, policy, scoring, τ, the baseline set or the analysis plan may influence Experiment E. Any later change is logged, and its effect is evaluated only on a new partition or reported as exploratory.

**Between F1 and F2: candidate extraction and annotation.**
- After F1, the test repositories are fetched at their frozen commits (`scripts/fetch_pinned.py repos --include-test`).
- The frozen batch runner executes every method once on them. Raw outputs and logs are written to a sealed directory. Before anyone reads them, `docs/freeze/test_run_seal.json` records for every run the SHA-256 of the raw report, of the log and of the parsed findings (`findings_sha256`).
- A mechanical step extracts only locations (file, line range, API call) and produces a candidate list with no tool attribution and no recommendation text.
- **[v1.0.4]** The owner labels from source with tool outputs hidden. The test loop of Sec. 3 runs, with the ledger (hashes only) pushed after each step. Test labels stay out of git until F2. The owner records an attestation that the sealed outputs were not opened.
- Nobody may change the system in this window. The frozen code cannot be tuned on test material, and any change voids F1 for the affected comparisons.

**Stage F2: test-label freeze.** It must be complete before any judgment or statistic is computed on the test split. The addendum `docs/freeze/label_freeze.json` is committed and the commit is tagged `phase3-label-freeze`. **[v1.0.4]** It records:
- the SHA-256 of the owner's primary files, the AI-review files and exports, the comparison tables, the adjudication log and the final label files;
- the ledger heads;
- the Phase T reliability results;
- the unresolved list;
- the attestation and the dates.

Label files are immutable after F2. A correction is a new, dated file with a reason, reported next to the original.

**Stage E: held-out evaluation.** Only once F1 and F2 are both valid:
- The sealed outputs are judged against the frozen labels with the frozen judge and statistics, in one pre-registered evaluation.
- A determinism check compares the parsed-findings hashes with the seal.
- The command, environment, outputs and every failure and exclusion are recorded.
- No threshold, policy, scoring or code change follows from test outcomes. **The statistical method is never changed after held-out results have been seen.**

## 7. Threats to validity

**v1.0.3 text, kept.**
- **Construct:** role labels are themselves a judgement; mitigated by the guide, reliability statistics and adjudication.
- **Internal:** leakage from development to test; mitigated by the frozen split and the no-fix rule.
- **External:** two libraries, Python only, crypto-dense repositories over-represented.
- **Conclusion:** small n for some roles; report per-role n and avoid claims for roles with n < 20.

**[v1.0.4] Added:**
- a single human annotator; builder–annotator overlap (Phase DV labels are less blind than Phase T);
- AI-review errors correlated with the owner's framing; context asymmetry between owner and AI;
- blinding to sealed outputs by self-discipline;
- **only 7 purposively chosen test repositories:** no generalisation claim, and repository-level analyses are exploratory;
- the design-mixture weighting (test, example and vendored code are capped at one third);
- the matched H2 difference measures complete-policy correctness, not recommendation accuracy;
- coverage matching depends on the tier ranking (ranking-free sensitivity reported);
- bootstrap calibration rests on an assumed generative model (an empirical calibration, not a proof);
- the 10-point margin is exploratory and has low power;
- tool execution failures restrict estimands to sites where the tools ran;
- no external human validation.

## Changelog

- v1.0.1 (2026-11-14, before any test-split access): Section 6 split into two freeze stages (F1 pre-test, F2 test-label) plus the sealed candidate-extraction run. No hypothesis, metric, threshold or statistic changed.
- v1.0.2 (2026-11-14, before any test-split access): the determinism check compares parsed-findings hashes rather than raw report hashes. No hypothesis, metric, threshold or statistic changed.
- v1.0.3 (2026-11-14, before any test-split access; owner decisions D2–D5): clarified the 300 / 150 targets; added the seeded, stratified, quota-based sampling rule with a one-third test-path cap; CBOMkit not run (D4 = A). No hypothesis, metric, threshold or statistic changed.
- **v1.0.4 (2026-11-16, before any test-split access; owner approval of R4-18 as amended by R4-21 Sec. 6, corrections C1–C6; record `phase3_decisions.md`):**
  - **Annotation:** single-investigator design with an isolated AI-assisted review (V1, V8, V9, V16); intra-rater, owner–AI and AI repeat-run reliability replace two-annotator κ (V3).
  - **Dataset B:** 13 repositories (V15); quotas as a tested constant (V2).
  - **Sampling:** scope classes and S1-nonapp strata; sampler and ledger integrity rules (V5, V6, V11); analysis sets (V14); the descriptive frame audit (V7); the design-mixture statement (C2).
  - **H2:** operationalised as H2a (confirmatory) and H2b (exploratory) with explicit reporting statements; the unqualified phrase "H2 supported" is withdrawn (V10a, C4).
  - **Families and level:** F-B Holm m = 3 over guarded p-values with a feasibility-gated claim (V10b); one-sided family α = 0.025 (V17).
  - **H2 procedure:** arms and thresholds (V18); matching and estimand (V12); re-matching bootstrap (V13); coverage-gap guard (V20), also on H2b (C5); feasibility gate (V21); execution-failure handling (V22); K / K_e rule (C3); two-stratum calibration (C1).
  - **F-A:** assumptions and required reporting (C6).
  - **Statistics amendments:** McNemar demoted to secondary for H2; the cluster bootstrap by repository is exploratory only (V24).
  - **Identifiers:** H-numbers (V23).
  - **Unchanged:** the H1–H4 sentences, the H1/H3/H4 decision rules, the metric definitions, τ = T2 and the manifests.
