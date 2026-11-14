# Phase 3 readiness checklist

Project: Post-quantum crypto scanner for Python projects. Base paper DOI 10.1145/3774748.3795653.
Written 14 Nov 2026 at Phase 2 closure. Status vocabulary: READY / NOT READY / BLOCKED (needs a person or decision outside the build team).

**Rule:** the held-out test split (`benchmark/real/manifest.json` → `test`) is not fetched, opened, scanned or labelled until every item in Sections A–D is READY and the freeze record (Section E) is written. `scripts/fetch_pinned.py` withholds it unless `--include-test` is passed.

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
| B2 | Second PyCryptodome-using test repository | NOT READY | Manifest open condition 1: only `saltstack/salt` qualifies. Search, verify with `experiments/bench/verify_candidates.py`, and add it before the freeze, or report the shortfall. |
| B3 | Synthetic benchmark (Dataset A) | NOT READY | About 60 base cases × operators {identity, alias-import, wrapper-function, class-method, cross-function, dict-dispatch}, plus `loaded-key` as a separate evidence-condition change. Base cases seeded from development-repository idioms. A generator in `pqscan/bench/` emits code and site records validated against `benchmark_schema.json`. 20% of cases validated by the external annotator. Variants are clustered by base case in all statistics. |
| B4 | Split safeguards | READY | Split frozen 2026-11-13 before Module C existed; test split withheld by the fetch script; no test-split repository appears in tests or experiments; the pilot repositories are development repositories. |

## C. Comparators and pipeline

| # | Item | Status | Evidence |
|---|---|---|---|
| C1 | Comparator versions pinned | READY | `benchmark/baselines_manifest.json` (six tools, full commit SHAs); rebuilt from pins and reproduced stored outputs identically (pqcheck, qsafe). |
| C2 | Baseline execution-failure handling | READY | Measured failure profiles in the manifest; `judge_external` turns silence on known-dropped files and logged failures into EXECUTION_FAILURE; rates use n_exec; regression tests in `tests/test_bench.py`. |
| C3 | CBOMkit | BLOCKED | Needs Docker Desktop running (or a SonarQube/JVM route). Otherwise reported as not run. |
| C4 | Mehl ESEM 2026 scanner | READY (limited) | Results-only artefact; repository-level comparison only, stated in every table. |
| C5 | Run logs captured for every tool run | NOT READY | A batch runner must save `<prefix>_<repo>.log` next to each output so error logs can be parsed (required for pqblocks-scan). |

## D. Frozen analysis rules

| # | Item | Status | Evidence |
|---|---|---|---|
| D1 | Primary scoring policy | READY | `docs/specification/scoring_policy.md` v1.0 Sec. 2 |
| D2 | Strict sensitivity scoring (UNSUPPORTED_DROP_IN) | READY | `scoring_policy.md` Sec. 3; `strict_judgment`; reported in every table |
| D3 | Harm definitions; indeterminate and unassessable handling | READY | `scoring_policy.md` Sec. 2 and 4 |
| D4 | Hypotheses and decision rules (H1a ≥ 25%, H1b ≥ 10%, H2 +10 pp, H3, H4) | READY | `evaluation_protocol.md` Sec. 1 |
| D5 | Statistical analysis plan | READY | `evaluation_protocol.md` Sec. 5. Wilson CIs; bootstrap clustered by repository or base case (1,000 resamples, seed 20261113); exact McNemar on sites where both methods ran; Holm within each comparison family; Cohen's κ plus raw disagreement tables; risk–coverage curves and AURC; effect sizes with CIs. Implemented and cross-checked against statsmodels in `pqscan/bench/stats.py`. |
| D6 | τ = T2 and evidence-tier definitions | READY | `recommendation_policy.md` Sec. 4; `data_dictionary.md` Sec. 3 |

## E. Freeze record (to be written immediately before the first test-split action)

| # | Item | Status | How |
|---|---|---|---|
| E1 | Code version | NOT READY | No git repository exists. Either initialise git and tag `phase3-freeze` (decision for the user), or record `python scripts/tree_hash.py --manifest docs/implementation/freeze_manifest.json`. The Phase 2 closure fingerprint is recorded in the Phase 2 report; it is not the Phase 3 freeze. |
| E2 | Frozen labels (development, validation, test) | NOT READY | Adjudicated label files hashed into the freeze manifest. |
| E3 | Freeze statement | NOT READY | A dated entry listing taxonomy v1.0.1, policy v1.1, scoring v1.0, τ = T2, the repository manifest, baseline manifest and code fingerprint. Any later change is evaluated only on a new partition or labelled exploratory. |

## F. Reproducible experiment commands (to be run in this order after the freeze)

```bash
.venv/Scripts/python scripts/fetch_pinned.py baselines .cache/baselines
.venv/Scripts/python scripts/fetch_pinned.py repos .cache/repos
.venv/Scripts/python scripts/fetch_pinned.py repos .cache/repos --include-test
.venv/Scripts/python -m pqscan.bench.run --sites benchmark/labels/adjudicated_test.csv --tool-outputs .cache/outputs --repos .cache/repos/test --out results/test
```

Run the third command only after Section E is complete. The baseline batch runner that produces `.cache/outputs` with logs (item C5) and the synthetic generator (B3) are still to be written; their commands will be added here when they exist.

## Summary

Ready now: split safeguards, comparator pins, execution-failure handling, all frozen scoring and statistical rules. Blocked on people: external annotator, adjudicator, human review of taxonomy, policy and pilot labels. Blocked on a user decision: git versus tree hash. Engineering still to do: synthetic generator, baseline batch runner with logs, second PyCryptodome test repository.
