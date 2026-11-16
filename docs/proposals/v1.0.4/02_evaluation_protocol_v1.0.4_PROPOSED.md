# Evaluation protocol (v1.0.4 — PROPOSED, revision 2; not adopted — v1.0.3 remains in force until owner approval)

Project: Post-quantum crypto scanner for Python projects. Written 12 Nov 2026 after the H1 pilot and before any benchmark construction or analyzer code. Changes from v1.0.3 are marked **[v1.0.4]**. Items awaiting an owner decision are marked **(V#)**. Change log: `03_changelog_v1.0.4.md`. Audit mapping: `08_audit_response.md`.

## 1. Research questions and pre-registered hypotheses

The research questions, hypotheses H1–H4 and the decision rules for H1, H3 and H4 are unchanged from v1.0.3.

| RQ | Hypothesis | Pre-registered decision rule |
|---|---|---|
| RQ1 | H1a: ≥ 25% of eligible real sites require evidence beyond the method/algorithm name. H1b: every baseline has harmful + undecided + unjustified rate ≥ 10% on eligible real sites. | unchanged (Wilson 95% CIs per tool; re-centre on N3 if H1a or H1b fails) |
| RQ2 | H2: correct-per-eligible-site of the provenance-aware arm exceeds the method+argument arm by ≥ 10 percentage points at equal coverage. | **[v1.0.4] (V10a) interpretation, wording of the hypothesis unchanged.** Exact McNemar on per-site correctness (same sites), Holm-adjusted within family F-B. **Supported:** adjusted p ≤ .05 in favour of the provenance-aware arm *and* observed paired difference ≥ 10 pp. **Partially supported:** significant but observed difference < 10 pp. **Not supported:** otherwise. The difference is reported with a repository-clustered bootstrap CI. |
| RQ3 | H3 | unchanged |
| RQ4 | H4 | unchanged |

**[v1.0.4] Comparison families (V10b).**
- **F-B (Experiment B, H2):** full vs. method+args (the H2 comparison), full vs. method+args+recv, full vs. method-only; m = 3.
- **F-A (Experiment A):** pqscan full vs. each baseline that produced results on the test split; m = the number of such baselines, with not-run tools excluded and named.
- H1 and H3 use intervals, not multiplicity-corrected tests.

**[v1.0.4] Wording rule.** Outcome categories follow the decision rules on owner-final labels. "Robust" requires the same outcome category in the secondary analyses of Sec. 5 and a bounding range that does not cross a category boundary.

## 2. Datasets

**Dataset A (synthetic):** unchanged.

**Dataset B (real).** **[v1.0.4]** Target ≥ 300 eligible sites from 8–12 repositories, each **labelled by the owner (primary annotator) blind to tool outputs, reviewed by a separately conducted blind AI-assisted review, and adjudicated by the owner** (Sec. 3). The 300 is a feasibility and publication-norm minimum, not a power figure. Selection criteria, stratification, splits and the baseline-corpus exclusion are unchanged. Candidate discovery is unchanged.

**Targets.** ≥ 300 across Dataset B; ≥ 150 eligible test sites. Development/validation sites are never pooled with test sites; Experiment E uses test-split sites only.

**[v1.0.4] Quotas (V2).** Defined here and nowhere else:

| Split | Eligible quota per repository |
|---|---|
| test | 30 |
| development | 25 |
| validation | 25 |

The sampler holds a constant table that a test checks against this table. The repository's split is read from `benchmark/real/manifest.json`. An override requires a logged reason.

**Sampling rule.** Unchanged from v1.0.3 except as marked:
- **Pool:** unchanged.
- **[v1.0.4] Scope classes (V5, V11):**
  - *test*: a directory named `test`, `tests` or `testing`, or a file named `test_*.py`, `*_test.py`, `test.py`, `tests.py`, `tests_*.py`, `tests-*.py` or `conftest.py`;
  - *example*: under `examples/` or `demo*/`;
  - *vendored*: under `vendor/`, `_vendor/` or `third_party/`;
  - *app*: otherwise.

  One function implements this for the sampler and the label validator.
- **[v1.0.4] Strata (V11):**
  - S1-app: crypto-importing files of scope app;
  - S1-nonapp: crypto-importing files of scope test, example or vendored (replaces S1-test);
  - S2: all other candidates.
- **Order:** seeded random order per stratum (seed 20261113). **[v1.0.4]** Candidate identifiers are opaque: `C-` plus the first 12 hex digits of SHA-256 of seed, repository, file and line.
- **[v1.0.4] Batch B0:** the first 10 S2 candidates, issued once, before B1.
- **Batches B1, …:** 10 candidates each, 7 S1-app and up to 3 S1-nonapp. **[v1.0.4]** At most (cap − eligible non-app so far) non-app candidates per batch; empty slots are filled from the other S1 list.
- **Non-app cap:** one third of the quota (10 of 30, 8 of 25).
- **Stopping:** the quota is reached, 4 × quota S1 candidates have been issued, or S1 is exhausted. The last two are reported as shortfalls.
- **[v1.0.4]** Every annotated site is kept, including any beyond the quota or the cap.
- **[v1.0.4]** A site whose `eligible` value remains *unresolved* counts as not eligible for stopping, and is reported.
- **[v1.0.4] Ledger (V6):** append-only and hash-chained per repository. After every step (issue, primary submitted, AI review saved, adjudication saved), the ledger, which holds hashes only, is committed and pushed. That gives an external, time-stamped anchor and shows the owner's primary label existed before the AI review was requested. The next batch is issued only when every issued candidate has exactly one final label, and every label passes strict validation (Sec. 3).
- **Stopping rule:** depends only on adjudicated eligibility, never on a tool's output or correctness.
- **Annotator-added sites:** unchanged.
- **[v1.0.4] Frame audit (V7):** seeded crypto-importing development/validation files are added one at a time, each exhaustively labelled by the owner, until at least 60 eligible sites have been audited (at least 6 files). Report the share of audited eligible sites that are absent from the pool, with a Wilson CI and the per-file counts. Scope of the conclusion: frame recall within crypto-importing development/validation files only.
- **Reporting:** pooled (primary) and per scope.

## 3. Annotation **[v1.0.4: replaced]**

- **Primary annotator:** the owner, following annotation guide v1.1, from source at the pinned commit with every tool output hidden. Each label includes the role-specific evidence lines and a rationale.
- **AI-assisted review (V8):** ChatGPT Temporary Chat, or the API with a pinned model identifier. Memory, custom instructions, chat-history reference, Projects, connectors and web browsing/search are off. The prompt template is fixed and hashed. The packet holds only location and code context. The AI never sees the owner's label, any tool output or the project's name or results. Records: the model name or identifier, date and time, prompt and packet hashes, the verbatim response, and the exported conversation. Self-consistency check on a seeded 10% (at least 30) per phase. The AI review is never ground truth and is never called an annotation.
- **Fields labelled, compared and adjudicated:**
  - `eligible`, `gt_role`, `assessability`, `possible_roles`, `hybrid_component`;
  - `obvious_from_name`, `evidence_needed`;
  - `key_provenance`.
- **Order:** primary file → validation → hash → ledger commit → AI review → comparison table → hash → ledger commit → adjudication → hash → ledger commit.
- **Adjudication:** the owner records, per disputed field, the final value, the reason and a category: `kept`, `adopted_ai`, `third_value`, `unresolved`. A `context_difference` tag marks disagreements that come from the AI's limited excerpt.
- **Record format (V6):** an envelope `{"site": <record valid against the frozen schema>, "meta": {...}}`. `meta` holds `candidate_id`, `annotator`, timestamps, `evidence_lines`, `rationale`, `confidence`, `ambiguity`, `hard`, `time_seconds` and the AI metadata. `site.eligible` must be a JSON boolean. The frozen schema is not modified.
- **Reliability (V3):** owner–AI agreement per field (diagnostic). Intra-rater agreement per phase: a seeded sample of at least 50 candidates (or 10%, if larger), re-labelled blind at least 14 days later. Rule: κ(gt_role) point estimate < 0.60 → development/validation: revise the guide and re-label before F1; test: results exploratory. Reporting: raw agreement, κ with a bootstrap 95% CI, the confusion table, n.
- **Unresolved (V9):** every unresolved case is recorded before F2, excluded from primary metrics, listed by repository, role and scope, and bounded (Sec. 5).
- **Synthetic subset, pilot labels and specification review:** the same owner-plus-AI loop. The specification review is described as "ChatGPT review with owner sign-off".
- **Publication:** all primary labels, AI reviews, comparison tables, adjudication logs and ledgers.

## 4. Experiments

Unchanged from v1.0.3, including CBOMkit not run (D4 = A).

## 5. Statistics

The v1.0.3 methods are unchanged. **[v1.0.4]**
- **κ** means owner–AI agreement (diagnostic), intra-rater agreement or AI self-consistency. Never inter-annotator agreement.
- **Secondary analyses, pre-registered:**
  1. the consensus subset (owner primary = AI review on `eligible`, `gt_role`, `assessability`, `hybrid_component`);
  2. AI-review labels where those fields are definite;
  3. unresolved-site bounding: H2 and H3 recomputed with unresolved sites set to the owner's primary label, to the AI's label, and to INDETERMINATE; the range is reported. Unresolved sites above 5% of eligible test sites are flagged as a major limitation.
- **Power statement:** reported as in `01_revised_validation_design.md` Sec. 4, with exact McNemar figures, assumptions, the V10a rule and the clustering caveat.

## 6. Freeze procedure

The structure is unchanged (F1, the sealed extraction run, F2, E). **[v1.0.4]**

**F1 record additions:**
- guide v1.1 hash;
- the envelope definition;
- the prompt template and packet rule hashes;
- the AI model and settings;
- development/validation primary, AI-review and final label hashes, plus the ledger heads;
- development/validation intra-rater and AI self-consistency results;
- the frame-audit result;
- the specification-review record;
- the quotas table;
- the V10 decision.

"Annotators' identities" becomes "the owner (primary annotator and adjudicator) and the AI reviewer's model identity".

**Between F1 and F2:**
- The owner-plus-AI loop runs on test batches. The ledger, with hashes only, is committed after each step; test labels stay out of git until F2.
- The owner records an attestation that the sealed outputs were not opened.

**F2 record:**
- hashes of the primary, AI-review, comparison and adjudication files and the final labels;
- the ledger heads;
- owner–AI agreement and the test intra-rater result;
- the unresolved list;
- the attestation and dates.

## 7. Threats to validity

The v1.0.3 text is kept. **[v1.0.4] Added:**
- **Construct:**
  - single human annotator;
  - builder–annotator overlap; development/validation labels are less blind than test labels because the owner has seen development outputs;
  - AI reviewer errors correlated with the owner's or with the project's framing;
  - context asymmetry between the owner (whole repository) and the AI (an excerpt).
- **Internal:** blinding to sealed outputs between F1 and F2 rests on self-discipline, backed by hash anchoring and an attestation.
- **Conclusion:** power assumptions (discordance; clustering).
- **External:** no external human validation of the taxonomy, policy or scoring.

## Changelog

- v1.0.1–v1.0.3: as in v1.0.3.
- v1.0.4 (PROPOSED, revision 2, 2026-11-14, before any annotation or test-split access): single-investigator annotation with a blind AI-assisted review and owner adjudication; explicit H2 outcome categories and comparison families (V10); reliability, secondary and bounding analyses; sampler, ledger, scope and record-envelope corrections; frame audit. The hypotheses, the H1/H3/H4 decision rules, the metric definitions, τ and the statistical methods are unchanged. The H2 decision rule is interpreted, not changed in wording (V10a). See `03_changelog_v1.0.4.md`.
