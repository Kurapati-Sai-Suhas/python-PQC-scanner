# Hostile novelty audit: "Post-quantum crypto scanner for Python projects"

Audit date: 12 November 2026. Companion to `01_research_feasibility_report.md` (first review) and `02_audit_evidence_log.md` (raw source-inspection notes). Decision summary in `02_final_decision_summary.md`.

Fixed constraints honoured throughout: official title unchanged; base paper fixed as Lei Zhang, *Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography Migration*, ICSE-Companion '26, pp. 402–403, DOI 10.1145/3774748.3795653 (Crossref-verified), arXiv:2602.05759; lecturer requirements (RSA/ECC detection, Semgrep rules, CBOM, ML-KEM/ML-DSA recommendations) retained.

Evidence legend: ✔ verified at source this audit (full text, source code, schema, registry metadata) · ◐ abstract or metadata only · ○ relayed from earlier reports, not re-verified · [PR] peer-reviewed · [pre] preprint · [repo] code inspected · [doc] vendor/README.

---

## 1. Executive research verdict

**Verdict: B — CONDITIONAL GO, with the contribution re-centred.**

The audit set out to reject the proposal and partly succeeded. Three of the six "contributions" in the current proposal do not survive as novelty: Semgrep detection, CycloneDX CBOM generation, and alias/wrapper resolution are all established (Section 5). "Confidence scoring" as proposed is not defensible and should be replaced by discrete evidence tiers. The LLM is unnecessary in the core pipeline and belongs only in a baseline arm.

What survives, after inspecting the source of nine open scanners and two new peer-reviewed 2026 studies, is narrower than the proposal but real:

1. **No inspected tool infers the cryptographic role of an RSA/EC call site from the call itself.** Every open scanner either hard-codes a role per pattern (pqc-audit `Usage` enum, pqc-posture regex buckets, PostQuant category per pattern), assigns the role by library rather than by use (PostQuant: pyca RSA keygen → "asymmetric-encryption", PyCryptodome RSA keygen → "digital-signature"), emits an undecided dual target ("ML-KEM / ML-DSA": Quantum-Safe Auditor, pqc-audit, qproof, qorex, Pyhroff/pqc-scanner), or maps all RSA to ML-KEM (pqcheck policy). CBOMkit's pyca rules capture `sign`/`decrypt`/`exchange` only when the receiver is the literal result of `generate_private_key`; no verify, no public-key encrypt, no key loaders. CodeQL's Python models expose algorithm and block mode, not operation kind, and model no key loaders. The ESEM 2026 scanner (Mehl) classifies vulnerable/safe/PQC-ready and explicitly does not prescribe migration.
2. **No inspected paper or tool measures whether a PQC recommendation is correct for the site it is attached to.** All published numbers are detection precision/recall (pqcheck, Mehl, Shaw, Crypsy, Cryptoscope) or repository-level readiness labels (Yuan et al., ASE 2026), or functional correctness of migrated fragments whose category was labelled by hand (Pallarés de Bonrostro et al.).
3. **No inspected tool abstains.** pqc-audit has no unknown outcome; pqcheck's `context` policy field is parsed but unevaluated; Shaw's confidence is a tier constant.

Therefore the defensible contribution is **(a) a role-labelled Python benchmark and the first measurement of role-incorrect ("harmful") and undecided PQC recommendations across existing scanners, and (b) a bounded, key-provenance-aware role-inference analyzer with evidence-gated abstention that is shown, on that benchmark and on held-out repositories, to reduce harmful recommendations at a stated coverage.** The analyzer is the vehicle; the measurement is the paper. This ordering matters: even if the analyzer underperforms, (a) stands.

Conditions attached to the GO: run the 30-site H1 pilot first (Section 11); freeze held-out repositories before writing any rule; use at least one annotator outside the build team with κ reported; pin the five baselines by commit; do not claim CBOM, Semgrep or abstention as contributions; present the work as instantiating Pillar P1 of the base paper, not AQuA as a whole.

---

## 2. Verified base-paper analysis (revalidated)

Nothing in the first report's base-paper analysis was contradicted. Additional checks this audit:

| Item | Status |
|---|---|
| Identity | ✔ Crossref: title, sole author Lei Zhang (UMBC), *Proceedings of the 2026 IEEE/ACM 48th ICSE*, ICSE-Companion '26, Posters, pp. 402–403, published 12 Apr 2026. ✔ Consensus API record (publish_date 2026-04-12, 4 citations as indexed). |
| Content | ✔ Two pages; defines QSSE; gaps G1 (no code-level semantics in CBOM-oriented approaches), G2 (no refactoring patterns/automation), G3 (no PQC-tailored continuous verification); AQuA pillars P1 detection, P2 refactoring, P3 verification. P1 text: inventories "rarely capture where cryptographic operations sit in the control and data flow of a system, which protocol roles they implement, or how changes … would propagate". |
| What it lacks | ✔ No definitions, no tool, no data, no metrics. "Protocol role" is undefined; the project must define it operationally. |
| Citation by competitors | ✔ Mehl (ESEM 2026) does not cite it; the Consensus API shows 4 citing works (not enumerated here). |
| Correct framing for this project | Extend P1 only. State explicitly that P2 (refactoring engine) and P3 (side-channel/differential verification) are out of scope except for an optional single-pattern validation. |

A reviewer objection to pre-empt: "A two-page poster is a thin foundation." Answer: it is the lecturer's fixed reference and is used as motivation and vocabulary; all technical comparators are the peer-reviewed detection and misuse literature.

---

## 3. Updated literature review (independent re-investigation)

Method: 12 Consensus API queries (20 results each, 12 Nov 2026, `GET /v1/search`), 15 title look-ups for full abstracts, arXiv/PDF reads where open, Crossref for DOIs, web searches for venue checks (one web-search quota interruption; Dagstuhl, arXiv, IACR and GitHub were reached directly). IEEE Xplore and ACM DL block automated reads; those records come via Consensus/Crossref metadata and are marked ◐.

### 3.1 Papers that change the picture relative to the first report

