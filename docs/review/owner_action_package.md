# Action package for the project owner and lecturer

Project: Post-quantum crypto scanner for Python projects (base paper DOI 10.1145/3774748.3795653). Prepared 14 Nov 2026 on branch `phase3-preparation`.

The project cannot reach its pre-test freeze (F1) without the people and decisions below. Nothing here has been done yet. No reviewer, annotator or approval exists, and none may be recorded by the build team on anyone's behalf.

## 1. People needed

| Role | How many | Independence | Minimum qualifications | Time (estimate) |
|---|---|---|---|---|
| Specification reviewer | 1 (2 preferred) | outside the build team | Python; security analysis; basic public-key cryptography (signatures vs. key establishment vs. encryption); overview of FIPS 203/204 | 3–5 h |
| Pilot-label reviewer (may be the same person) | 1 | outside the build team | as above, plus reading classes and call chains in real code | about 2 h (31 sites) |
| External annotator (annotator B) | 1 | outside the build team; has never seen pqscan or baseline output for the repositories | Python; basic cryptography | see Sec. 3 |
| Internal annotator (annotator A) | 1 | build-team member allowed; test split only after F1 | same | see Sec. 3 |
| Adjudicator | 1 | not an annotator of the sites adjudicated; ideally the lecturer or a supervisor | security or cryptography background | 1–3 h per 100 disagreements |
| Synthetic-subset validator (may be annotator B) | 1 | outside the build team | same | about 3 h (78 instances) |

## 2. What each person reviews or approves

| Activity | Files | Output and decision |
|---|---|---|
| Specification review | `docs/specification/role_taxonomy.md` v1.0.1, `recommendation_policy.md` v1.1 with `pqscan/policy/policy_v1_1.yaml`, `scoring_policy.md` v1.0 | `docs/review/forms/spec_review_form.md`, one verdict per document: APPROVED / APPROVED WITH CHANGES / CHANGES REQUIRED |
| Pilot-label review | `docs/review/forms/pilot_label_review_blind.csv` (locations only), source at the pinned commits | completed blind form; κ against the existing labels; disagreements adjudicated |
| Synthetic validation | `benchmark/synthetic/validation_subset.csv` (locations only) and the case files | blind labels for 78 instances; disagreements adjudicated; confirmed generator errors fixed before F1 |
| Real-site annotation | candidate lists per repository (generated after the decisions in Sec. 4) | `forms/annotation_template.jsonl` per annotator, kept unchanged and hashed on submission |
| Adjudication | both annotators' labels and justifications, plus source (no tool output) | `forms/adjudication_log.csv` |
| Register | `docs/review/review_register.md` | every person adds their own row: ID, role, background, independence, conflict of interest, date |

The procedure, independence rules and raw-label preservation are in `docs/review/README.md` Sec. 3–6.

## 3. Annotation workload (from the repository-level candidate counts)

Regex over-approximation candidates are an upper bound, and many are ineligible:

| Split | Repositories | Candidates | Of which in test paths |
|---|---|---|---|
| Development | paramiko, python-jose, PyJWT, Authlib | 643 | 371 |
| Validation | jwcrypto, asyncssh | 249 | 14 |
| Test (not opened) | pyHanko, keylime, mitmproxy, scapy, salt, barbican, bismuth | 1,484 | 469 |

The final candidate pool is the union of these regex candidates, every baseline's findings and pqscan Module A detections, so it is somewhat larger. At 2–4 minutes per site, double-annotating every test candidate would take each annotator roughly 50–100 hours. That is why the per-repository cap (Sec. 4, D2) must be decided before F1.

The targets are unchanged and are not weakened here: at least 300 eligible, independently double-annotated real sites, and at least 150 eligible test sites if achievable.

## 4. Decisions needed from the project owner

| # | Decision | Options | Needed before |
|---|---|---|---|
| D1 | Who fills each role in Sec. 1 | names or pseudonymous IDs held by the lecturer | anything else |
| D2 | Per-repository candidate cap and sampling seed for annotation | e.g. all candidates; or a cap of N per repository, sampled with a recorded seed and stratified by library and scope (app vs. test). With 7 test repositories, a cap of 60–80 gives 420–560 test candidates, from which at least 150 eligible sites is plausible but not guaranteed. | F1 |
| D3 | Whether test-path sites count toward the 300 / 150 targets or are reported separately | count with a `scope` stratum (protocol default), or exclude | F1 |
| D4 | CBOMkit | start Docker Desktop and pull the pinned image (recommended); local Maven build; GitHub Actions (development only); or report as not run | F1 |
| D5 | Whether to adopt the CBOMkit in-scope (pyca-only) sub-analysis | adopt / reject (`docs/implementation/cbomkit_route.md`) | F1 |
| D6 | Licence for the public repository | e.g. MIT or Apache-2.0, or none | any time (publication) |

## 5. Readiness (14 Nov 2026)

| Item | Status |
|---|---|
| Code, specifications, scoring and statistics frozen in documents | READY |
| Pinned baselines rebuilt and run on development repositories (two runs; pilot judgments reproduced 155 of 155; no failure scored as MISSED) | READY |
| Synthetic Dataset A (regenerates byte-identically; schema-valid; holdout unscanned) | READY |
| Second PyCryptodome test repository (bismuth pin verified on GitHub) | READY |
| Human specification review | BLOCKED (people) |
| Human pilot-label review | BLOCKED (people) |
| External synthetic validation | BLOCKED (people) |
| Development and validation double annotation | BLOCKED (people; D2, D3) |
| CBOMkit | BLOCKED (D4) |
| F1, F2, E | NOT READY (depend on the rows above) |

## 6. Sequence from here to the final evaluation

1. D1–D5 decided and the register filled by the people themselves.
2. Specification review. Any accepted change produces a new version, before F1.
3. Pilot-label review and synthetic-subset validation. Generator fixes, if any, produce a regenerated Dataset A, before F1.
4. Candidate pools built for the development and validation repositories, then double annotation, κ, adjudication and frozen development/validation labels.
5. Development-only checks: pqscan and baselines judged on development and validation labels. These are reported as development results.
6. **F1**: freeze record and tag `phase3-pretest-freeze`.
7. Test repositories fetched; sealed extraction run; location-only candidate lists; double annotation; adjudication.
8. **F2**: label-freeze addendum and tag `phase3-label-freeze`.
9. **E**: one evaluation, plus a determinism re-run, plus all reports.

## 7. When the project is research-complete

The project may be declared research-complete only when all of the following hold:
- F1 and F2 records exist, are tagged and their hashes verify;
- E has been run once from the frozen code, and its outputs match the sealed hashes;
- every metric and test in `evaluation_protocol.md` and `scoring_policy.md` has been reported, including negative results and execution failures;
- κ and the raw disagreements are published;
- the human reviews are recorded in the register by the reviewers;
- the novelty audit has been redone against the final evidence;
- the final report reconciles with the logs and the repository at a tagged commit.

Until then, pilot and development numbers are development checks and must not be presented as results.
