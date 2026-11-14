# Evaluation protocol (v1.0, pre-registered)

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

## 3. Annotation

Two annotators per site, at least one outside the build team; annotation guide `docs/benchmark/annotation_guide.md`; Cohen's κ reported for role, assessability and provenance (target ≥ 0.70); disagreements adjudicated by a third person; all labels and adjudication notes published. A 20% sample of synthetic cases is validated by an external annotator.

## 4. Experiments

- **A. Baseline recommendation correctness** — Simple algorithm-name mapping, method/argument-only mapping, pqcheck 0.1.0, pqc-audit 0.4.1, PostQuant 0.7.0, qsafe 1.1.0 (pqc-posture), Quantum-Safe Auditor regex stage, CBOMkit (if runnable), Mehl's scanner (results-only artefact; repository-level, reported separately), ours. Outcome classes per site; harmful/undecided/unjustified/missed rates; detection precision/recall.
- **B. Provenance ablation** — method-only → +arguments → +receiver → +provenance → +downstream usage. Same sites; McNemar; which evidence resolves which sites.
- **C. Abstention** — always-recommend; tier gate τ ∈ {T1, T2, T3}; random withholding at matched coverage (100 seeds). Risk–coverage, AURC.
- **D. Robustness** — Dataset A operators; invariance per operator per tool; failure taxonomy.
- **E. Generalisation** — test split only, run once after the Phase 3 freeze.

## 5. Statistics

Wilson intervals for proportions; cluster bootstrap (1,000 resamples) by repo or base_case for differences and AURC; McNemar exact test for paired binary outcomes on the same sites; Holm correction within each family of comparisons; Cohen's κ for agreement; effect sizes (risk differences) with CIs always reported; p-values secondary. When a comparison involves different site sets (e.g. a tool that crashed on some files), the paired test is not applied and the reason is stated.

## 6. Freeze procedure (Stage 3.1)

Before Experiment E: tag code version (hash of the tree, or git tag), freeze taxonomy v1.0, policy v1.0, τ, split manifest with commit hashes, baseline versions/commits, adjudicated labels; record hypotheses above. Any later change is logged and evaluated only on a new partition or labelled exploratory.

## 7. Threats to validity (to be revisited)

Construct: role labels are themselves a judgement; mitigated by the guide, κ and adjudication. Internal: leakage from development to test; mitigated by the frozen split and the no-fix rule. External: two libraries, Python only, crypto-dense repositories over-represented. Conclusion: small n for some roles (PK_ENCRYPT/PK_DECRYPT were 2 of 29 in the pilot); report per-role n and avoid claims for roles with n < 20.
