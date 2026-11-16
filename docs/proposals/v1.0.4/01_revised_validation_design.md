# Revised validation design (PROPOSED, revision 2 — not adopted)

Status: proposal for owner approval. Revision 2 (14 Nov 2026) incorporates the methodology audit; the finding-by-finding mapping is in `08_audit_response.md`. Nothing in this folder replaces a frozen document until the owner approves it. Protocol v1.0.3, annotation guide v1.0 and every earlier record stay unchanged.

## 1. The owner's decision this responds to

The project has one human, the project owner. ChatGPT provides separately conducted AI-assisted reviews, and Claude implements, tests and documents. There is no lecturer, supervisor or external reviewer. No AI output may be presented as an independent human annotation, and no review may be described as independent human validation.

## 2. What changes

| Protocol v1.0.3 element | Replacement | What is lost | Mitigation |
|---|---|---|---|
| Two annotators per site, at least one outside the build team | **One primary human annotator (the owner)**, blind to tool outputs, followed by a **separate blind AI-assisted review** (ChatGPT, settings in Sec. 3) | an independent human check of every label | the AI review; intra-rater re-labelling (Sec. 5); sensitivity and bounding analyses (Sec. 6) |
| A third person adjudicates | **The owner decides** every owner–AI disagreement, in writing | adjudication independent of an annotator | disagreements logged and hash-anchored before adjudication; the owner's initial label and the AI's view published |
| Human–human κ, target ≥ 0.70 | **Owner–AI agreement** (diagnostic, no threshold) and **intra-rater κ** (Sec. 5) | the only true reliability statistic between people | intra-rater κ measures stability; owner–AI κ locates hard idioms |
| External review of taxonomy, policy and scoring | **ChatGPT methodology review** (same settings) plus **owner sign-off** | independent expert scrutiny | definitions cite FIPS 203/204 and SP 800-227; the limitation is stated |
| External validation of 20% of Dataset A | owner blind labels plus ChatGPT review of the 78-instance subset | external check of generated labels | disagreements trigger a generator review before F1 |
| Human review of the 31 AI-made pilot labels | owner blind re-labelling of all 31, then comparison | — | first human labelling of the pilot sites |
| — | **Optional later external re-annotation** of a random subset of test sites by any qualified person, if one becomes available. Reported as a post-hoc check, never used to change frozen results | — | allows the main weakness to be checked later |

**Fields cross-checked.** Both the owner and the AI review label every field the analyses use:
- `eligible`, `gt_role`, `assessability`, `possible_roles`, `hybrid_component` (these decide the expected class);
- `obvious_from_name` and `evidence_needed` (these decide H1a);
- `key_provenance` (provenance analyses).

All of these are compared and adjudicated.

## 3. AI-assisted review: settings and records

- **Session:** ChatGPT **Temporary Chat**, so no memory is used or created. Custom instructions, chat-history reference, Projects, connectors, file libraries and **web browsing/search** are all off. The pqscan repository is public, so browsing could reveal the system's design.
- **Alternative:** the OpenAI API with a pinned model identifier, run by the owner with the owner's own credentials. Claude never handles credentials.
- **Prompt:** a fixed, versioned template, hashed in the F1 record. It contains the annotation guide v1.1 decision procedure and field definitions, and the packet. It never contains the project's name, pqscan, any tool name, any hypothesis, any result, or the owner's label.
- **Packet:**
  - repository, commit, file, line;
  - the file's imports;
  - the enclosing top-level class or function, with line numbers;
  - for key sites, every function in the module that references the traced name;
  - the whole file if it is 400 lines or fewer.
- **Records per batch:** the interface model name, or the API model identifier; date and time; prompt-template hash; packet hash; the verbatim response; and the exported conversation file, with its timestamps.
- **Self-consistency:** a seeded 10% of AI-reviewed candidates per phase (at least 30) are reviewed a second time in a new session. AI–AI agreement is reported.
- **Context asymmetry:** the AI sees an excerpt and the owner sees the repository. Every disagreement is tagged `context_difference` when the AI's answer turns on code outside its packet. An AI answer of "insufficient context" is not a disagreement on role.
- **Correlation disclosure:** ChatGPT helped review this project's methodology. Its framing may match the owner's, so owner–AI agreement is not evidence of correctness.

