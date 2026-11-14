# Evaluation protocol (v1.0.3, pre-registered)

Project: Post-quantum crypto scanner for Python projects. Written 12 Nov 2026 after the H1 pilot and before any benchmark construction or analyzer code.

## 1. Research questions and pre-registered hypotheses

| RQ | Hypothesis | Pre-registered decision rule |
|---|---|---|
| RQ1 How accurately do existing Python scanners give role-appropriate PQC recommendations per call site? | H1a: ≥ 25% of eligible real sites require evidence beyond the method/algorithm name. H1b: every baseline has harmful + undecided + unjustified rate ≥ 10% on eligible real sites. | Report rates with Wilson 95% CIs per tool; if H1a or H1b fails on the full real set, the recommendation framing is weakened and the paper is re-centred on N3 (robustness) — stated in advance. Pilot values: 51.7% (15/29) and 7–31% (see `docs/pilot/h1_pilot_summary.md`); thresholds set *before* the full-set labelling. |
| RQ2 Does bounded provenance-aware analysis improve correctness over simpler mappings? | H2: correct-per-eligible-site of the provenance-aware arm exceeds the method+argument arm by ≥ 10 percentage points at equal coverage. | Paired McNemar on per-site correctness (same sites), Holm-corrected across arms; report difference with bootstrap CI clustered by repo. |
| RQ3 Does evidence-based withholding reduce harmful recommendations at comparable coverage? | H3: at coverage ≥ 70%, the harmful rate of the τ = T2 policy is lower than "always recommend" and than random withholding at the same coverage. | Risk–coverage curves; AURC with bootstrap CI; comparison at fixed coverages 70/80/90%. |
| RQ4 Which transformations change classification or recommendation? | H4: at least one operator (predicted: `loaded-key`, `cross-function`) flips ≥ 30% of base cases for every baseline; the proposed analyzer is invariant under `alias-import` and `wrapper-function` for ≥ 90% of base cases. | Per-operator invariance rate with Wilson CI; pairs (base, variant) are the unit. |

A negative result on any hypothesis is reported as such.

## 2. Datasets

**Dataset A (synthetic).** ~60 base cases × up to 7 variants (`identity`, `alias-import`, `wrapper-function`, `class-method`, `loaded-key`, `cross-function`, `dict-dispatch`) ≈ 400 instances; both libraries; all roles; generated and loaded keys; negatives (padding constants, unrelated `.sign(` methods, `pqcrypto`-like names, comments). Base cases are seeded from idioms observed in the pilot and development repos. Variants are correlated with their base case: all statistics cluster on `base_case`. `loaded-key` is an **evidence-condition change**, not a semantics-preserving transformation; it is analysed separately from the invariance operators.

**Dataset B (real).** Target ≥ 300 eligible, double-annotated sites from 8–12 repositories. Selection criteria: public GitHub, OSI licence, ≥ 100 stars or a security-relevant purpose, uses pyca and/or PyCryptodome for RSA/EC, ≥ 10 candidate sites by regex over-approximation. Stratify by library and domain (JOSE/JWT, SSH, PKI/TLS, cloud-auth, generic). Split: development (rules may be tuned), validation (threshold τ and operator choices), **test (frozen, never inspected for tuning)**. Repositories used in any baseline's own tuning corpus (pqcheck `tests/corpus`, Mehl's 19-repo ground truth, Quantum-Safe Auditor's 5-repo corpus) are excluded from the test split. The two pilot repositories are development repositories.

