# Owner decisions G02, G03, G08, G10 (19 Nov 2026) and their implementation

Decided by the owner on 19 Nov 2026, after the verification in `second_review_closure.md`. Implemented in revision v1.0.5-r3 (`adoption_record_v1.0.5-r3.json`). Before any labelling and any test-split access. Pre-change texts are archived in `docs/specification/archive/v1.0.5-r2/` (and `archive/v1.0.4`, `archive/v1.0.5` where the earlier reviews saw the same text).

## Decision register

| ID | Owner decision (verbatim intent) | Implementation | Evidence | Scientific impact |
|---|---|---|---|---|
| G02 | `obvious_from_name` uses nullable Boolean semantics: true/false on eligible (applicable) records, null on ineligible (not applicable) records. A data-contract correction, not a label, sampling or estimand change. | Benchmark schema v1.1 (`type: [boolean, null]` plus conditional rules: eligible ⇒ boolean, ineligible ⇒ null); taxonomy rule 8, guide (Step A, type rules), data dictionary and AI-review prompt aligned; Dataset A regenerated with generator 1.1; pilot record migrated | 52 synthetic ineligible values `false` → `null`; 1 pilot value `n/a` → `null`; nothing else in any label changed (test compares every field with the archived generator-1.0 dataset); all 388 records validate against schema v1.1 | None: `obvious_from_name` feeds H1a on eligible sites only |
| G03 | Retain the F03 primary sampling and annotation rule; additional same-family calls are not extra primary sites; clarify the four units; keep denominators and labels; disclose the impact | Guide: candidate-discovery unit, sampling unit, primary annotated site, analysis unit; `notes` format `also-call: <api_call> @<line>:<column>`; taxonomy rule 7; protocol threats | At most 8 of 3,503 DV pool candidates are multi-call (E64) | None: primary sample, denominators and estimands unchanged; nothing expanded retrospectively |
| G08 | H4 Part 1 uses the F-A baseline set; exact identifiers from the registry; T0-only comparators separate; CBOMkit and Mehl exclusions kept | Run specification JSON (authoritative) and Markdown; registry `pqscan/bench/h4.py` | Part 1 = pqcheck, pqc-audit, PostQuant, qsafe, QSA-regex, pqblocks-scan, pqscan:B1-algorithm, pqscan:B2-method-args. Proposed analyser pqscan:B4-full-T2 (Part 2). B1-dual descriptive (D15). T0 comparators B3-full-noabst, method-args-recv-T0, method-only-T0 separate. Excluded: CBOMkit (D4 = A), Mehl (results-only) | Fixes the H4 tool set before any evaluation; no threshold change |
| G10 | Keep the signed guard and its threshold; before F1 run an additional pre-specified calibration of heterogeneous repository gaps with the existing procedure and criteria; stop before F1 if it fails | `scripts/g10_calibration.py`; analysis plan Sec. 11.7 | **PASS**: worst Type I 0.0183 at α = 0.025 (limit 0.0297); cancellation case 0.0062; near-threshold case 0.0092; power at δ_r = +0.04: 0.158–0.219. Seeds `default_rng([20261113, 21, tid, chunk])`, tid 9001–9008 | Guard, threshold and p-values unchanged; planning-model evidence only |

**Interpretation recorded for G08.** "Include the seven specified pqscan arms" is implemented as: all seven runnable pqscan arms are enumerated with their roles in the inventory; Part 1 contains only those that are registered F-A baseline arms (B1-algorithm, B2-method-args), because the same decision keeps T0-only comparators separate and B1-dual is descriptive only under D15. If the owner intended all seven arms in Part 1, that is a separate decision.

## Hashes

| Artefact | Before | After |
|---|---|---|
| `benchmark/synthetic/sites.jsonl` | `a18c023ea62ec714a2ae41ca9dbb896411428ecc5f87bb751190c782dbae6b2e` | `a2f8f354f3638e172fb58ba2d2e0b60f8fa6a7377cdd1d08549d51939e545390` |
| `benchmark/synthetic/manifest.json` | `2dbb9c4c9300b66d292825b0dfee9a1dc8c095b90eb945538899a296cebf1cb6` | `eabe8951e85753c8ac66d431492eb3bab70435e63b8d288099f2206d11756c35` |

