# Phase 1 report — Research specification, pilot and data foundation

Project: **Post-quantum crypto scanner for Python projects**. Base paper: Lei Zhang, "Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography Migration", ICSE-Companion '26, pp. 402–403, DOI 10.1145/3774748.3795653. Date: 12 November 2026. Full phase documentation (14 sections, PDF): `docs/reports/Phase_1_Research_and_Feasibility_Report.md/.pdf`.

## 1. Stage reports (A–J per stage)

### Stage 1.1 — Inspect the existing environment

- A. Intended: inventory the project, environment, tools, prior documents.
- B. Implemented: inventory recorded; venv created; Semgrep 1.185.0 smoke-tested on Windows (1 rule, 1 result, 0 errors); five baseline scanners cloned at the audit's pinned commits and installed in isolated venvs (PostQuant built from TypeScript source); NIST FIPS 203/204, SP 800-227 and IR 8547 PDFs downloaded and text-extracted; Mehl ESEM 2026 Zenodo record downloaded.
- C. Files: `docs/pilot/pilot_manifest.json`, `.venv/` (not committed), `docs/specification/system_requirements.md` Sec. 6.
- D/E. Tests: `semgrep --config r.yaml t.py --json` → 1 result; `python -c "import cyclonedx, Crypto, reportlab"` → versions printed; `docker info` → daemon not running; `wsl -l -v` → Ubuntu available.
- F. Metrics: n/a.
- G. Limitations: no git repository existed; Docker daemon stopped (CBOMkit blocked); Mehl's artefact is results-only.
- H. Acceptance: PASS.
- I. Corrections: none required.
- J. Next stage authorised: yes.

### Stage 1.2 — Freeze the technical specification

- A. Intended: six specification documents.
- B. Implemented: `system_requirements.md` v1.0, `role_taxonomy.md` v1.0, `recommendation_policy.md` v1.1, `api_coverage.md` v1.0 (all rows NOT_STARTED), `evaluation_protocol.md` v1.0 (pre-registered hypotheses and decision rules), `data_dictionary.md` v1.0.
- C. Files: `docs/specification/*.md`.
- D/E. Tests: documents cross-checked for consistency by two independent AI reviews (annotation review: 6 taxonomy ambiguities found and fixed; policy review: 3 MAJOR + 8 MINOR findings, all fixed in v1.1).
- G. Limitations: human review outstanding; `api_coverage.md` claims no supported API yet.
- H. Acceptance: PASS (documents exist and are internally consistent after review).
- J. Next stage authorised: yes.

### Stage 1.3 — Roles and migration policy

- A. Intended: 8-role taxonomy, 8+ provenance kinds, role→target table verified against FIPS 203/204 and SP 800-227 with parameter-set and protocol qualifications; independent review before freezing.
- B. Implemented: taxonomy v1.0 (8 roles + `NONE` for ineligible negatives, 11 provenance kinds, 9 labelling rules, evidence scopes); policy v1.1 with a standards-basis table verified line-by-line from the NIST PDFs (categories, KEM/DEM, key derivation, key confirmation, hybrid combiners, deprecation/disallowance dates, ML-KEM-768 default, legacy-use definition), seven target classes, scoring rules and a drop-in-wording flag.
- D/E. Independent review: AI cryptography reviewer in a separate context with the NIST text: verdict "APPROVE WITH CHANGES"; every finding incorporated and every cited line re-checked by the author.
- G. Limitations: reviewers were AI; a human reviewer outside the team has not yet reviewed.
- H. Acceptance: CONDITIONAL PASS (condition: human review before the Phase 3 freeze).
- J. Next stage authorised: yes, under the condition.

### Stage 1.4 — 30-call-site feasibility pilot

