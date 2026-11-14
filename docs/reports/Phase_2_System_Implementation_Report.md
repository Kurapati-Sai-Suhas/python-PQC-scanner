# Phase 2 — System Implementation

**Project:** Post-quantum crypto scanner for Python projects (title fixed).
**Mandatory base paper:** Lei Zhang. "Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography Migration." ICSE-Companion '26, pp. 402–403. DOI 10.1145/3774748.3795653. arXiv:2602.05759. This phase implements part of Pillar P1 (PQC-aware detection with protocol roles and an enriched inventory). AQuA P2 and P3 are not implemented.
**Dates:** 13–14 November 2026. **Phase outcome: PASS — Phase 2 gate complete (Section 12)**, with Phase 1 conditions carried into Phase 3.

Everything below was executed in this phase. Results on the two pilot repositories and the two other development repositories are **development checks**, used to find and fix analysis gaps. They are not experimental results and must never be reported as evidence that the approach works; that is Phase 3's job on the frozen test split.

## 1. Objectives and scope

Build the research system defined in `docs/specification/system_requirements.md`: Module A (Semgrep candidates, lecturer requirement L2), Module B (bounded Python semantic layer), Module C (role inference with evidence tiers T0–T3), Module D (policy v1.1 with abstention, L4), Module E (CycloneDX 1.6 CBOM, L3; SARIF; JSON), Module F (benchmark judging and statistics), Module G (baselines and adapters), and a CLI that never executes scanned code (L1 end to end). Test each module independently, integrate, and pass the Phase 2 gate.

Out of scope here: benchmark construction, human annotation, final experiments (Phase 3).

## 2. Work performed, in execution order

1. **Handoff audit** (model change from Claude Fable 5.1 to Claude Opus 5.5 in the same session). Every Phase 1 claim was re-checked against files and command output. Written to `docs/implementation/opus_handoff_audit.md` with a per-module code audit (`phase2_code_audit.md`) and a rebuilt tracker. The audit found 5 failing Module B tests, a new market tool not covered by earlier audits (pqblocks-scan), and six contradictions between prompts and documents; all are recorded there.
2. **pqblocks-scan source inspection** (PQBlocks/cbom-scanner, commit 3d1eccfdfc). Its AST matching keys on literal receiver names; every `ec.generate_private_key` becomes ECDSA with "replace with ML-DSA-65"; RSA receives "ML-KEM-768 / ML-DSA-65"; no operations, no loaders, no roles, no abstention.
3. **Module B defects fixed** (five root causes): constructor call-site typing for attributes; parameter markers kept in type unions; conditional reassignment of parameters; class-attribute curve arguments; static/class methods no longer treated as having `self`. One test expectation that required path-sensitive reasoning was corrected to the documented flow-insensitive design.
4. **Module B checked on real code** (development repositories). Running it on the 31 pilot sites exposed six further gaps that synthetic snippets had missed: a merge that dropped origins (hid JWK construction), key pairs passed as tuples and unpacked into attributes (paramiko `vals=`), `self.__class__(...)` constructors (python-jose), public keys passed as the peer of `exchange`, keys returned to in-module callers, and two-step Numbers construction. Each fix received its own test. Intra-class hops were made exempt from the call-depth budget, because attribute tracing is already class-wide; they are protected by a visited set.
5. **Module C** implemented: a deterministic decision table with four ablation arms (method-only, method+args, method+args+recv, full). A tier inconsistency between arms (method-only forced T1 where method+args gave T0) was corrected to follow the frozen tier definitions.
6. **Module D** implemented: policy v1.1 as versioned YAML with a validating engine. Safety invariants are checked at load time: signatures must map to the SIG family; key establishment and encryption must map to the KEM family; UNKNOWN must abstain.
7. **Module E** implemented after checking the bundled CycloneDX 1.6 schema against the official 1.6.1 schema. Their `cryptoProperties` definitions are identical. The schema has no key-agreement `cryptoFunctions` value and no PSS padding; both are handled explicitly.
8. **Pipeline and CLI**: safe walk (no symlink or junction following, root confinement, size limit, per-file timeout), parse failures recorded as execution failures, Semgrep run alongside and joined by location.
9. **End-to-end development scans** of paramiko, python-jose, PyJWT and Authlib. This exposed two more structural gaps: classes defined inside a module-level `if has_crypto:` block (PyJWT) were invisible, and methods inherited from a base class were unresolved. Ed25519-or-Ed448 receivers were also wrongly reported as conflicting. All three were fixed and tested.
10. **Modules F and G** packaged from the pilot scripts. The packaged adapters reproduce the published pilot judgments exactly (regression test). Two simple baselines and three pqscan arms were added, and pqblocks-scan was run on both pilot repositories.
11. **Reproducibility**: `scripts/fetch_pinned.py` rebuilt every development and validation repository and all six baselines at their pinned commits into a fresh directory. The rebuilt pqcheck and qsafe produced outputs identical to the stored pilot outputs. Test-split repositories were not fetched.
12. Coverage measurement, README, specification updates (API coverage statuses, schema-verified CBOM mapping), explicit reporting of out-of-scope crypto libraries, and SARIF validation against the official OASIS 2.1.0 schema.
13. **Independent code and methodology review, round 1: verdict FAIL** (13 findings; Section 13). All findings were fixed with regression tests. Fixing them exposed and fixed two further consequences: wrong-half consumers in classes that hold either key half, and consumers reached through `self.public_key().<attr>`.
14. Independent review round 2: **PASS WITH FIXES**, with two conditions: the hybrid scope must require combined secrets, and negation stripping must not remove the real target. Both were fixed with regression tests (new module `pqscan/semantic/hybrid.py`), along with four minor items.
15. **Independent review round 3: verdict FAIL.** A fresh reviewer with new probes found that the hybrid check still accepted branch alternatives, ciphertext instead of the shared secret, logging, tuples, custom `encapsulate` classes, nested functions and fallback verifiers. It also found that the paramiko `is_available()` probe key received a recommendation. `hybrid.py` was rewritten conservatively and all 28 probes became regression tests.
16. **Confirmation round: verdict PASS WITH FIXES**, with 9 downgrade probes still accepted (A2 legacy early return, A3 helper shared by a legacy caller and A7 optional PQ verify were MAJOR). Fixed with a sole-sink rule, a top-level combiner with no intervening `return`, every-caller helper checks, verification guards, a message-rebinding check and a non-ML-KEM parameter check. All 12 probes became regression tests.
17. Test-count reconciliation and a timestamped final test log (Section 7).
18. Baseline execution-failure handling (Section 10a) and the frozen scoring policy (`docs/specification/scoring_policy.md`, Section 11).
19. Phase 2 closure fingerprint, this report's gate verdict, the PDF, and the Phase 3 readiness checklist (`docs/implementation/phase3_readiness_checklist.md`).

