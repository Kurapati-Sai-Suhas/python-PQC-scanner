# Owner decision package: D1–D6, human review and F1 readiness

Project: Post-quantum crypto scanner for Python projects (base paper DOI 10.1145/3774748.3795653). Prepared 14 Nov 2026 at commit `09d3c83` (branch `phase3-preparation`).

**Owner decision, 14 Nov 2026 (recorded from the project owner's approval in the project chat):** D2 = O2, D3a = test-path sites count, capped at one third of each repository's quota, D3b = held-out population kept separate, D4 = A (CBOMkit not run, never scored on recommendations), D5 = not adopted. D1 (people) and D6 (licence) remain open: they need the lecturer or institution.

**Status before that approval:** proposals only. Nothing in the protocol, manifest, scoring policy or sampling plan has been changed. No reviewer, annotator or approval exists. The seven held-out test repositories have not been fetched, inspected or sampled.

Evidence used:
- **Measured on development repositories only:** `docs/review/dev_candidate_pool_profile.md`, from `experiments/dev/candidate_pool_profile.py`.
- **Recorded before this package:** repository-level qualification counts (Phase 1 and round 3; numbers of files and regex matches, no site content).
- **Assumptions:** marked as such wherever used.

## 1. Decision table

| # | Decision | Recommended choice | Alternatives | Changes a frozen document? |
|---|---|---|---|---|
| D1 | Who fills the human roles | Three different people: external annotator, adjudicator, specification and pilot-label reviewer (Sec. 2) | the reviewer may also adjudicate if there is no other choice (never for sites they annotated) | no (register entries only) |
| D2 | Annotation sample size and seed | **Option O2 "balanced"** (Sec. 3): seeded, stratified, quota-based sequential sampling; 30 eligible test sites per test repository (210), 25 per development or validation repository (150); seed 20261113 | O1 lower (154 test), O3 higher (315 test) | yes: sampling rule added to `repository_split.md` / protocol Sec. 2 before F1 |
| D3a | Do test-path files (`tests/`, `test_*.py`) count toward the targets? | **Yes, as a stratum capped at one third of each repository's quota**, with results reported per scope as well as pooled | count without cap (protocol as written; test code would dominate: 63% of development candidates are in test paths); exclude | yes: cap added to the sampling rule |
| D3b | Is the held-out test population kept separate from development and validation? | **Yes, for every analysis.** Keep the protocol meaning of the targets: ≥ 300 eligible sites across Dataset B including the test split, and ≥ 150 eligible test sites as a separate minimum. Development and validation sites are never pooled into held-out results | require ≥ 300 development/validation sites on their own (doubles workload; not required by the protocol) | no |
| D4 | Run CBOMkit? | **Option A: keep it out of the primary evaluation and report it as not run**, with the reason (Sec. 5) | Option B: pre-registered pyca-only inventory comparison | no for A; yes for B |
| D5 | CBOMkit pyca-only sub-analysis | not adopted (follows from D4 = A) | adopt with D4 = B | yes if adopted |
| D6 | Repository licence | **Ask the lecturer or institution first** (Sec. 6); afterwards add MIT or Apache-2.0 and make `pyproject.toml` consistent | keep no licence (all rights reserved) | no (repository metadata) |

## 2. D1: human roles

Different people are preferred for all three roles. Annotator and adjudicator must differ for any given site, and the external annotator must be outside the build team. The pilot-label reviewer and the specification reviewer may be the same person, because both review the frozen definitions.

| | External annotator | Independent adjudicator | Specification and pilot-label reviewer |
|---|---|---|---|
| Qualifications | Python (classes, imports, call chains in real libraries); basic public-key cryptography (sign/verify vs. key exchange vs. encryption); no prior exposure to pqscan or baseline outputs on the benchmark repositories | security or cryptography background (lecturer, supervisor, postgraduate researcher); able to read Python | applied cryptography or security engineering; familiarity with FIPS 203/204 at overview level; Python reading |
| Where to find | final-year or postgraduate student in security or systems, through the lecturer | the lecturer, a supervisor, or a faculty member in security | lecturer, faculty security group, or an external research contact |
| Responsibilities | label every sampled candidate blind (`docs/benchmark/annotation_guide.md`); label the 78-instance synthetic validation subset blind | decide each disputed field from both justifications and the source, never tool output; log the reason | review taxonomy v1.0.1, policy v1.1 and scoring v1.0 with the form; label the 31 pilot sites blind |
| Deliverables | raw label files (`annotation_template.jsonl`) per batch; synthetic-subset labels | `adjudication_log.csv` rows | completed `spec_review_form.md` with a verdict per document; completed `pilot_label_review_blind.csv` |
| Workload | O2: about 26–34 h (assumed; Sec. 3) plus about 3 h synthetic subset (78 × 2–3 min, assumed) | O2: about 14–22 h (assumed 20% of candidates disputed, 5 min each) | about 3–5 h review (assumed) plus about 2 h pilot labels (31 × 2–4 min, the guide's budget) |
| Independence | not a build-team member; no access to tool outputs before submission | not an annotator of the sites they adjudicate | not a build-team member |
| Required evidence | own row in `docs/review/review_register.md`; SHA-256 of each submitted file, recorded on submission | own register row; signed or dated log | own register row; dated, completed forms |

"Measured" in this package means counted from repository files. Every hour figure is an estimate from stated assumptions, because no annotation has happened yet.

## 3. D2: what the targets mean, and the sampling options

**What the documents say.**
- Protocol Sec. 2: "Target ≥ 300 eligible, double-annotated sites from 8–12 repositories" for Dataset B as a whole, all splits.
- `repository_split.md` Sec. 2: "test ≥ 150 eligible sites", a minimum for the held-out split.
- The readiness checklist (B1) paraphrases the first as "≥ 300 independently double-annotated real sites" and drops "eligible". The protocol wording governs; the checklist will be corrected after approval.
- Neither document defines a sampling rule, a cap or a seed. `repository_split.md` refers to `experiments/bench/regex_candidates.py`, which does not exist yet. The candidate-pool builder is still to be written after D2 is approved.

**Measured on the four development repositories** (`dev_candidate_pool_profile.md`):

| Quantity | Value |
|---|---|
| Candidate pool (union of regex, six baselines and pqscan, by file and line) | 2,802 |
| Found only by the tool-independent regex (missed by every evaluated tool) | 216 |
| In test paths | 1,753 (63%) |
| In files importing no supported crypto library | 1,132 (40%) |
| Biggest contributors | QSA-regex 1,337 and qsafe 1,041 lines (both flag hashing and symmetric crypto too) |
| Regex coverage of the 31 pilot sites | 30 of 31; the one miss, J14, is an ineligible padding object |

Consequences:
1. The pool does contain sites that every tool misses (216 regex-only candidates), so the benchmark is not built only from the evaluated tools' findings.
2. A uniform sample of the union would be mostly ineligible, low-value candidates, so the sample must be stratified.
3. No eligibility rate can be measured without labels. Yield is treated as an assumption (30% or 50% in the crypto-importing stratum).

The test pools themselves are unknown and will only be built after F1. Recorded qualification counts give 1,484 regex candidates across the seven test repositories; if the development ratio holds (an assumption), the test union could be about five times larger.

**Proposed sampling rule** (identical across options; only the quotas differ):
1. The pool per repository is the protocol union, deduplicated by (file, line).
2. Strata are tool-independent. S1 is candidates in files importing pyca or PyCryptodome; S2 is all other candidates. S1 is further split into app and test-path; test-path sites fill at most one third of the quota (D3a).
3. Each stratum is ordered by a seeded random permutation. The seed is 20261113, recorded in F1; candidates are sorted by (file, line) first, so the order is reproducible.
4. Candidates are annotated in that order, in batches of 10 per repository. Disagreements on `eligible` are adjudicated per batch. Annotation stops when the repository's eligible quota is reached, or at a cap of 4 × quota S1 candidates.
5. A fixed 10 S2 candidates per repository are always annotated, to measure what that stratum contains.
6. If a repository hits its cap first, the shortfall is reported. Quotas are not moved between repositories after test annotation starts.
7. Annotators may add eligible RSA/EC sites they notice in the same function that are not in the candidate list. These are flagged `annotator_added` and reported separately, as sites missed by every candidate source.

Stopping depends only on eligibility labels, never on any tool's correctness. Every sampled candidate is annotated; none is skipped. The order is fixed by the seed before anyone sees the pool. Together these prevent cherry-picking.

**Options.** Allocation is equal per repository; repositories are the statistical clusters.

| | O1 lower | **O2 balanced** | O3 higher |
|---|---|---|---|
| Eligible quota per test repository × 7 | 22 → 154 | 30 → 210 | 45 → 315 |
| Eligible quota per development or validation repository × 6 | 25 → 150 | 25 → 150 | 30 → 180 |
| Total eligible, double-annotated | 304 | 360 | 495 |
| Candidates per annotator (S1 at 50% / 30% yield, plus S2) | about 740 / 1,140 | about 850 / 1,330 | about 1,120 / 1,780 |
| Hours per annotator (assumed 3 min per eligible site, 1 min per ineligible one) | 22–29 | 26–34 | 35–46 |
| Adjudication (assumed 20% of candidates disputed, 5 min each) | 12–19 h | 14–22 h | 19–30 h |
| Wilson 95% half-width at p = 0.5, test split | ±7.8 pp | ±6.7 pp | ±5.5 pp |
| H2 (≥ 10 pp paired difference, McNemar, 80% power, assuming 20% discordant pairs) | n ≈ 155 at α = .05, ≈ 207 under the worst Holm step: borderline | adequate | comfortable |

By library: PyCryptodome appears in only two test repositories (salt, bismuth). Under any option the number of PyCryptodome test sites is at most two repository quotas, so library-wise claims for PyCryptodome stay descriptive.

By role: roles are unknown before labelling, so the sample cannot be stratified by role. Following protocol Sec. 7, role-wise results are reported only for roles with n ≥ 20. In the pilot, encryption roles were 2 of 29 sites, so no option is likely to support claims about PK_ENCRYPT or PK_DECRYPT.

What every option cannot support:
- generalisation beyond crypto-dense open-source Python repositories;
- tight cluster-bootstrap intervals, because there are only 7 test clusters;
- claims about rare roles;
- any statement about migration security.

**Recommendation: O2.** It meets both protocol targets with margin, gives H2 adequate power under the stated assumption, and keeps each annotator near 30 hours.

Limitations:
- The yield and time assumptions are unmeasured. The quota-based stopping rule absorbs yield uncertainty, but not time overruns.
- Small repositories (bismuth has 55 regex candidates) may not reach 30 eligible sites, and the shortfall would then be reported.

The rule is implemented only after you approve it, and before F1.

## 4. D3: targets and populations

- **Test-path files (D3a).** The protocol counts them: `scope` is recorded and never changes the role (taxonomy rule 6). With no cap, test code would dominate (63% of development candidates). The proposed cap keeps app code at least two thirds of each quota. Results are reported pooled and per scope, and pooled results are primary. Cost: slightly more S1 candidates are read to fill app quotas. Benefit: results reflect application code.
- **Held-out separation (D3b).** Your preference matches the protocol. Development and validation labels are produced first, by the same procedure, and used only for development and validation results. Test labels are produced after F1, kept out of git until F2, and are the only data for Experiment E. The "≥ 300" counts all splits, with the test split contributing ≥ 150. The two are never pooled in any reported metric.

## 5. D4 and D5: CBOMkit

- **What it produces.** CBOMkit (cbomkit-action v2.3.0, engine sonar-cryptography) produces a CycloneDX cryptographic inventory, with assets and locations. It does not infer call-site roles, and it gives no migration recommendation.
- **How it would be scored.** It may be scored only on detection: DETECTED_ONLY or MISSED for an eligible site, FALSE_POSITIVE_SITE for an ineligible one. It must never be scored on recommendation correctness or role inference.
- **Coverage.** It supports pyca/cryptography but not PyCryptodome, and it excludes test files by default.

**Option A (recommended).** Keep CBOMkit out of the primary evaluation. Record it in every table as "not run: inventory-only tool, Docker unavailable; would not be scored on recommendations".
- Pros: no extra pre-registration; no denominator complications; no downloads.
- Con: reviewers may ask why the best-known CBOM tool is missing. The answer is that it is not a recommendation baseline.

**Option B.** A separately titled, pre-registered supplementary inventory comparison: detection recall and precision on eligible pyca sites in non-test paths, its own denominator, every detection-capable tool on the same subset, and no pooling with the primary tables.
- Pros: scientifically defensible as a detection comparison.
- Cons: Docker Desktop plus a pinned image download; a new pre-registered analysis; extra tables. It does not inform the primary research question.

Recommended: A. B can be added only before F1 if the lecturer considers an inventory comparison necessary.

## 6. D6: licence

**Facts.**
- All 15 commits are under your GitHub identity. The work is a university course project, possibly team work.
- Bundled third-party files keep their own terms:
  - the CycloneDX 1.6 schema states Apache-2.0;
  - the OASIS SARIF 2.1.0 schema falls under OASIS terms;
  - pilot tool outputs quote short excerpts of paramiko (LGPL-2.1) and python-jose (MIT);
  - qualification records quote the first lines of third-party LICENSE files.
- **Inconsistency found:** `pyproject.toml` already declares `license = Apache-2.0`, while the README and the release record say no licence has been chosen. It is left unchanged pending your decision.

**Confirm with the lecturer or institution first:**
1. Who owns the IP in course-project work, and whether any assignment applies.
2. Whether every team member agrees.
3. Whether open-sourcing is allowed before assessment.

This is not legal advice.

**MIT vs. Apache-2.0.** Both are permissive and allow commercial reuse with attribution.
- MIT is shorter and has no explicit patent terms.
- Apache-2.0 adds an express patent licence from contributors, with termination if the licensee sues over patents. It requires retaining NOTICE files and stating changes, and it fits the Apache-2.0 schema already bundled.
- Either way, `pyproject.toml`, README and a LICENSE file must agree, and the third-party files keep their own notices.

## 7. Contact sequence

1. The lecturer: request the roles, confirm D2–D6, and ask about licence ownership. A message draft is in `docs/review/lecturer_request.md`.
2. Candidates suggested by the lecturer are briefed with `docs/review/README.md` and register themselves.
3. The specification review runs first, because it may change definitions. Then pilot review and synthetic validation, in parallel. Then development and validation annotation.

## 8. Key methodological risks

| Risk | Mitigation |
|---|---|
| Eligibility yield far below the assumption, which would inflate workload | quota stopping rule with a cap; shortfalls reported, not hidden |
| Annotators recognise tool output styles | location-only candidate lists; no tool attribution |
| The build-team annotator (A) has seen development code | allowed by the protocol; the external annotator (B) and κ provide the check |
| Too few clusters (7 test repositories) | cluster bootstrap reported with that caveat; no repository-level claims |
| Rare roles | n ≥ 20 rule; descriptive reporting only |
| Definitions change after the review | allowed only before F1; after F1, exploratory only |

## 9. Who does what

| Task | Owner (you, lecturer, reviewers) | Claude (after your approval) |
|---|---|---|
| Recruit people and fill the register | you and the lecturer | — |
| Decisions D1–D6 | you (with the lecturer) | — |
| Reviews, labels, adjudication | the reviewers | — |
| Write the D2/D3 sampling rule into the protocol and `repository_split.md` | approve | implement |
| Candidate-pool builder and seeded sampler, with tests | approve | implement |
| Batch generation of location-only candidate lists (development and validation) | approve | implement |
| κ, disagreement tables, adjudicated-label derivation scripts | — | implement |
| Licence files | decide | implement |
| F1 record and tag | approve | implement, after every prerequisite is met |

## 10. Exact F1 checklist (all must be true)

1. D1–D5 decided by the owner, and D2/D3 written into the protocol before any test access.
2. Specification review completed by a human, with a verdict per document in the register. Every accepted change is versioned.
3. Pilot-label review completed by a human; κ reported; disagreements adjudicated.
4. External validation of the 78-instance synthetic subset completed; confirmed generator errors fixed and Dataset A regenerated.
5. Development and validation candidate pools built and sampled by the approved rule; double-annotated; adjudicated; raw labels hashed.
6. Candidate-pool builder, sampler, κ and adjudication scripts implemented and tested.
7. The frozen code passes the full test suite at the F1 commit.
8. The freeze record contains:
   - the code fingerprint;
   - specification, protocol and scoring hashes;
   - τ;
   - the baseline manifest;
   - the sampling frame and rule (seed 20261113);
   - development and validation label hashes;
   - the Dataset A manifest hash;
   - the hypotheses and comparison families;
   - the E commands.

   It is committed and tagged `phase3-pretest-freeze`.
9. The CBOMkit status is recorded (D4).

Not required for F1: test-split labels (those belong to F2) and the licence (D6).