| Paper | Venue, year | Problem and method | Data and results | Limitations (stated or evident) | Overlap with us | Unsolved |
|---|---|---|---|---|---|---|
| Mehl, L. *PQC-Readiness of Open-Source Software: An Empirical Study*. DOI 10.4230/LIPIcs.ESEM.2026.53 | ESEM 2026, Emerging Results track [PR] ✔ full text | Multi-language scanner (Python `ast`, Java/Go tree-sitter); Python: imports of 11 libraries and 14 call patterns (e.g. `RSA.generate`, `ECC.generate`, `load_pem_private_key`); labels vulnerable / quantum-safe / PQC-ready; confidence high for calls, medium for imports | 14,508 GitHub repos; reference set n = 19 repos: precision 1.00, recall 0.93 (has_vulnerable) and 0.88 (has_pqc_ready), repository-level, single annotator; Zenodo 10.5281/zenodo.19634475 | "measures where source code still relies on quantum-vulnerable public-key primitives rather than prescribing how to migrate"; no data flow, no aliases, custom wrappers "not captured"; path-based test heuristic; dynamic calls missed | High on detection and on the vulnerable/safe label; Python catalogue overlaps ours | Call-site roles; recommendation; provenance; call-site-level ground truth |
| Yuan, T. et al. *Post-quantum Cryptography in the Wild: Assessing the Readiness of Open-Source Ecosystems*. DOI 10.1145/3832783.3837461 | ASE 2026 [PR] ◐ abstract (no open copy) | Two-stage "PQC Scanner": package-level crypto detection, then repository-level binary PQC-support label from commit history, source analysis and LLM agent post-verification | 1,117,913 packages, 8 ecosystems; recall lower bound ≥ 97.48% (219 negatives audited); precision 1.000 on 247 repos; 1.88% show PQC support | Repository-level label, not call sites; LLM cost/stability | Low on technique; high on framing ("source-level readiness") | Call-site role and recommendation |
| Cho, S., Yu, S., Woo, S. *Cryptbara: Dependency-Guided Detection of Python Cryptographic API Misuses*. DOI 10.1109/ase63991.2025.00133 | ASE 2025 [PR] ◐ abstract | Static intra-/inter-procedural dependency extraction encoded into LLM prompts for context-sensitive misuse detection | F1 95.43% and 84% on two benchmarks vs ≤ 73.68%/70.59% for prior tools; 22 confirmed misuses | Misuse, not PQC; LLM-dependent | Prior art for "inter-procedural crypto-object context in Python" | Role for migration; deterministic provenance |
| Ahn, J. et al. *HyBind: Structural Analysis of PQ/T Hybrid Cryptographic Usage*. IACR ePrint 2026/2347 | preprint [pre] ◐ abstract (PDF blocked) | Intraprocedural Python analysis with "registered API contracts"; checks that hybrid key derivation and signature acceptance depend on both components | 50 fixtures + 33 programs match specified counts; no P/R | Intraprocedural; contracts per API; hybrid-specific | Role contracts for KEM/derivation vs signature acceptance exist here | Classical-site role inference and recommendation |
| Christakis, M. et al. *Testing Static Taint Analyzers with Equivalence Modulo Taint*. DOI 10.1145/3832231 | FSE/PACMSE 2026 [PR] ◐ | Oracle-free robustness testing of taint analyzers (FlowDroid, Mariana Trench, Pysa, Semgrep) via flow-preserving variants | 16 confirmed issues | Taint, not crypto roles | Methodological precedent for a label-free robustness check on Semgrep-based detection | Role-invariance oracle |
| Zhang, H. et al. *Statfier* (ESEC/FSE 2023, DOI 10.1145/3611643.3616272 ◐) and *SAFuzzer* (ASE 2026) | [PR] ◐ | Semantics-preserving transformations to test static analyzers | 79 and 42 analyzer bugs | General analyzers | Methodological precedent for our transformation operators | Crypto-role-specific operators |
| Xiong, B. et al. *From Hallucination to Precision: … Python Cryptographic API Misuses with Chain-of-Thought*. DOI 10.1109/cscwd68734.2026.11582031 | CSCWD 2026 [PR] ◐ | CoT-prompted LLM detection on PyCryptoBench | 100% precision; recall 65.79% → 89.47% vs Cryptolation | PyCryptoBench only | LLM baseline design for Python crypto | Role/PQC |
| Mallick, T. et al. *Classifying Implementations of Cryptographic Primitives and Protocols that Use Post-Quantum Algorithms*. DOI 10.1145/3750555.3811889; arXiv:2503.17830 | SACMAT 2026 [PR] ✔ arXiv v4 | Runtime telemetry (CPU/memory) classifiers for classical vs PQ key exchange and signatures | 98–100% binary accuracy | Dynamic, binaries/protocols, no source | None technically; shows "KE vs signature" is treated as the primary axis elsewhere | Source-level |
| Lee, E. et al. *Taxonomy-Driven Cryptographic Dependency Inventory for PQ Migration in Decentralized Systems*. DOI 10.1145/3774905.3794696 | WWW 2026 companion [PR] ◐ | Taxonomy + inventory schema + P0–P3 triage rules | Worked example only | No tool, no experiments | Inventory fields include role-like category | Automation |
| Campbell, R. *Agentic Cryptographic Debt*. DOI 10.3390/computers15090625 | *Computers* 2026 [PR] ◐ | LLM agents asked to migrate RSA-JWT signing to ML-DSA; scored by static analysis + execution | 56 runs, no successful migration; Qwen3-Coder substituted Ed25519 | Two repos; descriptive | Evidence that automated migration fails without correct role/target reasoning | Role-correct guidance upstream of migration |
| Näther, C. et al. *Toward a Common Understanding of Cryptographic Agility*. DOI 10.1109/access.2026.3728196 | IEEE Access 2026 [PR] ◐ | Systematic review, 48 sources; layer model | Definitions | Conceptual | Vocabulary | — |
| Ye, X., Tan, T. G., Zhou, J. *Towards Discovering Quantum-Threats for Applications Using Open-Source Libraries*. DOI 10.1007/978-3-031-61486-6_17 | LNCS 2024 [PR] ◐ | 11 keywords for RSA/ECC/DH in Python | precision/accuracy > 90% | Keyword level | Shows the "basic Python PQC scanner" is 2024 prior art | Everything beyond keywords |
| Xue, Z. et al. *Actionable Warning Is Not Enough* (ICSE-C 2026); Hu, H. et al. *Suppressed Static Analysis Warnings* (FSE 2025); Du, X. et al. *Reducing False Positives in Static Bug Detection with LLMs* (ICSE-SEIP 2026); Wen, C. et al. LLM4SA (TKDD 2024); Iranmanesh, M. et al. ZeroFalse (2025, pre) | [PR]/[pre] ◐ | Actionability/abstention/triage literature | — | Not crypto | Confirms abstention and triage are established methods | Application to recommendation correctness |

### 3.2 Papers from the first report re-confirmed by the API sweep
Cryptolation (TSE 2024), CryptoPyt (ACSAC 2024), LICMA (ESEM 2021), Cryptoscope (arXiv 2025), Crypsy/"Hidden Ciphers" (LNCS/ICICS 2026), BF-CBOM (ICPC 2026), Shaw (arXiv 2604.00560), Pallarés de Bonrostro et al. (arXiv 2606.07341), MASC/"Why Crypto-detectors Fail" (TOPS 2026, DOI 10.1145/3796221), Chen et al. (NDSS 2024), Xia et al. (FSE 2025), CrySL (TSE 2019), CogniCrypt (ASE 2017), CryptoGo (ACSAC 2022), Gopher (CCS 2024), CamBench (2022), Afrose et al. (TSE 2022), Mousavi et al. *Detecting Misuse of Security APIs: A Systematic Review* (CSUR 2025, DOI 10.1145/3735968), Yamamuro SoK (ICISSP 2026), Hasan et al. (IEEE Access 2024), Rattanavipanon et al. (IEEE Access 2024), Näther SLR (IEEE Access 2024), Rameshan & Messmer (2026, pre), PyCG (ICSE 2021), InferCG (TOSEM 2026).

### 3.3 Retrieval limits
Consensus API: 20 results per query, 12 queries plus 15 look-ups; relevance-ranked, so long-tail venues may be missed. IEEE Xplore/ACM DL/Semantic Scholar blocked automated reads (Cryptbara, Yuan et al. read from abstracts only). Web search quota interrupted once. Chinese-, German- and Japanese-language venues not searched. Google Scholar not directly queried.

---

## 4. Competitor capability matrix

Inspection date 12 Nov 2026; commits and versions as in `02_audit_evidence_log.md`. Legend: Y yes · N no · P partial · ? not verifiable · — not applicable. Numbered columns follow the 14 questions in the brief: (1) RSA/ECC detection · (2) Python · (3) pyca + PyCryptodome · (4) aliases · (5) wrappers/cross-function · (6) loaded keys (PEM/DER/JWK/env/param) · (7) classifies actual role · (8) distinguishes sign/verify/enc/dec/KE · (9) role-specific PQC target · (10) abstains · (11) CycloneDX CBOM · (12) evaluates recommendation correctness · (13) public benchmark · (14) demonstrated limitation (one line).