## 3. Technical and methodological decisions

| Decision | Justification |
|---|---|
| Module B discovers sites from the AST itself; Semgrep runs alongside and is joined by (file, line) | Semgrep stays the lecturer-required detector and the floor baseline; the AST layer needs the same sites with evidence attached. Semgrep-only candidates are reported separately. |
| Flow-insensitive typing; a parameter keeps its incoming value unless unconditionally reassigned at top level; self-referential reassignments typed against the other definitions | Bounded, predictable, explainable; path-sensitive reasoning is a documented limitation. |
| Unknowns that come from parameters stay in type unions | They represent real external callers; dropping them would overstate provenance completeness. |
| Two call levels for flows that leave a class; intra-class hops free but cycle-protected | Matches the specification's "bounded, one-to-two level" design while not penalising the class-wide attribute tracing already in scope. |
| Private helpers' returns traced to in-module callers; public functions and properties always count as an escape | External callers may exist for public API; a key that leaves the analysed scope cannot be given a single role with full confidence. |
| Tier computed only from evidence the arm may use | Keeps ablation arms comparable and consistent with the frozen T0–T3 definitions. |
| Policy as data with load-time invariants | A policy edit that breaks the ML-KEM/ML-DSA separation fails immediately. |
| Abstention on a determinate site scored UNASSESSABLE; on an indeterminate site CORRECT | Uses the frozen judgment enum (no new label), consistent with policy v1.1 Section 5. |
| B1 algorithm-family baseline uses the most common tool convention (RSA→ML-KEM, EC→ML-DSA); B1-dual refuses to choose | Two pre-stated variants avoid choosing a strawman. |
| CBOM without timestamps by default; serial number derived from content | Byte-identical output across runs (NFR1). |

## 4. Architecture and workflow

```
repository ──► safe walk (root-confined, no symlinks/junctions, size + time limits)
                 │
                 ├──► Module A  Semgrep CE 1.185.0, 28 rules (pyca, PyCryptodome, method candidates, PQC presence)
                 │                                         │ joined by (file, line)
                 └──► Module B  ast: imports → typing → arguments → consumers → SiteEvidence
                                   │
                                   ▼
                     Module C  decision table → role + tier T0–T3 + reason + conflicts   (arms for ablation)
                                   │
                                   ▼
                     Module D  policy v1.1 (YAML) → RECOMMEND {SIG | KEM | KEM_DEM}
                                                  | FLAG_NO_TARGET {INVENTORY | NO_ACTION_HYBRID | PROTOCOL_REVIEW}
                                                  | ABSTAIN (role UNKNOWN or tier < τ = T2)
                                   │
                                   ▼
                     Module E  CycloneDX 1.6 CBOM (schema-validated) | SARIF 2.1.0 | JSON
Module F/G: site labels + tool outputs (adapters) + pqscan arms → judgments → statistics
```

## 5. Files created or modified

