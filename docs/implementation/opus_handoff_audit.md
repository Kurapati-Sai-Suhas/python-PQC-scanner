# Handoff audit — context reconciliation (Opus 5.5 takeover)

Project: **Post-quantum crypto scanner for Python projects** (title fixed).
Base paper: Lei Zhang, "Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography Migration", ICSE-Companion '26, pp. 402–403, DOI 10.1145/3774748.3795653, arXiv:2602.05759. A two-page vision poster proposing QSSE and the AQuA framework (P1 detection/inventory, P2 semantic refactoring, P3 hybrid verification). It reports no implementation and no evaluation; nothing in this project attributes a scanner or metrics to it.
Audit date: 13 November 2026. Auditor: Claude Opus 5.5, taking over from Claude Fable 5.1 in the same session.

Method: every statement below was checked against files on disk or a command run during this audit. Where a statement rests only on the earlier conversation, it says so.

## 1. Project summary

A research prototype that scans a Python repository (without executing it), finds RSA/ECC usage in PyCA `cryptography` and PyCryptodome, infers the cryptographic role of each call site from bounded evidence (receiver, arguments, key provenance, consumers), maps the role to an ML-DSA / ML-KEM migration direction or abstains, and exports a CycloneDX 1.6 CBOM. The research contribution is a role-labelled benchmark and the measurement of recommendation correctness across existing scanners and our analyzer.

## 2. Original requirements

Lecturer (mandatory, L1–L4): detect RSA/ECC in Python; Semgrep rules; CBOM; ML-KEM/ML-DSA migration suggestions. User process requirements across prompts: research-first; three phases with gates; a Markdown report and a PDF per phase; no fabrication; independent review; frozen held-out data; tracker with NOT_STARTED / IN_PROGRESS / IMPLEMENTED / TESTED / VALIDATED / BLOCKED.

## 3. Frozen research direction (verified in `docs/specification/*`, `docs/research/02_final_decision_summary.md`)

- **N1 (primary):** PyPQC-RoleBench, a role-labelled benchmark measuring correct / incorrect (harmful) / undecided / abstained / missed recommendations per call site.
- **N2 (technical):** bounded key-provenance-aware role inference with evidence-tier (T0–T3) abstention; contribution only as a *measured* improvement.
- **N3 (supporting):** robustness under semantics-preserving transformations (MASC, Statfier are prior art).
- Not claimed as novel: Semgrep, CBOM generation, AST/alias/interprocedural/taint analysis, key provenance as a technique, abstention, the L1–L4 combination.

## 4. Important decisions from earlier discussion (with where they are recorded)

| Decision | Record |
|---|---|
| Base paper and title fixed | memory, every spec header |
| Benchmark-first framing after hostile audit (verdict B, CONDITIONAL GO) | `docs/research/02_final_decision_summary.md` |
| Scope: pyca + PyCryptodome; RSA/EC core; X25519/Ed25519/DH/DSA as extensions | `docs/specification/system_requirements.md`, `api_coverage.md` |
| Role taxonomy v1.0 frozen after pilot and independent re-derivation | `docs/specification/role_taxonomy.md` |
| Policy v1.1 (NIST-verified; KEM_DEM "redesign, not replace"; hybrid transitional) | `docs/specification/recommendation_policy.md` |
| τ = T2 pre-registered; tiers ordinal, no numeric confidence | policy Sec. 4, `data_dictionary.md` Sec. 3 |
| Pre-registered hypotheses H1a ≥ 25%, H1b ≥ 10% | `evaluation_protocol.md` Sec. 1 |
| No LLM in the core pipeline | `system_requirements.md` Sec. 4 |
| Consensus API key pasted in chat must be rotated; never stored in files | conversation; `phase1_report.md` Sec. 14 |

## 5. Research findings and corrections from previous audits