| Tool (pin) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 Demonstrated limitation | Ev. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CBOMkit / sonar-cryptography 1.7.0 (PQCA) | Y | Y | pyca only | Y (Sonar frontend) | N (receiver must be `generate_private_key` result) | N | P | sign, decrypt, exchange only; verify commented out; no encrypt | N | N | Y 1.6 with `cryptoFunctions` | N | N | Roles only for in-place keys; PoC quantum-safe check defaults unknown to safe | ✔ repo |
| pqcheck 0.1.0 (develop 3e99c74) | Y | Y | Y + hashlib, oqs | Y (scope-aware) | N ("No dataflow analysis") | N | N (family proxy only) | N (no instance-method rules) | N: RSA→ML-KEM-768 always; `ec.generate_private_key`→SIGNATURE→ML-DSA-65 | N (`context` parsed, unevaluated) | Y 1.6, no `cryptoFunctions` | N | tuning 10 repos + held-out 6 (detection only) | README: "usage-context blindness" | ✔ repo |
| pqc-audit 0.4.1 (develop b5ccaac) | Y | Y | Y + 20 roots | Y (import-bound names only) | N | N (no loaders) | P hard-coded `Usage` per rule | keygen rules only; no sign/verify/enc/dec/exchange matching | P: DH/X25519→ML-KEM, Ed25519/DSA→ML-DSA; RSA and EC→"ML-KEM / ML-DSA" undecided | N (no unknown outcome) | Y 1.6; signing emitted as `keygen` | N | N | No precision/recall | ✔ repo |
| PostQuant 0.7.0 (4dc61b7) | Y | Y (AST + regex) | Y | Y (top-level imports) | N ("No cross-function data flow") | N | P (nearby-word heuristics: sign/verify→digital-signature) | AST: keygen only; regex: `.sign(` w/ PSS/PKCS1v15 and `.exchange(ec.ECDH())` | P: dual strings; category by library | N | Y 1.6 with `cryptoFunctions` | N | N | Role assigned per library, not per use | ✔ repo |
| pqc-posture 0.4.0 / qsafe 1.2.0 | Y | Y (regex) | Y (strings) | N | N | N | P regex buckets | "RSA Key Exchange" bucket includes `PKCS1_OAEP`, `RSA.generate`, KMS strings | P: bucket→ML-KEM 768 / ML-DSA 65 | N | Non-standard layout | N | N | Self-written stress tests only | ✔ repo |
| Quantum-Safe Auditor 1.1.0 (4d69550) | Y | Y (regex, 12 langs) | strings | N | N | N | N (LLM labels production/test/safe) | N | N: RSA→"ML-KEM / ML-DSA" | N | N | N | N | Single-labeller eval; FN defined as zero | ✔ paper+repo |
| Mehl ESEM 2026 scanner (Zenodo 10.5281/zenodo.19634475) | Y | Y (`ast`) | Y (11 libs, 14 patterns) | ? | N (wrappers "not captured") | P (`load_pem_private_key` is a pattern, flagged vulnerable, no role) | N | N | N (no recommendations by design) | N | N | N | reference set n=19 repos (repo-level) | Repo-level labels; TLS import heuristic | ✔ paper |
| Yuan et al. ASE 2026 "PQC Scanner" | Y (package/repo level) | Y | ? | ? | ? | ? | N | N | N | N | N | N | audit samples | Repository-level binary label | ◐ |
| Pyhroff/pqc-scanner (18 commits) | Y | Y (`ast`) | Y | Y | N ("intentionally syntactic") | N | N | N | N (dual strings) | N | N | N | 8 fixtures | Fixture-level metrics | ✔ repo |
| PQCWorld/pqaudit (npm, 4★) | Y | regex only | manifests | N | N | N | P rule category | N | N (dual) | N | Y 1.6 | N | N | Static "confidence" constants | ✔ README |
| qproof 0.4.0, qorex 0.0.1, crypto-scanner 0.1.2 | Y | regex | strings | N | N | N | N | N | N (dual) | N | qproof Y / qorex planned / N | N | N | Regex | ✔ PyPI |
| rexcoleman/pqc-migration-analyzer | Y | regex | ? | N | N | N | N | N | table only | N | N | N | CVE AUC | "+14pp" is AUC on CVEs vs 0.494 baseline | ✔ repo |
| Cryptolation (franceme, GPL-3.0) | Y (misuse) | Y | Y (59 modules) | Y | Y (inter-procedural, variable inference) | P (flows) | N | N | N | N | N | N | PyCryptoBench 1,836 | Misuse rules; repo README empty | ✔ repo/◐ paper |
| CryptoPyt (ACSAC 2024) | Y (misuse) | Y | Y (21 libs) | Y | Y (taint) | P | N | N | N | N | N | N | PyCryptoBench + PCAMD | Code not located | ◐ |
| Cryptbara (ASE 2025) | Y (misuse) | Y | ? | ? | Y (inter-procedural deps + LLM) | ? | N | N | N | N | N | N | two benchmarks | LLM-dependent | ◐ |
| Cryptoscope (IBM) | Y | N (future work) | — | — | Y (Java slicing) | Y (Java) | P (Java operations) | P | N (future) | N | N (model only) | N | CamBench | Java only | ✔ paper |
| Crypsy | Y | N (Ruby/Go) | — | — | P | P | P | P | N ("does not compute migration strategies") | N | Y 1.7 | N | Cryben (OSF) | Not Python | ✔ paper |
| CodeQL Python models (github/codeql main) | Y (keygen, ciphers) | Y | Y | Y (API graph) | Y (data flow) | N (no loaders modelled) | N | P (PyCryptodome `Signature` sign/verify only; pyca enc/dec merged) | N | N | via cbom-action (fields unknown) | N | N | Operation kind not exposed | ✔ source |
| cdxgen `cbom` | ? | Y (atom) | ? | ? | ? | ? | ? | ? | N | N | Y 1.6 | N | N | Not inspected in depth | ◐ |
| Semgrep registry | weak-key rules only | Y | — | Y (CE) | CE intraprocedural; Pro cross-file | — | N | N | N | N | N | N | — | No PQ ruleset found | ✔ docs |
| IBM Quantum Safe Explorer | Y | Y | ? | ? | ? | ? | ? | ? | remediation in other products | ? | Y | ? | N | Closed; no public eval | ◐ |
| SandboxAQ AQtive Guard | Y | N (no Python source evidence) | — | — | — | — | Y at rule level (KE vs signature rules) | P | P | ? | Y | ? | N | Network/Java evidence; docs login-gated | ◐ |

Reading of the matrix: columns 7–10 and 12 are empty or partial for every Python-capable open tool. Column 5 is solved only by misuse detectors (Cryptolation, CryptoPyt, Cryptbara, CodeQL) that do not do 7–10. That intersection is the project's space.

---

## 5. Component-by-component attack report

Format per component: A need · B exists? · C their limitation (evidence) · D our difference · E strongest rejection · F evidence-backed answer · G decision.

**5.1 Semgrep detection.** A: lecturer requirement; cheap candidate generation with rule tests. B: Semgrep is used as a baseline in Cryptolation and CryptoPyt; weak-key rules exist in the registry; no PQ ruleset found. C: CE is intraprocedural by design (Semgrep docs); registry has no PQ rules. D: none that is research. E: "A Semgrep ruleset is engineering." F: agree; present as Module A and as the *floor baseline* (name-based mapping), never as a contribution. G: **Keep as requirement, remove from novelty claims.**