Candidate discovery for ground truth = union of (regex over-approximation, every baseline's findings, our Module A) followed by manual source reading. The scanner's own output is never the sole source.

**Targets (clarified in v1.0.3; unchanged in meaning).** "≥ 300 eligible, double-annotated sites" counts Dataset B across all splits. The test split must also contain ≥ 150 eligible sites (`docs/benchmark/repository_split.md` Sec. 2). Development and validation sites count toward the 300 but are never pooled with test sites in any reported metric. Experiment E uses only test-split sites.

**Sampling rule (v1.0.3; owner decisions D2 = O2 and D3, 14 Nov 2026; implemented in `pqscan/bench/candidates.py`).**
- **Pool.** Per repository, the union above, deduplicated by enclosing statement.
- **Strata.** These do not depend on any tool:
  - S1-app: files importing pyca or PyCryptodome, outside test paths;
  - S1-test: the same, in test paths;
  - S2: all other candidates.
- **Order.** Each stratum is put in a seeded random order (seed 20261113, recorded in F1).
- **Eligible quota.** 30 sites per test repository (7 × 30 = 210) and 25 per development or validation repository (6 × 25 = 150).
- **Batches.** Annotation proceeds in batches of 10: 7 S1-app and 3 S1-test, with empty slots filled from the other S1 list.
- **Test-path cap.** Test-path sites count toward a quota up to one third of it (10 of 30, 8 of 25). Once the cap is reached, no further test-path candidates are drawn.
- **S2.** The first 10 S2 candidates of each repository are annotated once.
- **Stopping.** Annotation stops when the counted eligible sites reach the quota, when 4 × quota S1 candidates have been issued, or when S1 is exhausted. The last two are reported as shortfalls; quotas are never moved between repositories.
- **Stopping depends only on adjudicated eligibility.** It never depends on any tool's output or correctness.
- **Annotator-added sites.** Eligible RSA/EC sites an annotator notices in the same function, but which are not in the candidate list, are recorded as `annotator_added` and reported separately.
- **Reporting.** Results are reported pooled (primary) and per scope (app vs. test path).

## 3. Annotation

Two annotators per site, at least one outside the build team; annotation guide `docs/benchmark/annotation_guide.md`; Cohen's κ reported for role, assessability and provenance (target ≥ 0.70); disagreements adjudicated by a third person; all labels and adjudication notes published. A 20% sample of synthetic cases is validated by an external annotator.

## 4. Experiments

- **A. Baseline recommendation correctness** — Simple algorithm-name mapping, method/argument-only mapping, pqcheck 0.1.0, pqc-audit 0.4.1, PostQuant 0.7.0, qsafe 1.1.0 (pqc-posture), Quantum-Safe Auditor regex stage, pqblocks-scan 0.1.0, CBOMkit (not run: owner decision D4 = A; it is an inventory tool without migration advice and is never scored on recommendations; reported as not run in every table), Mehl's scanner (results-only artefact; repository-level, reported separately), ours. Outcome classes per site; harmful/undecided/unjustified/missed rates; detection precision/recall.
- **B. Provenance ablation** — method-only → +arguments → +receiver → +provenance → +downstream usage. Same sites; McNemar; which evidence resolves which sites.
- **C. Abstention** — always-recommend; tier gate τ ∈ {T1, T2, T3}; random withholding at matched coverage (100 seeds). Risk–coverage, AURC.
- **D. Robustness** — Dataset A operators; invariance per operator per tool; failure taxonomy.
- **E. Generalisation** — test split only, run once after the Phase 3 freeze.

## 5. Statistics

Wilson intervals for proportions; cluster bootstrap (1,000 resamples) by repo or base_case for differences and AURC; McNemar exact test for paired binary outcomes on the same sites; Holm correction within each family of comparisons; Cohen's κ for agreement; effect sizes (risk differences) with CIs always reported; p-values secondary. When a comparison involves different site sets (e.g. a tool that crashed on some files), the paired test is not applied and the reason is stated.

## 6. Freeze procedure: two stages (revised in v1.0.1, before any test-split access)

Version 1.0 listed "adjudicated labels" inside the single freeze that also had to precede any contact with the test split. Test labels can only be produced after test access, so that order was impossible. Version 1.0.1 splits the freeze into two stages. The hypotheses, metrics, statistics, τ and decision rules in Sections 1–5 are unchanged.

**Stage F1: pre-test methodological and code freeze.** It must be complete before any test-split repository is fetched. The freeze record `docs/freeze/pretest_freeze.json` is committed and the commit is tagged `phase3-pretest-freeze`. It contains:
1. the git commit SHA and the source-tree fingerprint (`scripts/tree_hash.py`);
2. SHA-256 of role taxonomy, recommendation policy (YAML and text), scoring policy, this protocol, the data dictionary, the annotation guide and the benchmark schema;
3. τ and every threshold and decision rule (Sections 1, 4 and 5; `scoring_policy.md`);
4. the baseline manifest, with tool versions, commit SHAs and measured failure profiles;
5. the sampling frame: the test entries of `benchmark/real/manifest.json` (repositories and commits), the candidate-pool procedure (Stage F1→F2 below) and the per-repository site sampling rule (all candidates, or a stratified random sample with a recorded seed if a repository yields more than its cap);
6. hashes of the frozen development and validation labels and of the synthetic dataset (Dataset A);
7. the hypotheses and the planned comparisons with their correction families (Sections 1 and 5);
8. the experiment commands for Stages F1→F2 and E.

After F1, no change to code, policy, scoring, τ, the baseline set or the analysis plan may influence Experiment E. Any later change is logged, and its effect is evaluated only on a new partition or reported as exploratory.

**Between F1 and F2: candidate extraction and annotation.**
- After F1, the test repositories are fetched at their frozen commits (`scripts/fetch_pinned.py repos --include-test`).
- The frozen batch runner executes every method once on them. Raw outputs and logs are written to a sealed directory. Before anyone reads them, `docs/freeze/test_run_seal.json` records for every run the SHA-256 of the raw report, of the log and of the parsed findings (`findings_sha256`; v1.0.2).
- A mechanical step extracts only locations (file, line range, API call) from the union of the regex over-approximation, every baseline's findings and pqscan Module A detections. It produces a candidate list with no tool attribution and no recommendation text. Annotators label from source with tool outputs hidden (annotation guide Sec. 1 and 4).
- The two annotators label independently, and each one's raw file is hashed when they submit it.
- Nobody may change the system in this window. The frozen code cannot be tuned on test material, and any change voids F1 for the affected comparisons.

**Stage F2: test-label freeze.** It must be complete before any judgment or statistic is computed on the test split. The addendum `docs/freeze/label_freeze.json` is committed and the commit is tagged `phase3-label-freeze`. It records:
- the SHA-256 of both annotators' raw label files and of the initial disagreement table;
- the adjudication log and the adjudicated label file;
- κ and raw agreement per field;
- the annotators' and adjudicator's identities (or pseudonymous IDs held by the supervisor) and dates.

Label files are immutable after F2. A correction is a new, dated file with a reason, reported next to the original.

**Stage E: held-out evaluation.** Only once F1 and F2 are both valid:
- The sealed outputs are judged against the frozen labels with the frozen judge and statistics, in one pre-registered evaluation.
- A determinism check re-runs the frozen batch runner and compares the parsed-findings hashes with the seal (v1.0.2: three pinned tools embed timestamps, durations or random serial numbers, so raw report hashes are compared and reported but are not the criterion).
- The command, environment, outputs and every failure and exclusion are recorded.
- No threshold, policy, scoring or code change follows from test outcomes.

## 7. Threats to validity (to be revisited)

Construct: role labels are themselves a judgement; mitigated by the guide, κ and adjudication. Internal: leakage from development to test; mitigated by the frozen split and the no-fix rule. External: two libraries, Python only, crypto-dense repositories over-represented. Conclusion: small n for some roles (PK_ENCRYPT/PK_DECRYPT were 2 of 29 in the pilot); report per-role n and avoid claims for roles with n < 20.

## Changelog

- v1.0.1 (2026-11-14, before any test-split access): Section 6 split into two freeze stages (F1 pre-test, F2 test-label) plus the sealed candidate-extraction run. This resolves the contradiction in which adjudicated test labels were required to precede test access. No hypothesis, metric, threshold or statistic changed.
- v1.0.2 (2026-11-14, before any test-split access): the determinism check compares parsed-findings hashes rather than raw report hashes. Two identical development runs showed that PostQuant, pqc-audit and qsafe embed volatile fields (timestamps, scan durations, CBOM serial-number UUIDs) while their parsed findings were identical in 12 of 12 cases (`docs/implementation/runner_evidence/`). No hypothesis, metric, threshold or statistic changed.
- v1.0.3 (2026-11-14, before any test-split access; owner decisions D2–D5): clarified the meaning of the 300 / 150 targets; added the seeded, stratified, quota-based sampling rule with a one-third test-path cap; CBOMkit not run and never scored on recommendations (D4 = A). No hypothesis, metric, threshold or statistic changed.