| Path | Purpose |
|---|---|
| `pqscan/models.py` | shared data types |
| `pqscan/detect/runner.py`, `rules/{pyca,pycryptodome,common}.yaml` | Module A |
| `pqscan/semantic/{imports,apis,model,typer,args,consumers,evidence}.py` | Module B |
| `pqscan/semantic/hybrid.py` | combined-secret evidence for PQ/T hybrids, with downgrade guards |
| `pqscan/semantic/branches.py` | mutually exclusive branch detection (if/else, try/except) |
| `pqscan/bench/fileprobe.py` | tool-independent file condition (ok / syntax-error / null-byte / non-utf8) |
| `docs/specification/scoring_policy.md` | frozen primary and strict scoring (v1.0) |
| `scripts/tree_hash.py`, `docs/implementation/phase2_closure_fingerprint.json` | source-tree fingerprint (no git) |
| `tests/fixtures/baseline_errors/` | failure fixture repository, every tool's output and logs |
| `docs/implementation/phase3_readiness_checklist.md` | Phase 3 readiness |
| `docs/implementation/test_logs/phase2_final_pytest.log` | final verbose test and coverage log |
| `pqscan/roles/classifier.py` | Module C |
| `pqscan/policy/{engine.py,policy_v1_1.yaml}` | Module D |
| `pqscan/export/{cbom,sarif,jsonout}.py`, `export/schemas/bom-1.6.schema.json` | Module E (official schema kept as reference) |
| `pqscan/pipeline.py`, `pqscan/cli.py` | integration and CLI |
| `pqscan/bench/{judge,stats,run}.py` | Module F |
| `pqscan/baselines/{adapters,simple}.py` | Module G |
| `benchmark/baselines_manifest.json` | pinned baselines with invocations |
| `scripts/fetch_pinned.py` | rebuild repositories and baselines from pinned commits |
| `tests/test_*.py` (8 files), `tests/fixtures/` | 286 tests and fixtures |
| `experiments/dev/*.py`, `docs/dev/*` | development checks (not results) |
| `docs/pilot/raw_tool_outputs/pqblocks_*` | pqblocks-scan outputs on the pilot repositories |
| `docs/implementation/{opus_handoff_audit,phase2_code_audit,implementation_tracker}.md` | audit and tracking |
| `docs/specification/{api_coverage,role_taxonomy}.md` | coverage statuses; schema-verified CBOM mapping (taxonomy v1.0.1, roles unchanged) |
| `README.md`, `pyproject.toml` | install and usage; package metadata |

## 6. Tools, commands and environment

Windows 11 Home 10.0.26300; Python 3.12.10; Semgrep 1.185.0; cryptography 47.0.0; pycryptodome 4.4.0; cyclonedx-python-lib 11.12.0; scipy 1.18.1; statsmodels 0.15.0; Node v24.15.0 (PostQuant build); uv 0.12.23.

```
uv pip install --python .venv/Scripts/python.exe -e .
.venv/Scripts/python -m pytest -o addopts="" -q --cov=pqscan
.venv/Scripts/pqscan scan <repo> --format cbom -o <repo>.cbom.json
.venv/Scripts/python -m pqscan.bench.run --sites docs/pilot/h1_pilot_sites.csv --tool-outputs docs/pilot/raw_tool_outputs --repos <pilot_repos> --out docs/dev/pilot_harness
.venv/Scripts/python scripts/fetch_pinned.py repos <dest>
.venv/Scripts/python scripts/fetch_pinned.py baselines <dest>
```

## 7. Tests and actual outputs

| Test file | Tests | Covers |
|---|---|---|
| `test_detect_rules.py` | 10 | every `# expect:` fixture line matched; no finding on unmarked lines; metadata; import gate; determinism; confined default targets incl. `tests/`; outside-root targets ignored; failure handling |
| `test_semantic_typing.py` | 26 | aliases; typing of every key factory and loader; attributes; parameters (annotation, isinstance); one-level calls |
| `test_semantic_evidence.py` | 22 | receivers, arguments, consumers on paramiko- and python-jose-style idioms; tuple pairs; JWK two-step; `self.__class__`; peer keys; escapes; module-level `if` classes; inheritance |
| `test_roles.py` | 36 | each role and tier rule; conflicts; excluded kinds; arms; PyCryptodome; type-valid consumers; rebinding; origin consistency (T3→T2 cap); wrong-half filtering; same-class instance attributes |
| `test_policy.py` | 54 | exhaustive role × tier sweep; ML-KEM/ML-DSA separation; KEM_DEM "redesign" wording; threshold parameter; hybrid family must match the role; dual-stack legacy path is not a hybrid; combined paramiko-style hybrid is; invalid policies rejected |
| `test_pipeline_export.py` | 21 | end-to-end roles; Semgrep join; execution failures; scope; CycloneDX 1.6 and SARIF 2.1.0 schema validation; CBOM links; no secrets or planted literals; determinism; size limit; symlink (skipped: not permitted here); junction confinement for walker and Semgrep; per-file timeout stops only the slow file; unsupported libraries; CLI |
| `test_bench.py` | 49 | judging table; statistics cross-checked against statsmodels; **packaged adapters reproduce the published pilot judgments**; simple baselines; abstention on ineligible sites; negation-aware drop-in wording; parse failure as execution failure; labelled-method hit selection; external-tool execution failures per measured profile; failed files cannot change executed-site rates; strict scoring |
| `test_hybrid_review3.py` | 68 | every round-3 and confirmation-round reviewer probe (positives must be NO_ACTION_HYBRID, negatives never); capability probes; chained keygen; branch keys; ML-DSA operations excluded; 21 negation phrasings |