**5.2 API coverage (pyca + PyCryptodome, RSA/EC/DH).** A: without instance-method coverage roles cannot be inferred. B: pqcheck and pqc-audit cover constructors/keygen for both libraries; CBOMkit covers pyca `sign`/`decrypt`/`exchange` for in-place keys; Mehl covers 14 patterns. C: verified: no open tool catalogues `key.sign/verify/encrypt/decrypt/exchange` on arbitrary receivers; CBOMkit's `VERIFY_RSA` is commented out and there is no encrypt rule. D: an operation-level catalogue for both libraries including loaders and verify/encrypt. E: "Coverage is a table, not research." F: correct; it is enabling work and must be published as part of the benchmark artefact; the measured delta it produces is the evidence. G: **Keep as infrastructure; claim only the measured effect.**

**5.3 Python AST analysis.** A: needed to reach method calls and receivers. B: Mehl, pqcheck, pqc-audit, Pyhroff all use `ast`. C: all stop at import-bound names; none resolves receivers. D: receiver and provenance resolution (5.6). E: "Everyone uses ast." F: agree; the AST is not the claim. G: **Keep, no claim.**

**5.4 Alias and wrapper resolution.** A: realistic code aliases imports and wraps calls. B: aliases: pqcheck (scope-aware), pqc-audit, PostQuant, Pyhroff, CBOMkit, CodeQL. Wrappers/cross-function: Cryptolation, CryptoPyt, Cryptbara, CodeQL (misuse context). C: among PQC scanners, wrappers are unresolved (pqcheck "no dataflow", PostQuant "no cross-function", Mehl "custom wrappers … not captured"). D: applying one-level wrapper unwrapping to role inference. E: "Established technique (MASC showed detectors fail on exactly these; Cryptolation solved variable inference in 2024)." F: concede the technique is established; the novelty is only the measured role-invariance under these transformations (Section 5.16). G: **Keep as mechanism; claim only the robustness measurement.**

**5.5 Interprocedural analysis.** A: keys are generated or loaded in one function and used in another. B: Cryptolation (inter-procedural data flow), CryptoPyt (taint), Cryptbara (inter-procedural dependencies), CodeQL, Semgrep Pro (paid). C: none of these targets PQC roles; among PQC scanners none is interprocedural. D: bounded (one call level, same package) propagation of key type/algorithm/provenance to use sites. E: "Reinventing a weaker Cryptolation." F: the honest answer is to **reuse** rather than reimplement where licences allow (Cryptolation is GPL-3.0; PyCG is Apache-2.0) and to show the role-F1 gain attributable to interprocedural resolution in an ablation; if the gain is small, say so. G: **Keep bounded; reuse existing call-graph tooling; ablate.**

**5.6 Key provenance inference.** A: the role of an RSA key loaded from a PEM file, JWK or parameter is undetermined at load; provenance plus downstream use decides it; this is the single most common production shape. B: Conceptually: CrySL/CogniCrypt typestate (Java), Cryptoscope slicing to key material (Java), CodeQL key-generation models. Among Python PQC scanners: none models loaders (pqc-audit "No rules for load_pem_private_key"; CBOMkit receivers must be `generate_private_key`; CodeQL Python has no loader models; Mehl flags `load_pem_private_key` as vulnerable without role). C: as listed; all verified at source. D: provenance kinds {generated, loaded-PEM/DER, loaded-JWK/JWT, parameter, attribute, env/KMS stub, unknown} attached to each use site and used both for role evidence and as an abstention trigger. E: "Typestate/lifecycle analysis is 2019 work; for Python it is a smaller Cryptolation." F: the claim is not the analysis but the *finding*: what fraction of real sites need provenance to decide role (H1), and the harmful-recommendation reduction when it is used. If H1 is small, the component is demoted. G: **Keep as the core mechanism, conditional on the H1 pilot.**

**5.7 Cryptographic role classification.** A: ML-KEM and ML-DSA serve different roles; SP 800-227 says a KEM is not a drop-in for public-key encryption. B: CycloneDX 1.6 `cryptoFunctions` enum; CBOMkit partial; pqc-audit hard-coded `Usage`; PostQuant heuristic contexts; AQtive Guard rule split (network); HyBind role contracts (hybrid); de Bonrostro labels categories by hand. C: verified: no Python tool infers role from receiver + method + arguments + provenance + sinks; pqcheck's catalogue comment "can't reveal sign-vs-exchange use"; pqc-audit emits `signing` as `keygen` in its CBOM. D: deterministic evidence model producing a role with a tier and contributing sites; taxonomy {SIGN, VERIFY, KEY_ESTABLISHMENT, PK_ENCRYPT, PK_DECRYPT, KEY_MATERIAL_ONLY, PROTOCOL_CONFIG, UNKNOWN}. E: "Role is read off the method name; trivial." F: show with numbers the share of sites where the method name is absent (keygen/load only), ambiguous (PKCS1v15 used for sign and encrypt), or wrapped. The ESEM and pqc-audit catalogues contain exactly these keygen-only sites, which is why they emit dual targets. G: **Keep as the central claim, contingent on H1.**

**5.8 PQC recommendation mapping.** A: lecturer requirement; roles map to target classes. B: every scanner has a table; pqc-audit's `targets.py` already splits KE→ML-KEM, signatures→ML-DSA for DH/X25519/Ed25519/DSA. C: the tables are applied to algorithm names or hard-coded usages, hence dual or wrong targets for RSA/EC (verified in pqcheck, pqc-audit, PostQuant, Shaw, qproof, qorex). D: the table itself is not new; conditioning it on an inferred role, with an explicit "KEM + AEAD redesign, not a drop-in" class for PK_ENCRYPT and "protocol/library migration" for PROTOCOL_CONFIG, and reporting correctness, is. E: "A lookup table." F: agree it is a table; the measured difference between name-keyed and role-keyed application is the result. G: **Keep; fix the table a priori from FIPS 203/204 and SP 800-227 and publish it before experiments.**

**5.9 Confidence scoring.** A: proposal wanted a numeric confidence per recommendation. B: pqcheck (per-path constants), Shaw (tier constants), pqaudit (static percentages), Mehl (high/medium). C: none is calibrated; Shaw's are assigned, not estimated. D: proposal offered nothing better. E: "Uncalibrated scores are decoration; a reviewer will ask for reliability diagrams you cannot produce with 400 cases." F: cannot be answered convincingly. G: **Remove numeric confidence. Replace with ordinal evidence tiers (T0 none … T3 direct method + resolved key + consistent sink) and evaluate abstention per tier.**

**5.10 Abstention.** A: when evidence is insufficient a wrong target is worse than none. B: abstention/selective prediction is established in ML and in warning triage (Rathnasuriya ICSE-C 2026; actionable-warning literature). C: no PQC scanner abstains (verified: pqc-audit no unknown; pqcheck context unevaluated; Shaw none). D: abstention gated on evidence tier, reported with coverage. E: "Abstention lets you hide errors; also not novel." F: never report error without coverage; publish risk–coverage curves; compare tools at equal coverage. Do not claim abstention as novel; claim the measured trade-off. G: **Keep as evaluation discipline, not as a contribution.**

**5.11 CycloneDX CBOM.** A: lecturer requirement; interoperability. B: CBOMkit, pqcheck, pqc-audit, PostQuant, Crypsy, cdxgen all emit CBOMs; schema already has `cryptoFunctions`. C: pqc-audit emits `signing` as `keygen`; pqcheck omits `cryptoFunctions`; pqc-posture's layout is non-standard; BF-CBOM shows generators disagree. D: role-correct `cryptoFunctions` with per-site evidence and an explicit abstention property; validated against the schema. E: "CBOM output is not research." F: agree. G: **Keep as requirement; the only evaluable element is link/role correctness of the emitted CBOM, reported as a secondary result.**