The generator-1.0 dataset files are archived in `benchmark/synthetic/archive/generator-1.0/`; the pilot record before migration in `docs/pilot/archive/h1_pilot_sites_pre_g02.csv`. The 388 case files changed only on line 1 (generator version in the header docstring); candidate IDs, which depend on file path and line, are unchanged. Every record's `commit` field (generator hash) changed with the generator.

## New finding during this work (not decided; owner decision required)

**N1 — PyCryptodome post-quantum APIs.** The installed PyCryptodome 4.4.0 provides `Crypto.PublicKey.MLKEM`, `MLDSA` and `Hybrid`. The scanner's approved-hybrid encoding (`approved_hybrid_prefixes`) recognises only the pyca ML-KEM/ML-DSA prefixes, and the guide's list of PQ components (pyca `mlkem`/`mldsa`, `oqs`, `pqcrypto`) does not name PyCryptodome. A PyCryptodome-based PQ/T hybrid would therefore not be recognised by the scanner and is not explicitly covered by the labelling rule. Changing either alters labelling scope or scanner behaviour before F1; it is recorded as a limitation until the owner decides.

## Current G01–G11 closure matrix (after r3, 19 Nov 2026)

Source of the earlier statuses: `second_review_closure.md` (r2, kept unchanged apart from an appended pointer). The review was an isolated AI specification review with owner decisions, **not** independent human validation.

| ID | Finding (short) | Status after r3 | Closed by | Residual limitation |
|---|---|---|---|---|
| G01 | PROTOCOL_CONFIG branch missing in the guide | **CLOSED** | r2 (guide, taxonomy) | Kind (c) reserved in the current frame |
| G02 | `obvious_from_name` n/a vs boolean | **CLOSED** | r3, owner decision (schema v1.1, generator 1.1, pilot migration) | None for estimands; historical records keep the old representation (archived) |
| G03 | Same-family extra calls | **CLOSED** (F03 rule retained) | r3, owner decision (units, notes format, disclosure) | Up to 8 of 3,503 candidates' extra same-family calls are notes, not site records |
| G04 | "No scanners" vs frozen batch run | **CLOSED** | r2 | Compliance self-attested |
| G05 | Hypothesis labels in the forbidden list | **CLOSED** | r1 (`370549c`) | Lexical detection only |
| G06 | Fail-closed AI submission | **CLOSED** | r1 (`370549c`) | Bypass outside the tool is procedural |
| G07 | H3 comparison bases | **CLOSED** | r2 | — |
| G08 | H4 tool set | **CLOSED** | r2 inventory + r3 owner decision (frozen Part 1 set, registry `h4.py`) | Interpretation of "seven pqscan arms" recorded above |
| G09 | Hybrid detector needs combination | **FALSE POSITIVE**; comment fixed | r2 | — |
| G10 | Signed coverage-gap guard | **CLOSED** (rule retained; additional calibration PASS) | r2 diagnostics + r3 calibration | Planning-model evidence; says nothing about scanner accuracy |
| G11 | Tool-attribution isolation | **MITIGATED** | r2 | Procedurally controlled and self-attested, not technically enforced |

**Still open (outside G01–G11):** external human review (F1 prerequisite), 14-day intra-rater interval, pilot figure, W6, N1 (above).

**Update (19 Nov 2026, appended; text above unchanged).** Third-review finding TB01 asked for confirmation of the G08 interpretation. The owner confirmed that H4 Part 1 is exactly the eight registered F-A baselines and that the other five pqscan arms are reported separately; inclusion is by F-A membership only. Record: `owner_decision_g08_confirmation_2026-11-19.md`. G08: CLOSED, interpretation confirmed.