- Hostile audit (12 Nov 2026) removed six candidate novelty claims and kept three source-verified facts: no inspected Python-capable tool infers role from evidence; none measures recommendation correctness; none abstains.
- Independent policy review corrected three MAJOR issues (legacy-use attribution, hybrid permanence, PROTOCOL_CONFIG scoring) → policy v1.1.
- Independent annotation review found six taxonomy ambiguities → taxonomy rules 7–9; pilot site P15 split.
- H1 pilot (30 eligible sites, paramiko 5.1.0 + python-jose 3.5.0): 16/30 name-undeterminable; 4/30 indeterminate; baseline harmful + undecided 7–27%. Kill criterion not triggered. Re-verified in this audit: `docs/pilot/h1_pilot_sites.csv` has 31 rows, 30 eligible; join script output unchanged.

## 6. Prior art named in the handoff prompt — reconciliation

| Item | In project documents? | Status |
|---|---|---|
| Cryptolation (IEEE TSE 2024, DOI 10.1109/tse.2024.3377182) | yes (01, 02 docs) | peer-reviewed; abstract/paper-level verified earlier |
| CryptoPyt (ACSAC 2024, DOI 10.1109/acsac63791.2024.00088) | yes | peer-reviewed |
| Cryptbara (IEEE/ACM ASE 2025, DOI 10.1109/ase63991.2025.00133) | yes | peer-reviewed; abstract only (audit Sec. 14 item 2) |
| Cryptoscope (Moffie et al., arXiv:2503.19531) | yes (01 Sec. 2) | **preprint**; Java only |
| Pallarés de Bonrostro, González-Tablas, González Vasco 2026 (arXiv:2606.07341) | yes (01 Sec. 2) | **preprint**; LLM migration of 800 Python fragments with roles labelled by hand |
| ccPASTpqc (Wahlang et al., CODS-COMAD 2025) | yes (01 Sec. 2) | peer-reviewed; abstract only |
| MASC, Statfier | yes | peer-reviewed (S&P 2022 / ESEC/FSE 2023) |
| HyBind (IACR ePrint 2026/2347) | yes | **preprint**; PDF blocked earlier (audit Sec. 14 item 3) |
| pqc-audit, PostQuant, pqc-posture/qsafe, CBOMkit, Quantum-Safe Auditor | yes; source-inspected and pinned | four of five run in the pilot; CBOMkit blocked (Docker) |
| **pqblocks-scan** | **no — new in this audit** | source-inspected 13 Nov 2026, see below |

**pqblocks-scan 0.1.0** (PyPI; source github.com/PQBlocks/cbom-scanner, commit 3d1eccfdfc, 2026-10-27, Apache-2.0, 0 stars, created 2026-10-25). Source facts (`src/pqblocks_scan/discovery.py`, `deadlines.py`): a hybrid `ASTDiscovery` + `RegexDiscovery`. AST matching keys on the *names* `RSA.generate`, `rsa.generate_private_key`, `ec.generate_private_key` (receiver name compared literally, e.g. `node.func.value.id == "RSA"`, comment calls it "a heuristic"), not on resolved imports. Every `ec.generate_private_key(ec.SECP256R1())` becomes asset `ECDSA-P256`, whose deadline text is "replace with ML-DSA-65", so an ECDH key would receive a signature target. RSA assets receive "transition to ML-KEM-768 / ML-DSA-65" (dual target). No sign/verify/exchange/encrypt/decrypt operations, no key loaders, no role field, no abstention. It emits CycloneDX 1.6 and SARIF. Conclusion: it matches the pattern of the other inspected tools and does not weaken the three surviving facts. It should be added to the baseline list (Module G).

## 7. Files and documents reviewed in this audit

All of `docs/research/` (01, 02 ×3), `docs/specification/` (6), `docs/benchmark/` (5), `docs/pilot/` (CSV, joined CSV, summary, analysis, manifest, figure, 34 raw outputs), `docs/implementation/` (phase1_report, tracker), `docs/reports/Phase_1_*` (MD and PDF), `benchmark/real/manifest.json`, `pyproject.toml`, all of `pqscan/` and `tests/`, `experiments/`, `scripts/`, the memory files, and the previous session's scratchpad (baseline clones, pilot repositories, NIST text extractions, Mehl artefact, candidate clones).