**5.12 Evidence traceability.** A: reviewers and developers need to see why a role was assigned. B: CBOMkit/pqcheck/PostQuant emit `evidence.occurrences`; Cryptoscope links operation to key material; SATAM records rationale. C: occurrences without the *reason*; none links the use site to the key-source site. D: each recommendation carries the contributing sites (use, key source, sink) and the evidence tier. E: "Nice UX, not a result." F: evaluate provenance-link precision/recall on the annotated sample; otherwise do not claim it. G: **Keep as output; claim only if measured.**

**5.13 Synthetic benchmark.** A: ground truth with controlled variation; no role-labelled Python PQC benchmark exists. B: PyCryptoBench (misuse rules × language features), CamBench, MASC mutants, de Bonrostro's 800 fragments (category-labelled), Cryben (Ruby/Go), pqcheck `planted/`. C: none carries role labels for RSA/EC sites or provenance variants; de Bonrostro's categories are at fragment level and pyca-only. D: PyPQC-RoleBench: base cases × transformation operators × provenance kinds, with negatives. E: "Synthetic benchmarks are gamed by their authors (Chen et al. NDSS 2024)." F: pair with frozen held-out real repositories; publish the generator; include cases derived from real repositories; have an external annotator validate a sample. G: **Keep; it is a first-class artefact.**

**5.14 Real-world repository evaluation.** A: external validity. B: pqcheck's 16-repo corpus (pinned SHAs, adjudicated sites), Shaw's 5 repos, Mehl's 19-repo reference set, Cryptolation's 943 projects. C: pqcheck fixed misses from its held-out set; Shaw single labeller; Mehl repository-level. D: call-site-level, double-annotated, frozen before rule writing. E: "Too few repositories; authors annotate their own output." F: pqcheck's corpus shows 300–600 adjudicated sites are available in 6–10 repositories; freeze and κ answer the second point. G: **Keep, with the protocol in Section 10.**

**5.15 Baseline comparisons.** A: a claim of improvement needs baselines. B: pqcheck, pqc-audit, PostQuant, pqc-posture, Shaw (regex stage), CBOMkit, Mehl's scanner (Zenodo), Semgrep-only floor. C: heterogeneous inputs and output semantics (dual strings, policy reasons, `cryptoFunctions`). D: a normalisation layer mapping each tool's output to {correct, harmful, undecided, abstained, missed} per annotated site. E: "Unfair comparison; tools were not built to recommend by role." F: that is the point being measured; report undecided separately from harmful; include Mehl's scanner, which is peer-reviewed and public. G: **Keep; seven baselines, pinned.**

**5.16 Robustness and metamorphic testing.** A: role inference must be invariant under semantics-preserving edits. B: MASC (crypto misuse detectors, Java), Statfier, SAFuzzer, TaintCC/EMT (taint, includes Semgrep). C: none applies to role/recommendation invariance; none for Python PQC scanners. D: operators {import alias, wrapper function, method on class, key loaded vs generated, cross-file call, dict-driven selection, test-path placement}; invariance rate per operator for every baseline. E: "MASC already did this." F: MASC's operators and target differ (Java misuse alarms); cite it as the method and show new findings. G: **Keep; strongest supporting result.**

**Does the combination add research value beyond integration?** Only through the measurements it enables: (i) how often role is undeterminable from the call (H1), (ii) how often existing tools therefore emit harmful or undecided targets, (iii) how much provenance-aware inference and abstention change that at stated coverage, (iv) how fragile all of it is under transformations. Without those four numbers the system is integration.

---

## 6. Three-level reviewer cross-examination

| Claim | Q1 Why this? | Q2 This already exists | Q3 But this has this issue → our answer and proof | Status |
|---|---|---|---|---|
| Role inference for Python RSA/EC call sites | Target class depends on role; measurement studies show KE migration advancing while PQ signatures are undeployed, so advice differs by role; the base paper's P1 names protocol roles as the missing link | CycloneDX schema slot; CBOMkit partial; pqc-audit hard-coded usage; PostQuant heuristics; HyBind contracts; AQtive Guard rules (network) | Partial implementations assign role by pattern or library, not by evidence at the site; verified failures: pqcheck EC keygen → SIGNATURE; PostQuant PyCryptodome RSA keygen → digital-signature. Proof: role macro-F1 on double-annotated sites vs each baseline; H1 share | **Partial overlap → Potentially novel** (conditional on H1) |
| Key-provenance-aware inference | Loaded keys are the common production shape | CrySL typestate (Java), Cryptoscope (Java), Cryptolation/CryptoPyt flows (misuse) | No Python PQC tool models loaders; CBOMkit requires in-place keygen. Proof: ablation with/without provenance; per-provenance-kind results | **Partial overlap (technique established) → Potentially novel in application** |
| Measuring recommendation correctness and harmful rate | Nobody knows how wrong current advice is | None found (detection metrics only; de Bonrostro labels categories by hand) | Proof: normalised outcome classes on frozen held-out sites; McNemar vs each baseline | **Potentially novel** |
| Evidence-gated abstention with risk–coverage | Wrong advice is worse than none | Selective prediction (ML), warning triage, ICSE-C 2026 deferral framework | Not applied to PQC recommendations; proof: AURC and coverage at fixed error budgets | **Established method → not novel; novel only as measured trade-off** |
| Role-invariance robustness benchmark | Detectors break on aliases/wrappers (MASC) | MASC, Statfier, SAFuzzer, EMT | Not for roles/recommendations or Python PQC tools. Proof: invariance rate per operator per tool | **Partial overlap → Potentially novel artefact** |
| Role-annotated CBOM | Requirement; interoperability | CBOMkit, pqcheck, pqc-audit, PostQuant | Only correctness of emitted roles/links is evaluable | **Established → not novel** |
| Semgrep rules | Requirement | Baseline in prior work | — | **Not novel** |
| LLM role classifier | Context understanding | Shaw (context labels), Cryptbara, Xia et al., Xiong et al. | Only as a baseline arm | **Established → baseline only** |

---

## 7. Research-gap matrix (revised)

| Existing work | Implemented | Method | Limitation (evidence) | Our difference | Citation |
|---|---|---|---|---|---|
| Mehl ESEM 2026 | Multi-language vulnerable/safe/PQC-ready scanner; 14,508 repos | `ast`/tree-sitter patterns | No roles, no recommendations, repo-level reference set n=19, single annotator | Call-site roles, recommendations, call-site ground truth | ✔ |
| Yuan et al. ASE 2026 | Ecosystem-scale PQC support label | commit history + source + LLM agent | Repo-level binary label | Site-level role | ◐ |
| pqcheck 0.1.0 | AST detection, policy, CBOM, corpus | AST + YAML policy | No method calls; RSA→ML-KEM always; context unevaluated | Role-conditioned policy; abstention; recommendation metrics | ✔ |
| pqc-audit 0.4.1 | AST detection with hard-coded usage; CBOM | AST | Keygen-only; undecided RSA/EC; no loaders; no unknown | Inferred role; loaders; abstain | ✔ |
| PostQuant 0.7.0 | AST+regex; heuristics; CBOM | tree-sitter | Role per library; no cross-function; dual strings | Evidence-based role | ✔ |
| CBOMkit 1.7.0 | pyca inventory with cryptoFunctions | Sonar rule engine | In-place keys only; no verify/encrypt; no PyCryptodome | Provenance; verify/encrypt; PyCryptodome | ✔ |
| Shaw 2026 | regex + LLM + score | regex/LLM | Name mapping; single labeller | Role; double annotation | ✔ |
| Cryptolation / CryptoPyt / Cryptbara | Inter-procedural Python misuse detection | data flow / taint / deps+LLM | Misuse, not role/PQC | Reuse techniques for role | ◐/✔ |
| CodeQL Python models | Algorithm/mode for ops | API graph | No operation kind; no loaders | Role + loaders | ✔ |
| Cryptoscope / Crypsy | Semantic inventories | slicing / rules | Java; Ruby/Go; no migration strategy | Python; recommendation | ✔ |
| de Bonrostro 2026 | LLM migration of fragments | fine-tuning | Category labelled by hand | Automate and evaluate the category step | ✔ |
| MASC / Statfier / EMT | Robustness testing | mutation/metamorphic | Not roles | Role-invariance | ◐ |
| HyBind 2026 | Hybrid structure checks | intraprocedural contracts | Hybrid only | Classical-site roles | ◐ |