**Final run: 2026-11-14T07:05:11Z.** Command `.venv/Scripts/python -m pytest -o addopts="" -v --cov=pqscan --cov-report=term`; log `docs/implementation/test_logs/phase2_final_pytest.log`. Collected 286, **285 passed, 1 skipped, 0 failed**. The per-file counts above sum to 286. The skip is the symlink test: Windows refused unprivileged symlink creation, and the equivalent junction tests passed. Line coverage of `pqscan`: **89%**; every Module A–E file is at or above 86%. `pipeline.py` shows 75% because the coverage tool does not measure code that runs inside the analysis worker process. The pipeline tests exercise the worker path end to end.

Count reconciliation: earlier drafts of this report gave 202 passed (Section 12) and 208 passed (Section 7). Each figure was correct when written, because the suite grew with every review round: 202 after round 1, 208 after round 2, 261 after round 3 and 285 after the confirmation round. The 202 in Section 12 was stale. Every count in this report now refers to the final run above.

End-to-end development scans (all exit 0, CBOM validated against CycloneDX 1.6, zero execution failures):

| Repository (dev split) | .py files | Sites | RECOMMEND | FLAG_NO_TARGET | ABSTAIN | Wall time incl. Semgrep |
|---|---|---|---|---|---|---|
| paramiko 5.1.0 | 70 | 35 | 22 | 7 | 6 | 11 s* |
| python-jose 3.5.0 | 38 | 22 | 10 | 1 | 11 | 10 s* |
| PyJWT @16231abfd1 | 26 | 81 | 11 | 4 | 66 | 10 s* |
| Authlib @f817ad8a08 | 389 | 43 | 6 | 1 | 36 | 30 s* |

Site and action counts come from the final scans after every review fix (`docs/dev/e2e/*.summary.txt`, `*.cbom.json`, 14 Nov 2026). For paramiko, FLAG_NO_TARGET covers 4 INVENTORY sites and 3 NO_ACTION_HYBRID sites. *Wall times are from the round-2 scans and were not re-measured after the final fixes. Later spot checks put Semgrep's bare start-up at 9.5 s on the build machine under load, and pqscan's own analysis of Authlib's 389 files at 4.4 s without Semgrep.

In paramiko, the X25519 exchange of the `mlkem768x25519-sha256` key exchange (pilot site P16) is still recognised as an approved hybrid: its secret is returned to the caller and combined as `hash(k_pq + k_cl)` with the ML-KEM secret. After review round 3, the X25519 key generated only as an availability probe in `is_available()` (line 76) is KEY_MATERIAL_ONLY → INVENTORY. Its result is discarded, so it has no consumer, and taxonomy rule 3 applies. Lines 84, 111 and 112 (the genuine hybrid) remain NO_ACTION_HYBRID.

PyJWT's abstentions are dominated by test files (53 of 81 sites) and by keys returned from the public `prepare_key` API to callers in another module, which the bounded analysis cannot follow by design.

Development check on the 30 eligible pilot sites (circular: Module B was debugged against these sites; **not a result**):

| Method | Correct | Harmful | Undecided | Unassessable (abstained) | Missed |
|---|---|---|---|---|---|
| pqcheck 0.1.0 | 1 | 6 | 0 | 0 | 21 |
| pqc-audit 0.4.1 | 1 | 0 | 3 | 0 | 26 |
| PostQuant 0.7.0 | 4 | 3 | 3 | 0 | 20 |
| qsafe 1.1.0 | 6 | 2 | 0 | 0 | 22 |
| QSA regex | 7 | 5 | 3 | 0 | 15 |
| pqblocks-scan 0.1.0 (new) | 1 | 1 | 0 | 0 | 28 |
| B1 algorithm mapping | 11 | 9 | 9 | 0 | 0 |
| B1-dual | 2 | 1 | 27 | 0 | 0 |
| B2 method+args | 18 | 0 | 0 | 12 | 0 |
| B3 full, no abstention | 30 | 0 | 0 | 0 | 0 |
| B4 full, τ = T2 | 30 | 0 | 0 | 0 | 0 |