- A. Intended: two real repositories, ~30 manually inspected RSA/EC sites, per-site fields, existing scanners' output and its appropriateness, independent review of a sample, test of the kill criterion.
- B. Implemented: paramiko 5.1.0 and python-jose 3.5.0 (commits pinned); 31 sites annotated (30 eligible + 1 negative) across 19 fields; five baselines run from source with raw outputs preserved; Mehl artefact inspected; judgments computed by script under policy v1.1; outcome figure generated from the joined data.
- C. Files: `docs/pilot/h1_pilot_sites.csv`, `h1_pilot_joined.csv`, `h1_pilot_summary.md`, `h1_pilot_analysis.md`, `figures/pilot_outcomes.png`, `raw_tool_outputs/` (34 files), `experiments/pilot/{join_tool_outputs.py, plot_pilot.py, qsa_regex_driver.py}`.
- D/E. Tests: join script re-run after every annotation change; totals reconcile (5 tools × 31 sites = 155 rows). Independent re-derivation of 12 sites: 12/12 role, 12/12 assessability, 11/12 provenance, 12/12 obvious-from-name.
- F. Metrics (n = 30 eligible): role not determinable from name alone 16/30 = 53% (Wilson 95% CI 36–70%); statically indeterminate 4/30 = 13%; harmful + undecided per tool: pqcheck 20%, pqc-audit 10%, PostQuant 20%, qsafe 7%, QSA regex 27%; missed per tool 50–87%.
- G. Limitations: n = 30, two repositories (both inside baseline tuning corpora), pyca only, AI annotator + AI reviewer, QSA without its LLM stage, CBOMkit and Mehl's scanner not executed.
- H. Acceptance: PASS on observability (kill criterion not triggered on either arm); CONDITIONAL on human review of annotations.
- I. Corrections before proceeding: none blocking; carry the limitations into the protocol (done, Sec. 7 of the protocol).
- J. Next stage authorised: yes.

### Stage 1.5 — Data foundation

- A. Intended: Dataset A design, Dataset B split and ground-truth process, schema, annotation instructions.
- B. Implemented: `benchmark_schema.json` (JSON Schema 2020-12 with conditional rules), `annotation_guide.md` (decision procedure, worked examples, QC), `repository_split.md` (exclusion lists verified from the baselines' own corpus files; proposed dev/val/test candidates; verification checklist; freeze procedure), Dataset A design in `evaluation_protocol.md` Sec. 2.
- G. Limitations: repository list is a proposal until `verify_candidates.py` runs and `benchmark/real/manifest.json` is written (first stage of Phase 2, before Module C).
- H. Acceptance: CONDITIONAL PASS.
- J. Next stage authorised: yes, with the manifest freeze as the first Phase 2 task.

## 2. Phase 1 validation gate

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Frozen research specification exists | PASS | `docs/specification/system_requirements.md`, `evaluation_protocol.md` |
| 2 | Supported API coverage documented | PASS (as a plan; zero rows implemented, stated explicitly) | `api_coverage.md` |
| 3 | Role and recommendation taxonomy defined | PASS | `role_taxonomy.md` v1.0, `data_dictionary.md` |
| 4 | NIST-based policy independently checked | CONDITIONAL PASS — AI review done and incorporated (v1.1); human review pending | `recommendation_policy.md` Sec. 7 |
| 5 | 30-site pilot completed and analysed | PASS (CONDITIONAL on human annotation review) | `docs/pilot/h1_pilot_analysis.md` |
| 6 | Benchmark schema and annotation instructions exist | PASS | `docs/benchmark/benchmark_schema.json`, `annotation_guide.md` |
| 7 | Repository split and ground-truth process documented | CONDITIONAL PASS — process frozen; repository list proposed, not yet verified/pinned | `docs/benchmark/repository_split.md` |
| 8 | Feasibility decision recorded | PASS — proceed with N1 + N2 (+ N3); kill criterion not triggered | `h1_pilot_analysis.md` Sec. 4 |

**Gate outcome: CONDITIONAL PASS.** Phase 2 may start. Conditions carried forward: (i) human review of taxonomy, policy and pilot annotations by someone outside the build team before the Phase 3 freeze; (ii) `benchmark/real/manifest.json` written and verified before Module C is implemented; (iii) Docker (or a JVM route) for CBOMkit, else CBOMkit is reported as not run.

## 3. Feasibility decision

The research problem is observable on real code: half of the eligible RSA/EC sites in two mature libraries need consumer or provenance evidence to fix their role, and existing scanners (including one tuned on these very repositories) issue ML-KEM for signing, ML-DSA for ECDH key generation, dual targets for RSA key generation, and "already using PQC" for RSA signing and key wrap. N2's two mechanisms (bounded consumer tracing and key provenance) target exactly the observed failure modes. Proceed.