---

## 8. Ranked novelty candidates (maximum five)

**N1 — Role-labelled benchmark and measurement of harmful/undecided PQC recommendations in Python scanners.**
1. Problem: nobody knows how often current scanners attach a role-incorrect or undecided target. 2. Closest: pqcheck corpus (detection-level), MASC (misuse alarms), BF-CBOM (CBOM disagreement). 3. Unresolved: no role labels, no recommendation-level metric. 4. Solution: PyPQC-RoleBench (synthetic × operators × provenance) + frozen real-repository sites, double-annotated; outcome normalisation {correct, harmful, undecided, abstained, missed}; run seven pinned baselines. 5. Novelty claim: first call-site-level, role-labelled evaluation of PQC migration recommendations for Python (bounded to the inspected literature). 6. Proof: tables per tool and per provenance kind; McNemar; CIs. 7. Data: ~400 synthetic + ≥300 real sites. 8. Difficulty: medium-low. 9. Publication: workshop/short paper on its own; full paper with N2. 10. Rejection risk: "benchmark paper without a method" — mitigated by N2.

**N2 — Key-provenance-aware role inference with evidence-gated abstention (the analyzer).**
1. Problem: role undeterminable from the call alone. 2. Closest: CBOMkit pyca rules; pqc-audit usage enum; Cryptolation variable inference; CrySL typestate. 3. Unresolved: no Python tool combines receiver provenance, method, arguments and sinks into a role with an abstain outcome. 4. Solution: Modules B–D (Section 9). 5. Claim: reduces harmful recommendations relative to all baselines at a stated coverage; ablations attribute the gain. 6. Proof: role macro-F1, harmful rate, AURC, per-operator invariance. 7. Data: as N1. 8. Difficulty: medium. 9. Publication: with N1. 10. Risk: H1 small → gain small; mitigated by running the pilot first.

**N3 — Role-invariance robustness study of PQC scanners.**
1. Problem: scanners break under aliasing/wrapping/loading. 2. Closest: MASC, Statfier, EMT. 3. Unresolved: not applied to roles or PQC tools. 4. Solution: transformation operators over N1 base cases; invariance rate per tool. 5. Claim: first such study for PQC recommendation tools. 6–7: as N1. 8. Difficulty: low-medium. 9. Publication: part of the main paper or a tool-track paper. 10. Risk: "MASC did it" — answer with new, tool-specific failure taxonomy.

**N4 — LLM-versus-deterministic role adjudication (baseline study).**
1. Problem: whether LLM context reading beats deterministic evidence for roles. 2. Closest: Cryptbara, Xiong et al., Shaw, Xia et al. 3. Unresolved: not for roles. 4. Solution: pinned model, Xia-style validation, LLM-on-abstained-only hybrid. 5. Claim: comparative evidence only. 6. Proof: same metrics plus cost and run-to-run agreement. 8. Difficulty: low-medium; budget needed. 9. Publication: section of the main paper. 10. Risk: non-reproducibility; mitigated by pinning and releasing prompts/outputs.

**N5 — Role-correct CBOM link-correctness evaluation.**
1. Problem: emitted `cryptoFunctions`/occurrence links are never checked. 2. Closest: BF-CBOM, CBOMkit, pqc-audit. 3. Unresolved: correctness adjudication. 4. Solution: adjudicate asset→occurrence→role links on a sample; cross-tool comparison. 5. Claim: measured link correctness. 8. Difficulty: low. 9. Publication: secondary result. 10. Risk: seen as engineering.

Ranking by evidence × value × feasibility × differentiation: N1 > N2 > N3 > N4 > N5. N1 and N2 together form the paper; N3 is the strongest supporting result; N4 and N5 are optional.

---

## 9. Revised problem statement, questions, objectives and architecture

**Revised problem statement.** Existing Python PQC scanners attach ML-KEM or ML-DSA targets to RSA/ECC findings by algorithm name or by hard-coded pattern usage, so a call site's recommendation can be role-incorrect or undecided, and no study has measured how often this happens. We ask how often the cryptographic role of RSA/EC call sites in Python is undeterminable from the call alone, how often current tools consequently issue harmful or undecided recommendations, and whether key-provenance-aware role inference with evidence-gated abstention reduces harmful recommendations at an acceptable coverage.

**Research questions.**
- RQ1 (prevalence): what fraction of RSA/EC/DH call sites in real Python repositories have a role that cannot be determined from algorithm and method name alone, and which evidence resolves it?
- RQ2 (harm today): per existing scanner, what fractions of annotated sites receive correct, harmful, undecided, abstained and missed recommendations?
- RQ3 (improvement): does role inference with provenance reduce harmful recommendations relative to each baseline at equal coverage, and which evidence sources account for the gain?
- RQ4 (robustness): are role and recommendation invariant under semantics-preserving transformations, per tool and operator?
- RQ5 (optional): does an LLM adjudicator, alone or on abstained sites only, change RQ3 outcomes, at what cost and variance?

**Objectives.** O1 freeze role taxonomy, target-class table and labelling guide; O2 build PyPQC-RoleBench and the frozen real-site set with double annotation; O3 implement Modules A–E; O4 normalise and run seven baselines; O5 report RQ1–RQ4 with CIs and release everything.

**Revised architecture.**
Module A — Semgrep CE rules (pinned) emit candidate sites (requirement; also the floor baseline).
Module B — Python semantic layer: `ast` + `symtable` def-use chains; import/alias resolution; one-level wrapper unwrapping; PyCG call edges for cross-function reachability; provenance resolver {generated, loaded-PEM/DER, loaded-JWK, parameter, attribute, env/KMS, unknown}; argument resolver (padding, hash, curve, key size by constant propagation); scope attribution (app/test/vendored).
Module C — Role classifier: deterministic decision table over evidence (method, padding, key type, provenance, sinks such as JWT `alg`/SSL contexts); outputs role + evidence tier T0–T3 + contributing sites.
Module D — Policy engine: a-priori table role → target class {ML-DSA family; ML-KEM-based key-establishment redesign; KEM+AEAD design review (PK_ENCRYPT, "not a drop-in"); protocol/library migration; inventory-only}; abstain below tier threshold; threshold is a study parameter.
Module E — Outputs: CycloneDX 1.6 CBOM (`cryptoFunctions`, occurrences, properties for tier/role/recommendation/abstention), SARIF.
Module F — Evaluation harness: benchmark generator, baseline adapters and output normaliser, metrics, risk–coverage plots, statistics.

---

## 10. Experimental methodology (attacked and repaired)