After the review fixes the full arm's tiers on these sites are T3 = 15 and T2 = 15 (previously T3 = 21, T2 = 9): attributes that can also hold an externally supplied key, and keys exposed through public properties, now count as incomplete evidence. This is the intended conservative effect.

The external-tool rows reproduce the Phase 1 pilot; only pqblocks-scan is new. The B-rows show the harness works end to end. They say nothing about generalisation.

## 8. Diagrams and plots

The architecture diagram is in Section 4; the pilot outcome figure is in the Phase 1 report. No new plots are produced in Phase 2, because no experiment was run.

## 9. Errors and debugging

| Problem | Diagnosis | Resolution |
|---|---|---|
| 5 failing Module B tests at handoff | diagnosed without edits (handoff audit Sec. 11) | five targeted fixes; one over-strong test corrected with a documented reason |
| `AttributeError: 'Instance' object has no attribute 'reason'` on paramiko | local-class instance type had no description | type moved into the shared model |
| chained `pkcs1_15.new(k).sign(...)` lost its signer site | inner and outer calls share line and column | duplicate guard keyed on the full span |
| self-alias `key = key.public_key()` reported as an escape | alias hops consumed the call-depth budget | visited set; self-aliases skipped |
| PyJWT methods invisible | classes inside module-level `if` not indexed | indexer descends through module-level `if`/`try`/`with` |
| pytest executed a fixture project's test file | fixtures directory collected | `norecursedirs` |
| Semgrep rule files rejected ("null values prohibited") | unquoted metadata values containing commas | values quoted; `semgrep --validate` passes (28 rules) |
| Semgrep invocation error with `--lang` | flag only valid with `-e` | flag removed |
| pqblocks-scan CBOM had no advice text | advice is in SARIF messages | adapter reads SARIF |
| Independent review round 1: 13 findings (Section 13) | each reproduced and fixed | regression test per finding |
| Fix for finding 2 marked python-jose public-key loaders as conflicting | a class holding either key half sees the other half's `.sign` | wrong-half consumers filtered silently (taxonomy rule 1); conflict only if nothing valid remains |
| python-jose public RSA key lost its `verify` consumer | `.verify(...)` reached through `self.public_key().prepared_key` not recognised | attributes of same-class instances returned by methods count as the same slot |
| Review round 3: 9 hybrid false-assurance patterns, L76 probe recommendation | presence- and mention-based combination check; bare-expression keygen treated as an escape | `hybrid.py` rewritten; bare expression = no consumer; 28 probes as tests |
| Confirmation round: 9 downgrade probes | combiner anywhere later in the block was accepted | sole-sink rule, top-level combiner, no intervening return, every-caller helpers, verification guards; 12 probes as tests |
| Generated regression-test file had real newlines inside string literals | escaping in a generator script | tail rewritten by hand |
| Suite slowed from 67 s to 114–139 s | Semgrep start-up (9.5 s per invocation on this machine), not analysis | none needed; recorded |
| Unicode print failures in the Windows console | cp1252 console | `-X utf8` |

## 10. Failures and unresolved issues

- CBOMkit (sonar-cryptography) remains not run: the Docker daemon is stopped on the build machine.
- Mehl's ESEM 2026 scanner: results-only artefact; repository-level comparison only.
- Not modelled by Module B (detected by Semgrep only): `DH.key_agreement`, DH parameter key generation, PKCS#12 loaders.
- PROTOCOL_CONFIG cannot be emitted (TLS/SSH configuration libraries are outside the supported scope).
- PostQuant's npm dependency tree reports 8 known vulnerabilities (npm audit). It runs only as an isolated baseline and is never a dependency of pqscan.
- Human review of the taxonomy, policy and pilot labels is still outstanding (Phase 1 condition).
- The approved-hybrid check is conservative: it may miss genuine hybrids, for example a combination spread across modules. A miss only produces a migration note, never false assurance. It shows data combination, not that the combiner meets SP 800-227 Sec. 4.6.
- Residual lexical limits in recommendation-text classification (for example "ML-DSA must not be replaced by ML-KEM" reads as DUAL). None of these forms occurs in any pinned tool's output.
- Branch-aware typing covers if/else and try/except alternatives only. Loops and early returns are still flow-insensitive.
- No git repository exists, so the Phase 3 code freeze needs either a git tag or a recorded tree hash.

### 10a. Baseline execution failures (resolved before Experiment A)

None of the six pinned tools records per-file failures in its report. Each was run on `tests/fixtures/baseline_errors/repos/errrepo`, which has one valid file, one syntax-error file, one non-UTF-8 file and one null-byte file, each containing the same RSA keygen and sign:

