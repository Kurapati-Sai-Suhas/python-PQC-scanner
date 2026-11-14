# Hostile novelty audit — evidence log (work in progress)

Inspection date: 12 Nov 2026. This file holds source-verified facts gathered for the hostile audit before the session's usage limit was reached. The two deliverables (`02_hostile_novelty_audit.md`, `02_final_decision_summary.md`) are NOT yet written; they must be built from this log plus `01_research_feasibility_report.md`.

## Pinned competitor versions (GitHub API, 12 Nov 2026)

| Repo | Head commit | Date | Latest release | Stars | License |
|---|---|---|---|---|---|
| postquantdev/postquant | 4dc61b7965 | 2026-03-05 | v0.7.0 (2026-03-05) | 0 | MIT |
| Rafael-Ryu/pqcheck (default branch `develop`) | 3e99c742a3 | 2026-07-15 | pqcheck-v0.1.0 (2026-07-13) | 0 | Apache-2.0 per README |
| Miles0sage/quantum-mcp (pqc-posture/qsafe, branch `master`) | ff4f6dc384 | 2026-03-26 | v0.1.0 (2026-03-25) | 0 | MIT per README |
| AnimeshShaw/quantum-safe-auditor | 4d695503e6 | 2026-09-26 | v1.1.0 (2026-04-19) | 1 | MIT |
| rauleteee/pqc-scanner (PyPI `pqc-audit` 0.4.1, branch `develop`) | b5ccaac159 | 2026-10-27 | 0.4.1 (PyPI 2026-08-11) | 0 | MIT |
| franceme/cryptolation | eb0be0800a | 2024-03-20 | Release_2023-09-18 | 1 | GPL-3.0 |
| cryptolation/PyCryptoBench | d51d6bda4e | 2021-08-07 | none | 0 | none shown |
| advanced-security/cbom-action | e73233dcd4 | 2026-06-29 | v1.0.1 (2023-11-28) | 16 | MIT |
| github/codeql | fbf9fca5ce | 2026-11-11 | n/a | 10,344 | MIT |
| PQCA/sonar-cryptography, PQCA/cbomkit, CycloneDX/cdxgen | API returned "Moved Permanently"; use cbomkit/* and CycloneDX/cdxgen canonical names; sonar-cryptography 1.7.0, cbomkit 2.3.0 per report 01 | | | | |

Newly found (not in report 01): PQCWorld/pqaudit (npm, TypeScript, 4 stars, regex for Python), Pyhroff/pqc-scanner (Python AST, 1 star), rexcoleman/pqc-migration-analyzer (regex + CVE ML scoring), anthonyharrison/cbom4python (empty README, 1 commit), qproof 0.4.0 (PyPI, regex, CBOM 1.6, RSA → "ML-KEM, ML-DSA"), qorex 0.0.1 (RSA → "ML-KEM / ML-DSA"), crypto-scanner 0.1.2 (Quantum Shield Labs, regex). Many more hobby repos exist (GitHub search "pqc-audit" returns 66).

## Source-verified capability facts (the ones that decide novelty)

**pqcheck 0.1.0 (develop 3e99c74)** — `detectors/python_detector.py` is an `ast.NodeVisitor` with scope-aware alias resolution; catalog in `detectors/algorithms.py` covers pyca, PyCryptodome, hashlib, oqs, etc. BUT: instance methods (`key.sign()`, `key.exchange()`, `key.encrypt()`) are NOT catalogued; only constructors/keygen/padding markers. `models.py` has no usage/operation field; comment in `algorithms.py`: `ec.generate_private_key` "can't reveal sign-vs-exchange use". Policy `cryptoct-default.yaml`: `RSA (family asymmetric-encryption) → "Shor — migrate to ML-KEM-768"` for every RSA finding; `ec.generate_private_key` is family SIGNATURE → "migrate to ML-DSA-65" even when the key is for ECDH. `policy/engine.py`: `context` rule field is parsed but unevaluated ("needs usage-context the detector does not emit in v0.1"). Confidence is per detection path (1.0 / 0.9 / 0.7 / 0.5), does not affect gating. CBOM: CycloneDX 1.6 by hand, `evidence.occurrences`, primitive, parameterSetIdentifier, NO `cryptoFunctions`. Evaluation: tuning set 10 repos (384 HIGH/CRITICAL, 0 FP; recall 1.00 vs 584 sites), held-out 6 repos recall 0.9867 (297/301), precision 0.9904 (103/104); detection-level only; held-out used for fixes afterwards.

**pqc-audit 0.4.1 (develop b5ccaac)** — `detectors/ast_engine.py` matches calls by import root + last two dotted components; `findings.py` has `Usage` enum {key_generation, signing, key_exchange, encryption, hashing, dependency, configuration, data_at_rest} but it is HARD-CODED PER RULE, not inferred. No instance-method rules (no sign/verify/encrypt/decrypt/exchange). RSA has only keygen rules → target string "ML-KEM (key establishment) / ML-DSA (signatures)" (undecided). EC keygen → "ML-KEM (ECDH) / ML-DSA (ECDSA)". No key-loading rules (load_pem_*, import_key, JWK import). No unknown/abstain outcome, no confidence field. CBOM 1.6 with `cryptoFunctions` but signing/key_exchange/key_generation all map to ["keygen"]. No precision/recall figures; benchmarks/ has only a runner script.

**PostQuant 0.7.0** — AST patterns (`src/scanner/code/ast/patterns/python.ts`) match only `generate`, `generate_private_key`, `generate_parameters`; pyca RSA keygen is category "asymmetric-encryption" while PyCryptodome `RSA.generate` is "digital-signature" (library-dependent, not use-dependent); migration strings are dual ("ML-KEM … or ML-DSA …"). Regex file has `python-rsa-sign` (`.sign(` with PSS/PKCS1v15) and `python-ecdh-exchange` (`.exchange(ec.ECDH())`) — the only use-level patterns. No RSA encrypt/decrypt, no verify. `risk-assessor.ts` infers "context" from nearby-word regexes (sign/verify/signature → digital-signature; key_exchange/kex/handshake → key-exchange; password/auth → authentication) with a priority table. `variable-resolver.ts`: single-file, literal assignments only; `import-resolver.ts`: top-level imports only. CBOM 1.6 includes `cryptoFunctions`, primitive by category, nistQuantumSecurityLevel. No evaluation.

**pqc-posture/qsafe** — regex table in `pqc_posture.py`; "RSA Key Exchange" bucket (18 regexes incl. `RSA\.generate`, `PKCS1_OAEP`, `PKCS1_v1_5`, `pkcs1v15`, KMS key-spec strings) → "ML-KEM 768"; "RSA Signature" (5 regexes, `.*sign`) → "ML-DSA 65". Test demotion by path substring (`test/` also matches `latest/`). CBOM is a non-standard layout (top-level `cryptoProperties.algorithms`). "Zero false positives verified" claim rests on 44 self-written stress tests; no labelled ground truth.

**CBOMkit sonar-cryptography 1.7.0 (pyca rules, from report 01)** — sign/decrypt/exchange only on receivers typed from `generate_private_key`; `VERIFY_RSA` commented out; no RSA encrypt; no DH/X25519 exchange; Ed25519/X25519 keygen only; no PyCryptodome.

**CodeQL Python models (github/codeql main)** — `frameworks/Cryptography.qll`: key generation (rsa/dsa/ec generate_private_key with key size), `Cipher(...).encryptor()/decryptor().update` as one `CryptographicOperation` (encrypt/decrypt not distinguished), hashes; NO sign/verify/exchange for pyca; NO key loaders. `frameworks/Cryptodome.qll`: `Cipher.*.new` methods, `Signature.*.new` sign/verify (only sign/verify model), hashes; operation kind is a private field, not exposed. Concept exposes algorithm, block mode, inputs only.

**GitHub cbom-action / CodeQL CBOM blog (Dec 2023)** — abstract crypto model, languages/libraries not named, no PQC recommendation, no evaluation numbers, no per-asset field list, no link to the query pack.

**Pyhroff/pqc-scanner** — Python AST (imports + hashlib call sites), "intentionally remains syntactic, not data-flow"; recommendations dual per algorithm; fixture-level metrics only (8 fixtures). **PQCWorld/pqaudit** — regex for Python, AST for JS/TS only; algorithm-keyed targets; CBOM 1.6; confidence values are static not measured. **rexcoleman/pqc-migration-analyzer** — regex (19 primitives); "+14pp" is AUC-ROC on 21,142 CVEs vs a 0.494 baseline, not code-level.

**Cryptolation / PyCryptoBench repos** — READMEs nearly empty; PyCryptoBench repo contains "source files and the json dictionary containing the truth" (1 commit, 2021); no role/PQC content.

## Literature added this session (abstract-verified via Consensus MCP, 3 results/query)
- CrySL (Krüger et al., IEEE TSE 2019) and CogniCrypt (ASE 2017): typestate/lifecycle specs for Java crypto objects — prior art for "key lifecycle" reasoning; Java only.
- Statfier (Zhang et al., ESEC/FSE 2023) and SAFuzzer (ASE 2026): semantics-preserving transformations to test static analyzers — methodology precedent for the robustness benchmark; Segura et al. TSE 2016 survey.
- LLM4SA (Wen et al., ACM TKDD 2024), ZeroFalse (Iranmanesh et al., 2025 arXiv), Gnieciak et al. (IEEE Access 2025): LLM triage of static warnings — precedent for an LLM adjudication baseline; none target crypto roles.

## Consensus API
`GET https://api.consensus.app/v1/search` (quick_search deprecated, removal 2027-02-07) with header `x-api-key: <key>` returned HTTP 200 with `results/page/page_size/is_end/next_page`; `Authorization: Bearer` returned 401. The MCP connector remains on the 3-result tier. The key was pasted into chat: rotate it after use. Not yet used for systematic queries.

## Still to do for the audit
1. Consensus API sweep (10–12 focused queries, page_size ≥ 20) across: key provenance, protocol-role classification, Python interprocedural crypto analysis, PQC recommendation engines, CBOM evaluation, selective prediction in SE, static-analyzer robustness, LLM security triage, automated PQC migration.
2. Venue-specific checks (USENIX Security, NDSS, CCS, TSE, ICSE 2025–2026) — WebSearch quota was exhausted before these ran.
3. Component-by-component attack (16 components), three-level cross-examination, ≤5 ranked candidates, methodology attack, feasibility, three reviewer reports, GO/NO-GO, unverified-claims list.
4. Write `02_hostile_novelty_audit.md` and `02_final_decision_summary.md`.

## Provisional reading (not a verdict)
Every inspected open tool either (a) hard-codes usage per pattern, (b) emits dual "ML-KEM / ML-DSA" strings for RSA and EC, or (c) assigns the role by library rather than by call; none matches instance methods on loaded keys, none abstains, none reports recommendation-level correctness. That keeps the role-inference-plus-measurement claim alive, but the audit must still test whether roles are usually obvious from method names in real code (H1 pilot) before calling it a contribution.