## 4. Sample size, H2 decision rule and power (corrected in revision 2)

**Targets.**
- **≥ 150 eligible test sites** comes from an approximate power calculation for H2.
- **≥ 300 eligible sites** across Dataset B is a feasibility and publication-norm minimum, not a power figure.
- **Recommendation V2:** keep 30 per test repository (210) and 25 per development/validation repository (150).

**The H2 decision rule needs one pre-registered interpretation (V10).** H2 states the provenance-aware arm "exceeds the method+argument arm by ≥ 10 percentage points". The earlier power figures were for a significant difference greater than zero. If support also requires an observed difference of at least 10 points, a true effect of exactly 10 points is supported only about half the time, at any sample size. Exact conditional McNemar test, simulated, 6,000 repetitions, seed 20261113:

| Test sites | Discordant pairs (assumed) | True difference | P(significant), α = .05 / .05/3 | P(significant and observed ≥ 10 pp), α = .05 / .05/3 |
|---|---|---|---|---|
| 210 | 20% | 10 pp | 0.89 / 0.79 | 0.52 / 0.52 |
| 210 | 20% | 15 pp | 1.00 / 1.00 | 0.97 / 0.97 |
| 210 | 30% | 10 pp | 0.72 / 0.56 | 0.53 / 0.53 |
| 210 | 30% | 15 pp | 0.98 / 0.95 | 0.93 / 0.92 |
| 245 | 20% | 10 pp | 0.94 / 0.86 | 0.51 / 0.50 |
| 245 | 30% | 15 pp | 0.99 / 0.97 | 0.93 / 0.93 |

Recommended interpretation (V10a): three outcomes, pre-registered.
- **Supported:** Holm-adjusted exact McNemar p ≤ .05 in favour of the provenance-aware arm, *and* an observed paired difference ≥ 10 pp.
- **Partially supported:** significant, but the observed difference is below 10 pp. Reported as a smaller-than-hypothesised effect.
- **Not supported:** otherwise.

Planning statement: with 210 sites the study is designed to detect true effects of about 15 pp or more (P(supported) ≥ 0.92 under the assumptions above). A true effect of exactly 10 pp has about a 50% chance of full support.

**Holm family (V10b).** Experiment B family, m = 3: full vs. method+args (the H2 comparison), full vs. method+args+recv, and full vs. method-only. Experiment A comparisons (pqscan full vs. each baseline that ran) form a separate family.

**Effect of label noise (approximation, stated as such).**
- When reference-label errors are spread over many classes and unrelated to the arms, a simulated true 10-point difference shrinks to about 9.2 pp at 5% error and 8.8 pp at 10% error. That is close to a factor of (1 − e).
- The earlier (1 − 2e) factor holds for binary flips and is conservative here.
- Neither approximation covers systematic (builder-related) labelling bias, which more sites cannot fix.

**Other caveats.**
- **Discordance assumption.** Power falls sharply as discordance rises: exact McNemar, true 10 pp, 210 sites gives 0.89 at 20% discordance, 0.73 at 30% and 0.59 at 40% (α = .05).
- **Clustering.** The calculations treat sites as independent. With 7 test repositories, clustering lowers effective power, and the cluster bootstrap CI will be wider than these figures suggest.
- **Approximation error.** Earlier normal-approximation figures overstate exact power by about 0.02–0.04.

**Owner workload (assumed).**

| Activity | Hours |
|---|---|
| Primary labelling of about 850–1,330 candidates | 26–34 |
| AI-review handling (packets, sessions, saving responses; about 1–2 min per candidate in batches of 10) | 15–40 |
| Adjudication (15–25% of candidates at 3–5 min) | 8–20 |
| Intra-rater re-labelling (≥ 100 candidates) | about 5 |
| Pilot, synthetic subset and frame audit | about 8 |
| **Total** | **about 60–105** |

