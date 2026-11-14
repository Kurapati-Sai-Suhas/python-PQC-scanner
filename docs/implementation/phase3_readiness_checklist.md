# Phase 3 readiness checklist

Project: Post-quantum crypto scanner for Python projects. Base paper DOI 10.1145/3774748.3795653.
Written 14 Nov 2026 at Phase 2 closure. Status vocabulary: READY / NOT READY / BLOCKED (needs a person or decision outside the build team).

Updated 14 Nov 2026 (branch `phase3-preparation`): two-stage freeze, per `evaluation_protocol.md` v1.0.1 Sec. 6.

**Rule:** the held-out test split (`benchmark/real/manifest.json` → `test`) is not fetched, opened, scanned or labelled until every item in Sections A–D needed before F1 is READY and the pre-test freeze record (E1) is committed and tagged. `scripts/fetch_pinned.py` withholds it unless `--include-test` is passed. Test labels are produced after F1 and frozen at F2 (E2). Only then may Experiment E run (E3).

Owner and lecturer action package (people, workload, decisions D1–D6, sequence, research-complete definition): `docs/review/owner_action_package.md`.

## A. People and human review

| # | Item | Status | Evidence / what is missing |
|---|---|---|---|
| A1 | External annotator (outside the build team) recruited and briefed on `docs/benchmark/annotation_guide.md` | BLOCKED | No person named yet. Needs a lecturer-approved volunteer with Python + basic crypto literacy. Budget about 2–4 min per site. |
| A2 | Adjudicator (third person) for disagreements | BLOCKED | Not named. The lecturer or a supervisor is suggested. |
| A3 | Human review of `role_taxonomy.md` v1.0.1 | BLOCKED | Only AI reviews so far (two independent contexts). Record reviewer, date and outcome in the taxonomy changelog. |
| A4 | Human review of `recommendation_policy.md` v1.1 and `scoring_policy.md` v1.0 | BLOCKED | Only AI reviews so far. Record in policy Section 7. |
| A5 | Human check of the 31 pilot labels (`docs/pilot/h1_pilot_sites.csv`) | BLOCKED | AI re-derivation agreed on 12/12 roles and 11/12 provenance values; a human check is still required. |

## B. Benchmark data

| # | Item | Status | Plan |
|---|---|---|---|
| B1 | ≥ 300 independently double-annotated real sites | NOT READY | Development (paramiko, python-jose, PyJWT, Authlib) and validation (jwcrypto, asyncssh) repositories labelled first. Test repositories (pyHanko, keylime, mitmproxy, scapy, salt, barbican) only after the freeze. Target ≥ 150 eligible test sites. Candidates = union of a regex over-approximation, every baseline's findings and pqscan's Module A, so the scanner's own output is never the sole source. κ reported per field (target ≥ 0.70); initial disagreements preserved; class distribution and uncertainty reported. |
| B2 | Second PyCryptodome-using test repository | READY | `hclivess/bismuth` @ `328a6b9d61` added 2026-11-14 by the pre-stated rule (most PyCryptodome public-key imports among accepted candidates); repository-level qualification only; `docs/benchmark/qualification_round3.md`, `candidate_verification_round3.{json,md}`; manifest amendment recorded. |
| B3 | Synthetic benchmark (Dataset A) | READY (generated and tested); external 20% validation pending (needs A1) | `pqscan/bench/synth.py`, `tests/test_synth.py` (13), `benchmark/synthetic/` (61 base cases, 388 instances, blind 78-instance validation subset), `docs/implementation/synthetic_benchmark.md`. The held-out half (`synthetic-holdout`) is not scanned before F1. |
| B4 | Split safeguards | READY | Split frozen 2026-11-13 before Module C existed; test split withheld by the fetch script; no test-split repository appears in tests or experiments; the pilot repositories are development repositories. |

## C. Comparators and pipeline

| # | Item | Status | Evidence |
|---|---|---|---|
| C1 | Comparator versions pinned | READY | `benchmark/baselines_manifest.json` (six tools, full commit SHAs); rebuilt from pins and reproduced stored outputs identically (pqcheck, qsafe). |
| C2 | Baseline execution-failure handling | READY | Measured failure profiles in the manifest; `judge_external` turns silence on known-dropped files and logged failures into EXECUTION_FAILURE; rates use n_exec; regression tests in `tests/test_bench.py`. |
| C3 | CBOMkit | BLOCKED (user decision) | Investigated 2026-11-14 (`docs/implementation/cbomkit_route.md`): cbomkit-action v2.3.0 covers pyca but not PyCryptodome. Docker Desktop is installed but stopped; OpenJDK 21 is present; Maven is absent. Three routes, each needing approval: start Docker and pull the pinned image (recommended), a local Maven build, or GitHub Actions (development and validation only). Proposed pre-registered in-scope sub-analysis to decide before F1. Otherwise it is reported as not run. |
| C4 | Mehl ESEM 2026 scanner | READY (limited) | Results-only artefact; repository-level comparison only, stated in every table. |
| C5 | Run logs captured for every tool run | READY | Real pinned tools on the 4 development repositories, two runs (2026-11-14): 40 of 40 runs with a report; 155 of 155 pilot judgments reproduced, plus pqblocks-scan 31 of 31; real-tool failure fixture: failures match the measured profiles and none is MISSED; 40 of 40 findings digests equal across runs (protocol v1.0.2). Evidence: `docs/implementation/runner_evidence/`, `baseline_runner.md`. |

