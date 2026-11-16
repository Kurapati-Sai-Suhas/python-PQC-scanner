# Evaluation protocol (v1.0.4 — PROPOSED, revision 3; not adopted — v1.0.3 remains in force until owner approval)

Project: Post-quantum crypto scanner for Python projects. Originally written 12 Nov 2026 after the H1 pilot. Changes from v1.0.3 are marked **[v1.0.4]**; items awaiting an owner decision are marked **(V#)**. Chronology: revision 1, 2 and 3 were all prepared on 14 Nov 2026, in that order, before any annotation or test-split access. Supporting analyses: `R3_01`–`R3_06`. Change log: `R3_08`.

## 1. Research questions and pre-registered hypotheses

The wording of RQ1–RQ4 and H1–H4 is unchanged. The H1, H3 and H4 decision rules are unchanged.

| RQ | Hypothesis | Pre-registered decision rule |
|---|---|---|
| RQ1 | H1a / H1b as in v1.0.3 | unchanged; Wilson CIs annotated "sites clustered in 7 repositories" |
| RQ2 | H2: correct-per-eligible-site of the provenance-aware arm exceeds the method+argument arm by ≥ 10 percentage points at equal coverage. | **[v1.0.4]** **(V12)** "At equal coverage" is implemented by coverage matching (Sec. 5.2). **(V10a′, V13, V17)** Estimand δ (repository-weighted, which equals the site-weighted value under equal quotas). Fixed sequence at repository level, one-sided α = 0.025: step 1 H0: δ ≤ 0; step 2 H0: δ ≤ 0.10. Repository-level one-sample t test, df = 6. **(V10b′)** Holm over family F-B. **Supported:** step 2 rejected. **Partially supported:** step 1 rejected, step 2 not. **Not supported:** step 1 not rejected. Exact sign-flip test (robustness); site-level exact McNemar and Tango score test (secondary, assumes independence). |
| RQ3 | H3 | unchanged; bootstrap intervals labelled descriptive (K = 7) |
| RQ4 | H4 | unchanged (clusters are base cases) |

**[v1.0.4] Family F-B (V10b′):** Holm over 4 hypotheses:
- H2-pos (full vs. method+args, δ > 0);
- H2-margin (full vs. method+args, δ > 0.10);
- full vs. method+args+recv, δ > 0;
- full vs. method-only, δ > 0.

**[v1.0.4] Family F-A:** full vs. each baseline that produced results on the test split, δ > 0, repository-level test, Holm.

**[v1.0.4] Planning statement.** With 7 test repositories, step 1 is probably detectable for true effects of 15–20 pp with similar repositories. Step 2 (the literal 10 pp margin) is unlikely to be established unless the true effect is about 25 pp or more (`R3_01` Sec. 5). "Partially supported" is the most likely positive outcome under moderate effects.

**[v1.0.4] Wording rule.** Categories as above, on owner-final labels and the primary set. "Robust" requires the same category in the secondary label analyses (Sec. 5.3) and a bounding range (Sec. 5.4) that does not cross a category boundary.

## 2. Datasets

**Dataset A (synthetic):** unchanged.

**Dataset B (real).** **[v1.0.4] (V15)** 13 repositories (4 development, 2 validation, 7 test), as frozen in `benchmark/real/manifest.json`. This replaces "8–12 repositories", a planning range written before the split was finalised. Every site is **labelled by the owner (primary annotator) blind to tool outputs, reviewed by a separately conducted blind AI-assisted review, and adjudicated by the owner** (Sec. 3). Selection criteria, stratification, splits and the baseline-corpus exclusion are unchanged. Candidate discovery is unchanged.

**[v1.0.4] Quotas and targets (V2):**

| Split | Repositories | Eligible quota per repository | Primary-set eligible sites |
|---|---|---|---|
| test | 7 | 30 | 210 |
| development | 4 | 25 | 100 |
| validation | 2 | 25 | 50 |
| **total** | 13 | | **360** |

The minimum targets are ≥ 300 primary-set eligible sites in Dataset B and ≥ 150 in the test split. Shortfalls are reported as such. Quotas are never moved. The sampler's quota constant is tested against this table.

**[v1.0.4] Analysis sets (V14):**
- **Primary set:** every adjudicated-eligible S1 site (app and non-app), including overshoot. This is the only set counted toward quotas and targets, and the only set in primary metrics.
- **S2 set** (B0, 10 per repository): reported separately; excluded from quotas, targets and primary metrics.
- **Annotator-added set:** reported separately.
- **Unresolved:** excluded and listed, then bounded (Sec. 5.4).
- **Sensitivity:** all adjudicated-eligible sites (primary ∪ S2 ∪ annotator-added).

**Sampling rule.** Unchanged from v1.0.3 except:
- **[v1.0.4] Scope classes and precedence (V5, V11):** `R3_05` Sec. 1; vendored > test > example > app.
- **[v1.0.4] Strata (V11):**
  - S1-app: crypto-importing files of class app;
  - S1-nonapp: crypto-importing files of class test, example or vendored;
  - S2: all other candidates.
- **Order:** seeded random order per stratum (seed 20261113). **[v1.0.4]** Opaque candidate IDs (`C-` plus 12 hex digits of SHA-256 of seed, repository, file and line).
- **[v1.0.4] B0:** the first 10 S2 candidates, issued once, before B1.
- **B1, …:** 10 candidates each, 7 S1-app and min(3, cap − eligible non-app so far) S1-nonapp. Empty slots are filled from the other S1 list, but **non-app issuance never exceeds the remaining cap**.
- **Cap:** quota // 3 (10 of 30, 8 of 25).
- **Counted** = eligible S1-app + min(eligible S1-nonapp, cap). Unresolved eligibility counts as not eligible.
- **Stopping:** counted ≥ quota, or 4 × quota S1 candidates issued, or S1 exhausted. The last two are reported shortfalls.
- **[v1.0.4]** Every annotated site is kept.
- **[v1.0.4] Ledger (V6):** append-only and hash-chained, holding hashes only. It is committed and pushed after every step. Strict validation applies. The stopping rule depends only on adjudicated eligibility.
- **[v1.0.4] Frame audit (V7):** `R3_04`; descriptive; ≥ 60 eligible sites and ≥ 1 file in each of the 6 development/validation repositories; file-level cluster bootstrap.

## 3. Annotation **[v1.0.4: replaced]**

- **Primary annotator:** the owner, following guide v1.1, from the full repository at the pinned commit, with every tool output hidden. Each label carries role-specific evidence lines and a rationale. **(V16)** `meta.context_used` is recorded (`packet_sufficient` or `extended`, with the extra files and lines).
- **AI-assisted review (V8):** the procedure in `R3_03` Sec. 5:
  - a fresh isolated Temporary Chat per batch, or the API with a pinned model identifier;
  - the existing project conversation is never used;
  - inputs: guide v1.1, the fixed hashed prompt and the packet only;
  - the model and interface identified, verbatim responses exported.

  The AI review is never ground truth and is never called an annotation.
- **Fields labelled, compared and adjudicated:** `eligible`, `gt_role`, `assessability`, `possible_roles`, `hybrid_component`, `obvious_from_name`, `evidence_needed`, `key_provenance`.
- **Order:** primary → validate → hash → ledger push → AI review → compare → hash → ledger push → adjudicate → hash → ledger push.
- **Adjudication:** per disputed field, the final value, the reason and a category (`kept`, `adopted_ai`, `third_value`, `unresolved`), plus a `context_difference` tag.
- **Record envelope:** `{"site": <frozen-schema record>, "meta": {...}}`. Boolean fields must be JSON booleans. The frozen schema is unchanged; a `meta` schema is added.
- **Reliability (V3):** the three statistics in `R3_03` Sec. 1–4.
  - Phases: DV (development and validation combined) and T (test).
  - Intra-rater n = max(50, ⌈0.10·N⌉), stratified by repository and by eligibility, ≥ 14 days later, seed `20261113:intra:<phase>`.
  - κ is reported with raw agreement, the confusion matrix, per-class specific agreement (classes with ≥ 5 items) and a CI.
  - Rule: κ(gt_role) < 0.60 → Phase DV: revise and re-label; Phase T: results exploratory.
- **Synthetic subset, pilot and specification review:** the same loop. The specification review is "ChatGPT review with owner sign-off".
- **Publication:** all primary labels, AI reviews, comparisons, adjudications and ledgers.

## 4. Experiments

Unchanged from v1.0.3, including CBOMkit not run (D4 = A).

## 5. Statistics

### 5.1 General

The v1.0.3 methods are retained, with these changes:
- **[v1.0.4]** All H2 and F-A tests are one-sided at α = 0.025, equivalent to two-sided 95% intervals **(V17)**.
- The confirmatory unit is the repository **(V13)**.
- Cluster-bootstrap intervals are descriptive with K = 7.
- Effect sizes are reported with CIs; p-values are secondary.
- No paired test across different site sets.

### 5.2 Coverage matching (V12)

For each comparison:
1. Coverage = the share of primary-set eligible sites on which an arm decides (does not abstain).
2. The arm with higher coverage withdraws decisions, lowest evidence tier first (T0, T1, T2, T3), ties broken by a seeded order (20261113), until both arms decide on the same number of sites.
3. Withdrawn decisions are scored as abstentions under the frozen scoring.
4. H2 uses these matched outcomes.

Comparison at natural coverage is reported as secondary.

### 5.3 Secondary label analyses (V4)

1. **Consensus subset:** owner primary = AI review on `eligible`, `gt_role`, `assessability` and `hybrid_component`.
2. **AI-review labels:** where those fields are definite.

### 5.4 Unresolved bounding (V9)

H2 and H3 are recomputed with unresolved sites set to the owner's primary label, to the AI's label and to INDETERMINATE, and the range is reported. More than 5% unresolved among eligible test sites is flagged as a major limitation.

### 5.5 Reliability and frame audit

`R3_03`, `R3_04`.

## 6. Freeze procedure

The structure is unchanged. **[v1.0.4]**

**F1 record additions:**
- guide v1.1 and the meta schema;
- the prompt template and packet rule (hashes);
- the AI interface and model;
- Phase DV primary, AI-review and final label hashes, plus the ledger heads;
- Phase DV intra-rater, owner–AI and AI repeat-run results;
- the frame-audit result;
- the specification-review record;
- the quota table;
- the V10–V17 decisions;
- the coverage-matching procedure;
- the statistical scripts (hashes) with their test results.

**Between F1 and F2:** the test loop runs, with the ledger (hashes only) pushed after each step; test labels stay out of git until F2. The owner records an attestation that the sealed outputs were not opened.

**F2 record:** all test label-file hashes, the ledger heads, Phase T reliability results, the unresolved list, the attestation and dates.

## 7. Threats to validity

The v1.0.3 text is kept. **[v1.0.4] Added:**
- single human annotator;
- builder–annotator overlap (Phase DV labels are less blind than Phase T);
- AI errors correlated with the owner's or the project's framing;
- context asymmetry;
- blinding to sealed outputs by self-discipline;
- **only 7 test clusters**: limited inferential power, H2's margin is probably not establishable at moderate effects, and repository-level conclusions are not generalisable;
- no external human validation;
- test, example and vendored code under-sampled by design.

## Changelog

- v1.0.1–v1.0.3: as in v1.0.3.
- v1.0.4 (PROPOSED, revision 3, 2026-11-14): see `R3_08`. The wording of H1–H4, the H1/H3/H4 decision rules, the metric definitions in `scoring_policy.md` v1.0, τ = T2 and the frozen manifests are unchanged. The H2 decision rule is made explicit (V10a′, V10b′, V12, V13, V17).