| Tool | Behaviour on failing files | Handling |
|---|---|---|
| pqcheck 0.1.0 | silently drops syntax-error and null-byte files | silence on such files = EXECUTION_FAILURE |
| pqc-audit 0.4.1 | same as pqcheck | same |
| PostQuant 0.7.0 | reports all files (regex fallback) | normal judging |
| qsafe 1.1.0 | reports all files | normal judging |
| QSA regex stage | silently skips the null-byte file | silence on null-byte files = EXECUTION_FAILURE |
| pqblocks-scan 0.1.0 | prints `Scan error: <path>` and exits 2 without writing any report | missing report = EXECUTION_FAILURE for every site of that repository; its log is parsed |

The profiles are recorded in `benchmark/baselines_manifest.json`. Every rate uses n_exec (sites where the method ran), and failures are reported in their own column. A test confirms that adding failed files leaves executed-site rates unchanged. All tools processed the non-UTF-8 file. Pilot numbers are unchanged, because no pilot file triggered a failure.

## 11. Deviations from the frozen methodology

- Role taxonomy v1.0.1: Section 6 (CBOM mapping) replaced by the schema-verified mapping; roles and rules unchanged.
- Judging: the pilot script had no ABSTAIN path (no baseline abstains). The packaged judge adds it using existing enum values (CORRECT on indeterminate sites, UNASSESSABLE on determinate sites). The regression test confirms the published pilot table is unchanged.
- pqblocks-scan added as a baseline (handoff instruction).
- Scoring frozen in `docs/specification/scoring_policy.md` v1.0 (2026-11-14), before any test-split action. The strict sensitivity analysis (drop-in wording on KEM-family sites counts as UNSUPPORTED_DROP_IN) is adopted, resolving open decision C2. Primary scoring is unchanged from policy v1.1 and is reported first in every table.
- The hybrid rule in policy v1.1 ("approved PQ component") is now implemented as "matching family and demonstrably combined". This is stricter than the text's "used in the same class or function", which earlier drafts encoded. The policy text is unchanged.

## 12. Validation gate (formal verdict, 14 Nov 2026)

| # | Criterion (master prompt, Phase 2 gate) | Result | Evidence |
|---|---|---|---|
| 1 | Every declared supported API has positive and negative fixtures | PASS: 33 rows at full depth; 3 rows (C16, C20, D11) at detection level only, with the gap stated | `api_coverage.md`; `tests/fixtures/semgrep/*` |
| 2 | All automated tests pass | PASS: 285 passed, 1 skipped (environmental), 0 failed | Section 7; final test log |
| 3 | Unsupported API patterns reported explicitly | PASS | `unsupported`, `semgrep_only`, `excluded`, `files_skipped` outputs; tests |
| 4 | Role classifier passes labelled unit tests | PASS | `test_roles.py` (36) |
| 5 | Recommendation-policy tests pass | PASS | `test_policy.py` (54); `test_hybrid_review3.py` (68) |
| 6 | CBOM validates against CycloneDX 1.6 | PASS (fixture and four real repositories; SARIF also validated against OASIS 2.1.0) | `test_pipeline_export.py`; `docs/dev/e2e/*.cbom.json` |
| 7 | End-to-end scanning on ≥ 2 real repositories | PASS (four development repositories; zero execution failures) | Section 7 |
| 8 | No private key or secret material emitted | PASS (PEM fixture; planted literals in arguments, targets and callees) | `test_no_secrets_or_source_in_any_output`, `test_no_string_literal_from_source_reaches_any_output` |
| 9 | Results reproducible from recorded input and configuration | PASS (deterministic CBOM; pinned rebuild reproduced baseline outputs; closure fingerprint `5cbe7392…f437` over 92 files) | `phase2_closure_fingerprint.json` |
| 10 | Independent code and methodology review completed | PASS: four reviews (round 1 FAIL → fixed; round 2 PASS WITH FIXES → fixed; round 3 FAIL → fixed; confirmation PASS WITH FIXES → all listed conditions fixed and every reviewer probe turned into a regression test) | Section 13 |
| 11 | Baseline execution failures distinguished from misses (handoff requirement before Experiment A) | PASS | Section 10a |
| 12 | Scoring rules frozen before held-out evaluation | PASS | `scoring_policy.md` v1.0 |

**Gate verdict: PASS. Phase 2 is complete.** The conditions carried from Phase 1 are unchanged and block Phase 3, not Phase 2: human review of the taxonomy, policy and pilot labels; an external annotator and adjudicator; the CBOMkit route. The last review round's verdict was PASS WITH FIXES. Its fixes were verified by turning the reviewer's own probes into regression tests; no further independent round was run after those fixes.

## 13. Independent code and methodology review

### Round 1 (verdict: FAIL)

An AI reviewer in a separate context, with read access to the repository and permission to run probes in a scratch folder, reproduced every finding below. Each was fixed and received at least one regression test.