## D. Frozen analysis rules

| # | Item | Status | Evidence |
|---|---|---|---|
| D1 | Primary scoring policy | READY | `docs/specification/scoring_policy.md` v1.0 Sec. 2 |
| D2 | Strict sensitivity scoring (UNSUPPORTED_DROP_IN) | READY | `scoring_policy.md` Sec. 3; `strict_judgment`; reported in every table |
| D3 | Harm definitions; indeterminate and unassessable handling | READY | `scoring_policy.md` Sec. 2 and 4 |
| D4 | Hypotheses and decision rules (H1a ≥ 25%, H1b ≥ 10%, H2 +10 pp, H3, H4) | READY | `evaluation_protocol.md` Sec. 1 |
| D5 | Statistical analysis plan | READY | `evaluation_protocol.md` Sec. 5. Wilson CIs; bootstrap clustered by repository or base case (1,000 resamples, seed 20261113); exact McNemar on sites where both methods ran; Holm within each comparison family; Cohen's κ plus raw disagreement tables; risk–coverage curves and AURC; effect sizes with CIs. Implemented and cross-checked against statsmodels in `pqscan/bench/stats.py`. |
| D6 | τ = T2 and evidence-tier definitions | READY | `recommendation_policy.md` Sec. 4; `data_dictionary.md` Sec. 3 |

## E. Two-stage freeze (protocol v1.0.1 Sec. 6)

| # | Item | Status | How |
|---|---|---|---|
| E0 | Version control for the freeze | READY | git initialised 2026-11-14; remote `Kurapati-Sai-Suhas/python-PQC-scanner`; Phase 2 snapshot tagged `phase2-complete` (`docs/implementation/github_release_record.md`). The freeze uses a git tag plus `scripts/tree_hash.py`. |
| E1 | Pre-test freeze (`docs/freeze/pretest_freeze.json`, tag `phase3-pretest-freeze`) | NOT READY | Needs A3–A4 (human review), B1 (development and validation labels, double-annotated), B2, B3, C5, and a decision on the per-repository site cap and sampling seed. Contents are listed in protocol Sec. 6. |
| E1a | Sealed candidate-extraction run on the test split | NOT READY (after E1 only) | The batch runner writes raw outputs and logs; their hashes go into `docs/freeze/test_run_seal.json` before anyone reads them. The location-only candidate list is given to annotators with no tool attribution. |
| E2 | Test-label freeze (`docs/freeze/label_freeze.json`, tag `phase3-label-freeze`) | NOT READY (after E1a only) | Both annotators' raw labels hashed on submission; disagreement table; adjudication log; adjudicated labels; κ per field; reviewer IDs and dates. `.gitignore` keeps `benchmark/labels/test/` out of git until this commit. |
| E3 | Held-out evaluation | NOT READY (after E2 only) | Judge the sealed outputs with the frozen judge and statistics; determinism re-run compared with the seal; record command, environment, failures and exclusions. |

## F. Reproducible experiment commands (to be run in this order after the freeze)

```bash
.venv/Scripts/python scripts/fetch_pinned.py baselines .cache/baselines
.venv/Scripts/python scripts/fetch_pinned.py repos .cache/repos
.venv/Scripts/python scripts/fetch_pinned.py repos .cache/repos --include-test
.venv/Scripts/python -m pqscan.bench.run --sites benchmark/labels/adjudicated_test.csv --tool-outputs .cache/outputs --repos .cache/repos/test --out results/test
```

Run the third command only after E1 is committed and tagged. Batch runner (C5): `.venv/Scripts/python -m pqscan.bench.batch --tools-dir .cache/baselines --repos-dir <split dir> --out runs/<split>`. Synthetic benchmark (B3): `.venv/Scripts/python -m pqscan.bench.synth --out benchmark/synthetic --seed 20261113`.

## Summary

Ready now: split safeguards, comparator pins, execution-failure handling, all frozen scoring and statistical rules, version control (E0). Blocked on people: external annotator, adjudicator, human review of taxonomy, policy, scoring and pilot labels. Engineering still to do: none blocking. CBOMkit depends on decision D4. External validation of the synthetic subset waits for the annotator (A1). Decision needed before F1: the per-repository site cap and sampling seed.