- **Sample size.** 60 base × ~7 operators ≈ 400 synthetic cases suffice to expose systematic operator failures (binary invariance per operator with n ≈ 60 gives Wilson 95% CI half-width ≈ 0.12) but not to estimate real-world rates. Real sites: pqcheck's corpus shows 301 adjudicated sites in 6 repos and 584 in 10, so ≥ 300 double-annotated real sites from 8–12 repositories is attainable. For paired tool comparisons on the same sites use McNemar's test; detecting a harmful-rate drop from 0.30 to 0.15 with power 0.8 at α = 0.05 needs roughly 120 discordant-capable sites, within reach.
- **Synthetic bias.** Seed base cases from real-repository idioms; release the generator; have an external annotator validate a 20% sample; report synthetic and real results separately and never pool them.
- **Enough RSA/EC in real repos?** Yes (above), provided repositories are crypto-dense (PyJWT, python-jose, authlib, paramiko, Lemur, google-auth, sigstore-python, josepy/certbot, pyOpenSSL users, asyncssh).
- **Annotators.** Two is the minimum; at least one outside the build team; report Cohen's κ (target ≥ 0.7); adjudicate disagreements by a third person; publish the guide and all labels. Three annotators on a 100-site subset would strengthen it.
- **Leakage.** Split repositories into development (rules may be tuned) and held-out (frozen commit hashes and site list committed before Module C is written; no fixes from held-out misses, which pqcheck admits doing).
- **Held-out selection.** Stratify by library (pyca/PyCryptodome), domain (JOSE, SSH, PKI, generic), and size; exclude repositories used by any baseline for tuning (pqcheck's corpus list).
- **Baseline fairness.** Restrict all tools to the same Python files; map each tool's output to the five outcome classes via published adapters; count dual targets as undecided, not harmful; report each tool's intended scope.
- **Ground truth independence.** Annotate from source, not from any tool's output; candidate sites come from a union of all tools plus a regex over-approximation to limit miss bias.
- **Objective correctness.** Fix the role → target-class table before experiments; a recommendation is correct iff its class equals the table entry for the annotated role; harmful iff its class cannot serve that role (KEM for SIGN/VERIFY; signature scheme for KEY_ESTABLISHMENT or PK_ENCRYPT; drop-in KEM for PK_ENCRYPT); undecided iff multiple classes; abstained; missed.
- **Abstention honesty.** Report risk–coverage curves and area under them; compare at fixed coverages (70/80/90%); report abstention rate by provenance kind.
- **Statistics.** Wilson intervals for rates; bootstrap CIs for AURC; McNemar for paired tool comparisons; Holm correction across baselines; κ for labels.
- **Ablation.** Mandatory: pattern-only → +alias → +wrapper → +provenance → +sinks → +abstention.
- **Reproducibility.** Docker image with pinned Semgrep, PyCG, baseline commits; released benchmark, labels, adapters, scripts, prompts.

---

## 11. Feasibility and implementation plan (no coding yet)

| Component | Status | Notes |
|---|---|---|
| Semgrep CE rules | essential | CE suffices for candidates; do not depend on Pro cross-file |
| `ast`/`symtable` semantic layer | essential | custom but bounded; the main engineering risk |
| PyCG | optional | Apache-2.0; last substantive releases 2021–22; adequate for reachability; fall back to intra-module resolution if it fails on a repo |
| Custom data flow | essential, bounded | def-use within function + one call level; no general taint engine |
| LLM | optional | baseline arm only; pinned model id |
| Two libraries | sufficient | pyca/cryptography + PyCryptodome cover the catalogues of all inspected tools; add python-rsa/ecdsa only if the pilot shows need |
| RSA + EC (+ DH/X25519 keygen) | sufficient | covers SIGN/VERIFY/KE/PK_ENCRYPT roles |
| CycloneDX via cyclonedx-python-lib | essential | schema-validate in CI |
| Baseline containers | essential | pqcheck 0.1.0, pqc-audit 0.4.1, PostQuant 0.7.0, pqc-posture 0.4.0, Shaw regex stage, CBOMkit 1.7.0 via Docker, Mehl's Zenodo scanner |

Plan: week 1–2 taxonomy, table, guide, H1 pilot (30 sites, two repos); week 3–5 benchmark generator and Module A; week 6–9 Modules B–D; week 10–11 baselines and normaliser; week 12–14 annotation and runs; week 15–16 analysis and writing. Minimum viable research contribution: N1 with the Semgrep floor and the five scanners, plus N2 without PyCG. Optional: N3 full operator set, N4, N5, one validated RSA-PSS → ML-DSA pattern (P3).

Risks: H1 small (pilot first); annotation cost (budget ~2 min/site × 400 × 2 annotators); PyCG failures on large repos (fallback); baseline drift (pin); LLM budget (optional).

---

## 12. Three independent reviewer reports

**Reviewer 1 (cryptography/PQC).** Problem is real: KEM vs signature confusion is a safety issue and SP 800-227 is explicit that KEMs are not PKE drop-ins. Concerns: the role taxonomy must handle RSA-PKCS1v15 used for both signing and encryption, hybrid constructions, and "verify-only" sites whose migration path differs (certificates/trust anchors); recommendations must not imply ML-KEM replaces RSA encryption without an AEAD redesign. Required revisions: publish the target table with standards citations; treat PROTOCOL_CONFIG separately; include verify-only and certificate cases; do not call anything "quantum-safe" without parameter sets. Rejection rationale if unaddressed: unsafe or vague recommendations. Verdict: accept with revisions.

**Reviewer 2 (program analysis/security).** Technique is bounded reuse of known analyses; the contribution must be empirical. Concerns: Cryptolation and CryptoPyt already resolve Python flows for crypto objects; show why not reuse them; PyCG recall (~70%) will cap interprocedural coverage; abstention may mask analysis weakness; Semgrep CE intraprocedural limits must be acknowledged. Required: ablations attributing gains to each evidence source; invariance study with operators drawn from real refactorings; release of the analyzer and benchmark; comparison against Mehl's public scanner. Rejection rationale if unaddressed: "engineering integration with a lookup table". Verdict: major revision now, acceptable if ablations and robustness results are convincing.

**Reviewer 3 (novelty/methodology).** The strongest claims are N1 and N3; N2 is credible only through N1's measurements. Concerns: author-labelled ground truth; synthetic benchmark bias; small n; cherry-picked baselines; LLM non-reproducibility; base paper is a poster used as motivation only. Required: external annotator with κ; frozen held-out set; pre-registered hypotheses and table; CIs and paired tests; include peer-reviewed baselines (Mehl) and CBOMkit; clear statement that Semgrep, CBOM and abstention are not claimed as novel. Rejection rationale if unaddressed: unverifiable novelty and weak validity. Verdict: conditional accept for a workshop/short paper; full paper only with ≥ 300 real sites and the robustness study.

---

## 13. Final decision

**B — CONDITIONAL GO.** Proceed with N1 + N2 (+ N3), under the conditions in Section 1 and the protocol in Section 10. The current title and base paper remain. The pipeline the lecturer specified remains the skeleton; the research claim moves from "a scanner" to "measured, role-correct recommendation with abstention".

Kill criteria, to be checked at the H1 pilot: if fewer than ~10% of real RSA/EC sites have an undeterminable role from name alone *and* existing tools' harmful + undecided rate on those sites is below ~10%, redesign around N3 (robustness) or abandon the recommendation framing.

---

## 14. Unverified claims and unresolved questions

1. Yuan et al. (ASE 2026): read from abstract only; whether its tool is released and whether its "source analysis" has any call-site semantics is unknown.
2. Cryptbara (ASE 2025): abstract only; library coverage and code availability unknown.
3. HyBind: PDF blocked; library contracts and role handling unverified.
4. Mehl's Zenodo scanner (10.5281/zenodo.19634475): not downloaded or run; alias handling unknown.
5. IBM Quantum Safe Explorer and SandboxAQ AQtive Guard: capabilities at call-site level unverifiable publicly.
6. cdxgen `cbom` Python output fields: not inspected.
7. CodeQL `Concepts.qll` tail (10k chars) not read; the `CryptographicOperation` concept's full predicate set is inferred from framework files.
8. PostQuant: `ast/patterns/index.ts` not read, so how AST and regex patterns combine is unconfirmed.
9. pqc-audit: `tests/` not read; whether any test covers method-call matching is unknown.
10. PyCryptoBench repository content (beyond README) not inspected; case count (1,836) is from the paper.
11. The RFC number for ML-KEM hybrid key exchange in SSH cited in the first report as "RFC 10042" remains unverified.
12. NIST IR 8547 final (Oct 2026) deprecation/disallowance tables not read directly; dates come from secondary reports.
13. Whether Semgrep's registry gained any PQ ruleset after 12 Nov 2026 must be re-checked at submission.
14. The Consensus API key used for the sweep was pasted into chat by the user and should be rotated.

---

## 15. References (new or re-verified in this audit; DOIs/links as resolved)

- Zhang, L. (2026). Toward Quantum-Safe Software Engineering. ICSE-Companion '26, 402–403. https://doi.org/10.1145/3774748.3795653 [PR ✔]
- Mehl, L. (2026). PQC-Readiness of Open-Source Software: An Empirical Study. ESEM 2026, LIPIcs 394, 53:1–53:14. https://doi.org/10.4230/LIPIcs.ESEM.2026.53 ; artefact https://doi.org/10.5281/zenodo.19634475 [PR ✔]
- Yuan, T. et al. (2026). Post-quantum Cryptography in the Wild. ASE 2026. https://doi.org/10.1145/3832783.3837461 [PR ◐]
- Cho, S., Yu, S., Woo, S. (2025). Cryptbara. ASE 2025. https://doi.org/10.1109/ase63991.2025.00133 [PR ◐]
- Ahn, J. et al. (2026). HyBind. IACR ePrint 2026/2347. https://eprint.iacr.org/2026/2347 [pre ◐]
- Mallick, T. et al. (2026). Classifying Implementations of Cryptographic Primitives and Protocols that Use Post-Quantum Algorithms. SACMAT 2026. https://doi.org/10.1145/3750555.3811889 ; arXiv:2503.17830 [PR ✔]
- Lee, E. et al. (2026). Taxonomy-Driven Cryptographic Dependency Inventory. WWW 2026 Companion. https://doi.org/10.1145/3774905.3794696 [PR ◐]
- Campbell, R. (2026). Agentic Cryptographic Debt. Computers 15(9), 625. https://doi.org/10.3390/computers15090625 [PR ◐]
- Christakis, M. et al. (2026). Testing Static Taint Analyzers with Equivalence Modulo Taint. PACMSE. https://doi.org/10.1145/3832231 [PR ◐]
- Zhang, H. et al. (2023). Statfier. ESEC/FSE 2023 [PR ◐]; SAFuzzer, ASE 2026 [PR ◐]
- Xiong, B. et al. (2026). From Hallucination to Precision. CSCWD 2026. https://doi.org/10.1109/cscwd68734.2026.11582031 [PR ◐]
- Näther, C. et al. (2026). Toward a Common Understanding of Cryptographic Agility. IEEE Access. https://doi.org/10.1109/access.2026.3728196 [PR ◐]
- Ye, X., Tan, T. G., Zhou, J. (2024). Towards Discovering Quantum-Threats for Applications Using Open-Source Libraries. LNCS. https://doi.org/10.1007/978-3-031-61486-6_17 [PR ◐]
- Xue, Z. et al. (2026). Actionable Warning Is Not Enough. ICSE-Companion. https://doi.org/10.1145/3744916.3773133 [PR ◐]
- Hu, H. et al. (2025). An Empirical Study of Suppressed Static Analysis Warnings. PACMSE. https://doi.org/10.1145/3715729 [PR ◐]
- Wen, C. et al. (2024). LLM4SA. ACM TKDD. https://doi.org/10.1145/3653718 [PR ◐]; Iranmanesh, M. et al. (2025). ZeroFalse. arXiv [pre ◐]; Gnieciak, D. et al. (2025). IEEE Access [PR ◐]
- Mousavi, Z. et al. (2025). Detecting Misuse of Security APIs: A Systematic Review. ACM CSUR. https://doi.org/10.1145/3735968 [PR ◐]
- Krüger, S. et al. (2019). CrySL. IEEE TSE. https://doi.org/10.1109/tse.2019.2948910 [PR ◐]; Krüger, S. et al. (2017). CogniCrypt. ASE [PR ◐]
- Ami, A. S. et al. (2026). Why Crypto-detectors Fail (MASC). ACM TOPS. https://doi.org/10.1145/3796221 [PR ◐]
- Chen, Y. et al. (2024). Towards Precise Reporting of Cryptographic Misuses. NDSS. https://doi.org/10.14722/ndss.2024.241032 [PR ◐]
- Xia, Y. et al. (2025). Beyond Static Pattern Matching? PACMSE 2. https://doi.org/10.1145/3728875 [PR ◐]
- Frantz, M. et al. (2024). Cryptolation / PyCryptoBench. IEEE TSE 50. https://doi.org/10.1109/tse.2024.3377182 [PR ◐]; repos franceme/cryptolation, cryptolation/PyCryptoBench [repo ✔]
- Guo, X. et al. (2024). CryptoPyt. ACSAC. https://doi.org/10.1109/acsac63791.2024.00088 [PR ◐]
- Moffie, M. et al. (2025). Cryptoscope. arXiv:2503.19531 [pre ✔]
- Näther, C., Hirsch, E. (2026). Hidden Ciphers (Crypsy). LNCS. https://doi.org/10.1007/978-981-92-6837-5_18 [PR ✔ arXiv]
- Bögli, R. et al. (2026). BF-CBOM. ICPC. https://doi.org/10.1145/3794763.3794831 [PR ◐]
- Shaw, A. (2026). Quantum-Safe Code Auditing. arXiv:2604.00560 [pre ✔]; repo AnimeshShaw/quantum-safe-auditor [repo ✔]
- Pallarés de Bonrostro, J. et al. (2026). arXiv:2606.07341; dataset https://doi.org/10.21950/7GK4MJ [pre ✔]
- Rathnasuriya, R. et al. (2026). When to Answer and When to Defer. ICSE-Companion [PR ◐]
- Salis, V. et al. (2021). PyCG. ICSE [PR ◐]; Xiang, D. et al. (2026). InferCG. TOSEM [PR ◐]
- NIST FIPS 203, FIPS 204 (Aug 2024); SP 800-227 (Sep 2025); IR 8547 final (Oct 2026) [std ✔ pages]
- OWASP CycloneDX 1.6 schema, `cryptoFunctions` enum [std ✔]
- Tool repositories (pins in `02_audit_evidence_log.md`): postquantdev/postquant; Rafael-Ryu/pqcheck; rauleteee/pqc-scanner (pqc-audit); Miles0sage/quantum-mcp; AnimeshShaw/quantum-safe-auditor; PQCA(cbomkit)/sonar-cryptography and cbomkit; github/codeql Python frameworks; advanced-security/cbom-action; Pyhroff/pqc-scanner; PQCWorld/pqaudit; rexcoleman/pqc-migration-analyzer; anthonyharrison/cbom4python; PyPI qproof, qorex, crypto-scanner [repo/doc ✔]