## 8. Current architecture (as implemented)

```
pqscan/
  models.py            Location, Candidate, enums (Library, CandidateKind, Role, Tier, Provenance)
  detect/              Module A: runner.py + rules/{pyca,pycryptodome,common}.yaml (28 rules)
  semantic/            Module B: imports.py, apis.py, model.py, typer.py, args.py, consumers.py, evidence.py
  (roles/ policy/ export/ bench/ baselines/ cli.py — not yet created)
experiments/pilot/     pilot join, plot, QSA driver (research tooling, not packaged)
experiments/bench/     verify_candidates.py (repository verification)
scripts/               build_pdf_report.py
```

Module B discovers sites itself from the AST; Module A (Semgrep) is run independently. The plan is to join the two by location so that Semgrep stays the lecturer-required detector and the AST layer supplies evidence. This join is not implemented yet.

## 9. Completed components and evidence

| Component | Evidence | Verified now |
|---|---|---|
| Phase 1 specification set (6 docs) | `docs/specification/*.md` | yes, files present and consistent |
| Policy v1.1 with NIST line-level citations | policy Sec. 1, 7 | yes |
| H1 pilot | `docs/pilot/*`; re-ran nothing, inspected outputs | yes |
| Benchmark schema, annotation guide, split process | `docs/benchmark/*` | yes |
| Real-repository manifest frozen before Module C | `benchmark/real/manifest.json` (frozen 2026-11-13; dev 4, val 2, test 6) | yes |
| Phase 1 report and PDF | MD + PDF, 9 pages, all 14 sections, embedded DejaVu fonts, page footer | yes (text extraction and rendered pages checked) |
| Module A Semgrep rules | `tests/test_detect_rules.py` 6/6 pass | yes, run in this audit |
| Module B typing | `tests/test_semantic_typing.py` 26/26 pass | yes |

## 10. Incomplete components

Module B evidence assembly (5 of 16 tests fail), Modules C, D, E, F (packaged), G (packaged), CLI, Semgrep↔AST join, security hardening (traversal/symlink/timeouts at the CLI level), reproducible baseline setup, Phase 2 report and PDF, all of Phase 3.

## 11. Known bugs and technical debt

1. **Five failing Module B tests** (diagnosed, not yet fixed):
   - attributes assigned from a constructor parameter are not typed from in-module constructor calls (`RSAKey(key=key)`), so `self.key` loses the RSA/generated origin and the PARAMETER marker;
   - `_merge` drops parameter-derived `Unknown` options, so external-caller provenance disappears;
   - a parameter reassigned only conditionally loses its incoming value (`key = load_pem_public_key(key)` inside `if`);
   - curve arguments given as class attributes (`self.curve`) are not resolved;
   - consumer tracing treats `key = key.public_key()` as an escape because alias hops consume the call-depth budget; a static method's first parameter is treated as `self`.
   - One test expectation (`private is False` after a conditional `key = key.public_key()`) needs path-sensitive reasoning that the documented flow-insensitive design does not provide; the test will be corrected and the limitation documented.
2. **Reproducibility debt:** baseline clones, pilot repositories, NIST extractions and candidate clones live in the previous session's scratchpad, outside the project. A setup script that re-creates them from pinned commits is needed.
3. **No git repository.** Phase 3 code freeze needs a git tag or a recorded tree hash.
4. `pqscan/detect/runner.py`: leftover no-op loop; Semgrep per-file errors are attached to the first candidate instead of a run report.
5. `api_coverage.md` still shows every row NOT_STARTED although Module A covers most rows at detection level.
6. Tracker entry 1.6 says the PDF has 8 pages; it has 9.

## 12. Contradictions between prompts, documents and implementation