| # | Severity | Finding (reviewer's words, condensed) | Fix |
|---|---|---|---|
| 1 | BLOCKER | Any ML-KEM or ML-DSA call in the same class made SIGN, VERIFY and KE sites NO_ACTION_HYBRID: an RSA signature next to ML-KEM was "no action" (false assurance) | approved PQ family encoded per role (ML-KEM only for KE; ML-DSA only for signatures); the policy refuses cross-family entries |
| 2 | MAJOR | Taxonomy rule 1 (type-valid consumers) not implemented; flow-insensitive name reuse let an RSA key inherit an X25519 `exchange` → RECOMMEND KEM | consumers filtered by algorithm and key half; algorithm-impossible consumers and incompatible rebinding are conflicts (tier T1 → abstain) |
| 3 | MAJOR | Per-file timeout did not stop the slow file and blamed the following files | analysis in a worker process; a timed-out worker is killed and replaced |
| 4 | MAJOR | Semgrep followed Windows junctions out of the root and read files there | Semgrep receives the confined explicit file list; out-of-root results dropped before any read; walker no longer enters junctions |
| 5 | MAJOR | Unparsed argument text, possibly secret literals, reached JSON output | kind labels only; evidence carries no source text |
| 6 | MAJOR | pqscan abstentions on ineligible sites escaped the false-positive count | reported ABSTAIN on an ineligible site is FALSE_POSITIVE_SITE |
| 7 | MAJOR | Drop-in flag asymmetric and fooled by "no drop-in replacement" | negation-aware detection applied to every method including pqscan |
| 8 | MINOR | Parse failures counted as MISSED in the benchmark | EXECUTION_FAILURE |
| 9 | MINOR | Semgrep silently skipped `tests/` | explicit targets (same fix as 4) |
| 10 | MINOR | Operations reached T3 even when their key's downstream use was inconsistent | T3 capped at T2 when the origin site spans families or has conflicts |
| 11 | MINOR | Role errors within the right family (public Ed25519 → SIGN; private key via public half → VERIFY; ECDH argument on sign unflagged) | fixed per taxonomy rule 1; operation/argument mismatches are conflicts |
| 12 | MINOR | README claimed protocol review and silent directory skips | README corrected (Known limits); skipped directories listed |
| 13 | MINOR | Hit selection ignored the labelled method; negated target mentions counted | labelled-method selection; negated mentions stripped. Adapter handling of tools' own error records unchanged (documented) |

Checked by the reviewer with no defect: no eval/exec/import of scanned code; the policy invariants; no drop-in wording in pqscan output; test-split repositories withheld.

### Round 2 (verdict: PASS WITH FIXES)

The reviewer re-ran all of its reproducers plus new probes:
- **Fixed:** findings 2–9, 11 and 12. It also confirmed no false conflicts on legitimate code (try/except loaders, branch keys, `None` defaults, key rotation, certificates, peer keys, PyCryptodome round trips) and that a hostile `.semgrepignore` is ignored.
- **Partially fixed:** findings 1, 10 and 13.
- **Conditions set for the gate:** (1) the same-class hybrid rule still excused a dual-stack legacy path, for example an X25519 `legacy()` method next to an ML-KEM `modern()` method; (2) negation stripping removed the real target ("No ML-KEM equivalent exists for signatures, migrate to ML-DSA" became NONE).
- **Required before Experiment A, not for the gate:** handle external tools' own per-file error records.

Fixes:
- Condition 1: `pqscan/semantic/hybrid.py` requires the classical and PQ results to meet in one expression within one function, following one return level. Regression tests cover the dual-stack class, ECDSA next to ML-DSA (combined vs. not combined), and the paramiko-shaped combination.
- Condition 2: only the negated token is removed.
- Minor items: an operation whose key may come from an untyped parameter is capped at T2; operation-level argument conflicts flow back to the key site; a key whose name is reused for a non-key object or another key is UNKNOWN under every threshold; labelled-method matching is exact; the README now says identifiers (not literals) appear in evidence trails.

### Round 3 (fresh reviewer, verdict: FAIL)

A new reviewer context wrote its own probes (28 cases: genuine composites, dual-stack code, branch alternatives, ciphertext mixing, logging, tuples, custom KEMs, nested functions, fallback and unrelated verifiers) and tested the real paramiko file.

| Area | Verdict | Key evidence |
|---|---|---|
| Genuine combined-secret hybrids (paramiko style) | PASS for key establishment; signature composites through `self` attributes missed (MINOR) | P1a–P1d → NO_ACTION_HYBRID; paramiko L84/L111/L112 → NO_ACTION_HYBRID |
| Rejection of non-combined dual-stack code | **FAIL (BLOCKER)** | N3 if/else secret, N4 ciphertext, N7 logging, N2/N8 tuple, N10 custom `RsaKem`, N11 nested def, S10 branch signature, S8/S12/S13 fallback or unrelated verification → false NO_ACTION_HYBRID |
| Negation-aware extraction | PARTIAL (MINOR) | 8 of 34 phrasings misclassified ("Avoid ML-KEM; use ML-DSA", "instead of", case) |
| paramiko `is_available()` L76 | **FAIL (MAJOR)** | RECOMMEND KEM for a discarded capability probe; by taxonomy rule 3 the correct outcome is KEY_MATERIAL_ONLY → INVENTORY (the defect the pilot criticised in pqcheck) |
| Regressions on legitimate code | PASS with MINOR issues | false conflict for the same name in exclusive branches; chained keygen escape; ML-DSA operations reported as sites |