## 5. Reliability evidence (revised V3)

| Statistic | Definition | Rule and reporting |
|---|---|---|
| Owner–AI agreement | per field in Sec. 2: raw agreement and Cohen's κ | diagnostic; no threshold; per split |
| Intra-rater agreement | per phase (development/validation, then test), the owner blindly re-labels a **seeded random sample of at least 50 annotated candidates** (eligible and ineligible), drawn from all candidates annotated in that phase, **at least 14 days** after the first label, mixed with no other cue. 10% of candidates if that is larger | per field: raw agreement, κ with a bootstrap 95% CI, the confusion table, and n. **Rule:** if the point estimate of κ(gt_role) < 0.60, then on development/validation the guide is revised and that phase re-labelled before F1; on test, all test results are labelled exploratory. The CI is always shown. With n = 50 and a true κ of about 0.85, the simulated 95% range of the estimate is about 0.71–0.97 |
| AI self-consistency | Sec. 3 | raw agreement and κ |

## 6. Pre-registered secondary analyses (revised V4, V9)

The primary analysis uses owner-final labels.

1. **Consensus subset:** sites where the owner's primary label and the AI review agree on every field that decides the expected class (`eligible`, `gt_role`, `assessability`, `hybrid_component`).
2. **AI-review labels:** sites where the AI gave definite values for all of those fields.
3. **Unresolved-site bounding.** Unresolved sites are excluded from the primary analysis and listed. The H2 and H3 statistics are recomputed three times: with unresolved sites assigned the owner's primary label, the AI's label, and `assessability = INDETERMINATE`. The range is reported. If unresolved sites exceed 5% of eligible test sites, this is flagged as a major limitation.

All label sets (primary, AI, final) are frozen at F2 before any judging, so none of these analyses can feed back into labels.

**Wording rule.** "Supported", "partially supported" and "not supported" follow V10a on owner-final labels. "Robust" may be used only if the outcome category is the same in analyses 1 and 2, and the bounding range in analysis 3 does not cross a category boundary.

## 7. Publication-claim limitations

**Allowed:**
- "pre-registered benchmark of N eligible call sites, labelled by a single investigator blind to tool outputs, with a separately conducted AI-assisted review and investigator adjudication; all raw labels, AI reviews and disagreements are released";
- intra-rater and owner–AI agreement, with their meaning stated.

**Not allowed:**
- "independently annotated", "double-annotated", "inter-annotator agreement", "expert-validated" or "externally reviewed";
- AI reviews presented as annotators.

**Required in every report:**
- the threats: single annotator; builder–annotator overlap (development/validation labels less blind than test labels); correlated AI errors; no external validation; blinding to sealed outputs by self-discipline;
- the power statement of Sec. 4;
- an invitation for independent re-annotation.

## 8. Recommended sequence

1. Owner approves `06_open_decisions.md`. Claude commits protocol v1.0.4, guide v1.1 and the schema envelope in small commits.
2. Claude implements the sampler and ledger requirements (`05`), the packet builder, prompt template and comparison, κ, bounding and derivation scripts, with tests. Development/validation orders are regenerated.
3. ChatGPT specification review, then owner sign-off.
4. Owner re-labels the 31 pilot sites; ChatGPT review; comparison with the Phase 1 AI labels.
5. Synthetic subset: owner plus ChatGPT. Dataset A is regenerated if needed.
6. Frame audit (`05` R8).
7. Development/validation annotation loop to quota, with the ledger committed after each step. Intra-rater sample at least 14 days later.
8. Development/validation results reported as development results.
9. **F1**; tag `phase3-pretest-freeze`.
10. Test repositories fetched; sealed extraction run; test annotation loop (the ledger with hashes only is committed; labels stay out of git); intra-rater sample; owner attestation.
11. **F2**; tag `phase3-label-freeze`.
12. **E**, run once, with primary, secondary and bounding analyses, and the determinism check.
13. Novelty audit and final report.