| # | Contradiction | Resolution in this audit |
|---|---|---|
| C1 | The handoff prompt lists four judgment / action values (CORRECT, INCORRECT, UNASSESSABLE; RECOMMEND, ABSTAIN, NO_FINDING, EXECUTION_FAILURE). The frozen data dictionary is richer (adds FLAG_NO_TARGET, DETECTED_ONLY, UNDECIDED, UNJUSTIFIED, FALSE_POSITIVE_SITE, OVER_RECOMMENDATION). | Keep the frozen schema (the prompt itself says not to redefine labels). The prompt's values are a subset; a mapping is in Sec. 13. |
| C2 | The first implementation prompt lists UNSUPPORTED_DROP_IN as a harm category. Policy v1.1 scores drop-in wording as CORRECT plus a flag reported beside harmful counts. | Unresolved research decision. Primary scoring stays v1.1; a pre-registered secondary "strict" scoring (drop-in = INCORRECT / UNSUPPORTED_DROP_IN) is proposed and needs the user's decision before Phase 3 freeze. In the pilot no tool's text triggered the flag, so no reported number changes. |
| C3 | Prompts require "at least one independent person"; all reviews so far were AI reviewers in separate contexts. | Open condition carried from Phase 1. |
| C4 | Taxonomy includes PROTOCOL_CONFIG, but `api_coverage.md` lists the `ssl` module and protocol libraries as unsupported, so the scanner cannot emit PROTOCOL_CONFIG in v1. | Recorded as a limitation; the role stays in the taxonomy for labelling; the analyzer will never claim it. |
| C5 | Handoff prompt names pqblocks-scan as a market tool; earlier audits did not cover it. | Covered now (Sec. 6). |
| C6 | The first implementation prompt asked to examine "the latest Consensus independent audit supplied in the conversation". Only the first-turn Consensus prior-art report exists in this conversation. | Marked unavailable (Sec. 14). |

## 13. Outcome-value mapping (handoff prompt → frozen schema)

| Handoff value | Frozen value(s) |
|---|---|
| RECOMMEND | RECOMMEND |
| ABSTAIN | ABSTAIN |
| NO_FINDING | NO_FINDING (judged MISSED on an eligible site) |
| EXECUTION_FAILURE | EXECUTION_FAILURE (never counted as MISSED) |
| CORRECT | CORRECT |
| INCORRECT | INCORRECT (always with a harm category) |
| UNASSESSABLE | UNDECIDED (dual target) or UNJUSTIFIED (single target on an indeterminate site); both reported separately |
| ROLE_INCOMPATIBLE / FALSE_ASSURANCE / OTHER | same |
| UNSUPPORTED_DROP_IN | `dropin_wording` flag in primary scoring; harm category in the proposed strict scoring (C2) |
| — | FLAG_NO_TARGET → DETECTED_ONLY; OVER_RECOMMENDATION; FALSE_POSITIVE_SITE (detection level) |

## 14. Missing information that cannot be recovered

- ChatGPT conversations the user ran in parallel: not accessible; not analysed.
- The "latest Consensus independent audit" referenced in the first implementation prompt: not present in this conversation.
- The screenshot described in the handoff prompt: described in text only; no image is attached; its contents match the plan list shown in this session.
- No human reviewer has been named; no human annotation exists.

## 15. Exact next implementation tasks (priority order)

1. Fix the five Module B defects listed in Sec. 11 and correct the one over-strong test; re-run Modules A and B.
2. Module C: deterministic role classifier with evidence tiers T0–T3, reasons, conflicts; labelled unit tests including the pilot idioms.
3. Module D: policy v1.1 as a versioned table with abstention at τ = T2; exhaustive policy tests (no SIG↔KEM substitution).
4. Module E: CycloneDX 1.6 CBOM, validated against the bundled official schema, plus semantic link tests and a no-secrets test.
5. CLI integrating A→E with safe traversal, timeouts and an end-to-end scan of two development repositories; then Module F/G packaging (adapters from the pilot scripts, simple mapping baselines, pqblocks-scan added) and the Phase 2 gate.

## 16. Feasibility under the frozen scope

Feasible. The critical path is software (Modules B–E, CLI) that an analyzer of this size can deliver. The real risks are outside the code: human annotation of ≥ 300 real sites with an external annotator, and the human review of the taxonomy and policy. Those block Phase 3, not Phase 2.