Fixes:
- `hybrid.py` rewritten: single definitions; same block; shared secret only; ML-KEM- or ML-DSA-typed receivers (or an untyped parameter for KEMs); accepted combiner forms only; nested scopes ignored; the verification shortcut removed.
- A discarded keygen result is no consumer and no escape.
- Chained `keygen().public_key().op()` is traced.
- ML-DSA operations are excluded as sites.
- Branch-aware receiver typing and rebinding checks (`branches.py`).
- Case-insensitive negation with avoid / instead of / rather than / post-token forms.

All 28 probes are permanent tests. Suite after round 3: 261 passed, 1 skipped.

### Confirmation round (same round-3 reviewer, new probes; verdict: PASS WITH FIXES)

- Confirmed: discarded probes and chained keygen; new positives (X-Wing-style combiner, labelled `sha3_256` concatenation, composite signing through attributes); paramiko L76 → INVENTORY and L84/L111/L112 → NO_ACTION_HYBRID; 16 of 20 new phrasings.
- Not confirmed: 9 downgrade probes still gave NO_ACTION_HYBRID. Three were MAJOR: A2 legacy early return, A3 helper also used by a legacy caller, A7 PQ verify skipped when `strict` is false. Six were MINOR: A1 classical-only session key, A9 combination only under `if DEBUG`, A4 `compare_digest` matching "digest", A5 a non-ML-KEM object passed to an untyped parameter, A6 message rebound between signatures, A8 swallowed verification failure.
- MINOR: C5, the same name in if/else branches for two algorithm families, abstained.
- MINOR: four lexical phrasings.

Fixes:
- Sole-sink rule: the classical secret may be read only inside the combiner or in validation checks.
- The combiner is a top-level statement with no `return` between the definitions and it.
- A helper is followed only when private and when every in-module caller combines.
- Verification is rejected across a `return` or inside a swallowing `try`.
- The signed message must not be rebound.
- An untyped KEM parameter is rejected if fed a local class or a classical key.
- "digest" removed from combiner names.
- Uses in branches exclusive with the key's creation are ignored.
- Negation extended ("over", post-token forms limited to usage verbs).

All 12 confirmation probes plus C5, B4 and B6 and 9 phrasings became tests. Final suite: 285 passed, 1 skipped. Remaining known lexical limit: "ML-DSA must not be replaced by ML-KEM; keep ML-DSA" still reads DUAL. It is documented, and no pinned tool emits such text.

## 14. References

- Zhang, L. ICSE-Companion '26, DOI 10.1145/3774748.3795653; arXiv:2602.05759.
- NIST FIPS 203, FIPS 204, FIPS 205 (Aug 2024); NIST SP 800-227 (Sep 2025); NIST IR 8547 final (Oct 2026).
- CycloneDX 1.6 JSON schema, https://github.com/CycloneDX/specification (tag 1.6.1), `schema/bom-1.6.schema.json`.
- Semgrep CE 1.185.0; cyclonedx-python-lib 11.12.0.
- Baselines (pinned in `benchmark/baselines_manifest.json`): pqcheck, pqc-audit, PostQuant, qsafe, Quantum-Safe Auditor, pqblocks-scan (PyPI 0.1.0, github.com/PQBlocks/cbom-scanner).

## 15. Next-phase prerequisites

The full list with status is in `docs/implementation/phase3_readiness_checklist.md`. Phase 3 has not started, and the held-out test split has not been fetched or opened.

1. Human review of taxonomy v1.0.1, policy v1.1, scoring v1.0 and the 31 pilot labels by someone outside the build team. BLOCKED: needs a person.
2. Recruit an external annotator and an adjudicator; label at least 300 real sites (development and validation first, test only after the freeze). BLOCKED: needs people.
3. Build the synthetic benchmark generator (about 60 base cases × transformation operators). NOT READY.
4. Write the baseline batch runner that saves each tool's output and run log (needed to parse pqblocks-scan failures). NOT READY.
5. Find and verify a second PyCryptodome-using test repository, or report the shortfall. NOT READY.
6. Decide git tag versus recorded tree hash for the code freeze (user decision), then write the freeze record (code fingerprint, label hashes, policy, scoring, τ and manifests) before any test-split action.
7. Optional: start Docker Desktop so CBOMkit can run; otherwise it is reported as not run.

Done in Phase 2 (formerly items 1a and 2): baseline execution-failure handling (Section 10a) and the strict-scoring decision (`scoring_policy.md`).
