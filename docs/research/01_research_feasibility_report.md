# Post-quantum crypto scanner for Python projects
## Research and feasibility report (Phases 1–6)

Prepared 12 November 2026. Every literature search and tool inspection reported here was executed on that date. Tool facts are pinned to the version and date named in the text; they will drift.

Official project title (unchanged): **Post-quantum crypto scanner for Python projects**
Mandatory base paper (unchanged): **Lei Zhang, "Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography Migration", ICSE-Companion '26** (details verified in Section 1)

---

## Verdict in one paragraph

The project is worth doing, but not as "Semgrep rules + CBOM + ML-KEM/ML-DSA suggestions". That triple already exists in at least four public tools (pqcheck, pqc-posture/qsafe, PostQuant, Quantum-Safe Auditor) and in CBOMkit at inventory level, so a reviewer would reject it as integration work. The defensible contribution is narrower and sits exactly inside the base paper's Pillar P1 ("linking cryptographic uses to ... protocol roles"): **infer the cryptographic role of each RSA/ECC call site (sign, verify, key establishment, public-key encryption, key handling only) under realistic Python key provenance (keys loaded from files, passed through functions, wrapped, aliased), map role to a PQC target class, abstain when evidence is insufficient, and measure recommendation correctness and risk–coverage, not just detection precision.** No inspected paper or tool measures recommendation correctness; the two most capable open tools either map by algorithm name (Quantum-Safe Auditor, pqcheck, which itself documents "usage-context blindness" as a limitation) or capture operations only for keys created in-place (CBOMkit's pyca rules, verified in source). The lecturer's four requirements are all retained as the pipeline's skeleton. Feasibility for an undergraduate team is moderate if scope is bounded to two libraries and a fixed set of APIs.

---

## 0. Method, sources and the limits of this review

**What was consulted directly.** The attached PDF (arXiv 2602.05759v2, full text), Crossref metadata for the DOI, the arXiv abstract page, the ICSE 2026 programme page, GitHub READMEs and raw source files (PostQuant, sonar-cryptography/CBOMkit, quantum-safe-auditor, cbom-action), PyPI metadata via its JSON API (qsafe, pqc-posture, pqcheck), NIST CSRC publication pages (FIPS 203, FIPS 204, SP 800-227, IR 8547), the CycloneDX 1.6 JSON schema, Semgrep's own documentation, arXiv full texts of the Quantum-Safe Auditor, quantum-safe-py, Cryptoscope, Crypsy and the LLM-migration paper, 13 Consensus queries and 11 web searches.

**Evidence legend used in every table.**
- ✔ verified at source in this session (full text, source code, schema, publisher metadata)
- ◐ verified from abstract or metadata only
- ○ relayed from the Consensus report you supplied, not re-verified here
- [PR] peer-reviewed venue · [pre] preprint · [std] standard or government document · [doc] vendor documentation or README · [repo] repository inspection

**Limits you must carry into the final report.**
1. The Consensus connector on this account returns three results per query, so Consensus was used for targeted confirmation, not exhaustive retrieval. Your supplied Consensus report covered breadth; I re-verified the items that matter for the novelty claim.
2. The ACM Digital Library blocked automated access. The DOI was verified through Crossref's registry record instead, which is authoritative for DOI metadata.
3. SandboxAQ AQtive Guard rule texts are behind a login; only rule names were readable. IBM Quantum Safe Explorer was not run; only IBM's public pages were read.
4. No tool was executed on code. Every capability statement is from documentation, source, or papers, and is labelled.
5. Several key competitors are preprints or hobby-scale projects (0–1 GitHub stars). That is not a reason to ignore them; it is a reason to pin versions and re-check before submission.

---

## 1. Phase 1 — Base paper investigation

### 1.1 Verified bibliographic identity

| Field | Value | Evidence |
|---|---|---|
| Title | Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography Migration | ✔ PDF, arXiv, Crossref |
| Author | Lei Zhang, University of Maryland, Baltimore County (sole author) | ✔ Crossref affiliation string |
| Venue | *Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering* (ICSE-Companion '26), Posters track, Rio de Janeiro, 12–18 April 2026 | ✔ Crossref event field; ✔ ICSE 2026 programme (Poster Sessions 1 and 4) |
| DOI | 10.1145/3774748.3795653 | ✔ Crossref resolves to this title, author and pages |
| Pages | 402–403 | ✔ Crossref |
| Publisher date | 12 April 2026 | ✔ Crossref |
| arXiv | 2602.05759; v1 5 Feb 2026, v2 7 May 2026; cs.SE (primary), cs.CR; CC BY-NC-ND 4.0; "2 pages, 1 figure, accepted by ICSE'26 Poster Track" | ✔ arXiv abstract page |
| Funding | NSF Grant No. 2347249 | ✔ PDF |

The "May 2026" on your PDF is the arXiv v2 revision date, not a second publication. The lecturer's short label "Quantum-Safe Software Engineering (PQC migration)" matches this paper and no other paper with that title was found. Cite the ACM record as the base reference and the arXiv identifier as the open-access copy. One sentence of confirmation from the lecturer, quoting the DOI, closes this question permanently.

### 1.2 Structured analysis

**1. Research problem and motivation.** PQC migration is framed as a software-evolution problem, not a library swap. The paper's own example: a refactoring engine could replace an RSA call with ML-DSA correctly at the API level and still break latency, bandwidth and storage assumptions (larger keys and signatures), miss new error handling for probabilistic failure, and alter timing behaviour relevant to side channels. Organisations report being blocked by "the lack of scalable tools for cryptographic discovery, code-level refactoring, and PQC-tailored verification".

**2. Objectives and research questions.** The paper has no numbered RQs. Its objective is to define Quantum-Safe Software Engineering (QSSE) as a subarea "on top of existing PQC migration roadmaps and CBOM standards" and to propose a research agenda. Implicit questions: how to discover cryptography with code-level semantics (G1), how to systematise and automate PQC-aware refactoring (G2), how to verify migrated systems continuously (G3).

**3. Methodology and architecture.** The AQuA framework (Figure 1): legacy codebase → P1 PQC-aware detection (static and dynamic analysis, ML-assisted scanning) producing an enriched CBOM → P2 semantic crypto-refactoring (architectural patterns, hybrid code generation) producing refactored code → P3 hybrid correctness verification (side-channel analysis, differential testing) producing verified quantum-safe software. It is a conceptual pipeline; no component is implemented.

**4. Techniques, algorithms, tools, frameworks.** Named only as categories: static and dynamic analysis, machine learning, call graphs, data-flow slices, protocol roles, transitive dependency tracing, refactoring schemata with preconditions/edits/consequences, metamorphic and differential testing, constant-time analysis, CI/CD integration. ML-DSA is the only PQC algorithm named in an example. CBOM is referenced as an existing standard.

**5. Dataset and experimental setup.** None. The paper contains no implementation, dataset or experiment.

**6. Evaluation metrics and results.** None reported.

**7. Contributions claimed.** (a) Defining QSSE as a distinct research direction; (b) identifying gaps G1–G3 in the current roadmap/CBOM landscape; (c) the AQuA three-pillar agenda; (d) the explicit goal "to spark collaboration on building and evaluating such tools".

**8. Limitations explicitly acknowledged by the author.** The paper calls itself a vision and an "architectural vision for tools"; it states that realising P1 "requires new static and dynamic analyses" and that P2 patterns are something "future tools can apply". It does not claim results.

**9. Limitations reasonably inferred (my assessment, not the author's).**
- Two pages give no operational definition of "protocol role", "enriched CBOM" or "semantic-free inventory", so any extension must define these terms itself.
- G1 is stated against "CBOM-oriented approaches" generally; the paper does not examine specific tools (CBOMkit, Cryptoscope, cdxgen) whose inventories already carry some operation-level information (Section 2.8 shows how much).
- The agenda is language-agnostic; Python's dynamic features (aliasing, duck typing, runtime dispatch) that make P1 hard are not discussed.
- No success criteria or metrics are proposed for any pillar, so "evaluation" is left entirely open.
- The RSA→ML-DSA example presumes the RSA use is a signature; the paper does not discuss that RSA/ECC uses must first be classified by role before any replacement is meaningful. This is the opening the project exploits.

**10. Unexplored research opportunities named or implied.** Enriched CBOMs with call-graph, data-flow and protocol-role links (P1); a catalogue of PQC refactoring patterns and automatic application (P2); differential/metamorphic classical-vs-PQC testing and constant-time checks in CI (P3); ML-assisted scanning; supply-chain transitive dependency tracing.

### 1.3 What the base paper does and does not accomplish

It accomplishes a clear problem framing and a vocabulary (QSSE, AQuA, G1–G3, P1–P3) that reviewers at ICSE accepted. It does not establish that discovery, contextual analysis, CBOM generation or recommendation are new, and it provides no tool, data or numbers. For this project it is the *motivating framework*; every other paper is a *comparator*. The project extends P1 (and touches P3 optionally) and must never be presented as implementing AQuA as a whole.

---

## 2. Phase 2 — Literature review and market investigation

### 2.1 Foundational and migration-framework literature

| Publication | Venue, year | Objective and method | Main finding | Limitation / relevance | Ev. |
|---|---|---|---|---|---|
| Ott, Peikert et al., *Identifying Research Challenges in PQC Migration and Cryptographic Agility*, arXiv:1909.07353 | CCC workshop report, 2019 | Research agenda from a workshop | Calls for automated discovery, dependency tracing, control-flow analysis, verification | Agenda, no tooling; cited by base paper | ✔ (base refs) [pre] |
| Joseph et al., *Transitioning organizations to post-quantum cryptography*, 10.1038/s41586-022-04623-2 | Nature, 2022 | Organisational perspective | Multi-year transition; performance, implementation security, compliance | Not code-level | ○ [PR] |
| Zhang, Miranskyy, Rjaibi, *Quantum Advantage and the Y2K Bug*, 10.1109/ms.2020.2985321 | IEEE Software, 2020 | 7E roadmap | Explicitly includes examining software and designing for agility | Roadmap, not tooling; base author's prior work | ✔ (base refs) [PR] |
| Zhang et al., *Making existing software quantum safe: IBM Db2*, 10.1016/j.infsof.2023.107249 | IST, 2023 | Industrial case study | Kyber/Dilithium migration; revised 7E | Single system; bespoke scripts (as base paper notes) | ✔ (base refs) [PR] |
| Näther et al., *Migrating Software Systems Toward PQC — SLR*, 10.1109/access.2024.3450306 | IEEE Access, 2024 | Systematic review | Four phases (diagnosis, planning, execution, maintenance); inconsistent terminology; implementations "mostly experimental" | Process-level | ✔ abstract [PR] |
| Von Nethen et al., *PMMP*, 10.1145/3655693.3655719 | EICC, 2024 | Migration management process | Risk-based migration management | Process-level; cited by base paper | ✔ (base refs) [PR] |
| Hasan et al., *A Framework for Migrating to PQC: Security Dependency Analysis*, 10.1109/access.2024.3360412 | IEEE Access, 2024 | Graph-theoretic dependency analysis, case studies | Prioritised replacement via dependency graphs | Enterprise level, not call-site level | ✔ abstract [PR] |
| El Bizri et al., *Institutional Approaches to PQC*, IEEE Access 2026 | IEEE Access, 2026 | Comparative survey of NIST/ANSSI/BSI/CRYPTREC/ENISA | Convergence on hybrid adoption, agility, phased migration | Policy level | ✔ abstract [PR] |
| Rameshan & Messmer, *Assessment Framework for Application-Level Cryptographic Agility*, arXiv:2606.13425 | arXiv, 2026 | Seven-dimension agility framework applied to six APIs | No API offers intent-based key creation or policy-driven algorithm selection | Assessment of APIs, not scanning | ✔ abstract [pre] |
| Wanko Naa et al., *Capability-Driven Framework for Prioritizing PQC Migration*, SECRYPT 2026 | SECRYPT, 2026 | Multi-criteria scoring on a real enterprise system | "Trust-establishing mechanisms—such as key exchange and identity-related functions—consistently rank highest" | Architecture level; supports that *role* drives priority | ✔ abstract [PR] |
| Sharma et al., *Dependency-Aware PQC Migration Planning*, ICAISET 2026 | ICAISET, 2026 | Graph optimisation on simulated enterprises | Dependency-aware ordering reduces risk exposure faster | Simulated assets, not code | ✔ abstract [PR] |
| CARAF (Chujiao et al., 2021), Loebenberger et al. 2024, Nzetchuen et al. 2026, Zelenović et al. 2026, Schmitt et al. 2024, Hirsch & Raab 2026 | various | Agility risk, formal migration models, implicit dependencies, governance, inventory criteria, architecture-derived CBOM | Context, provenance, prioritisation are active areas | Not Python call-site level | ○ |

### 2.2 Python cryptographic-API analysis (closest detection competitors)

| Publication | Venue, year | Method | Result | Limitation / relevance | Ev. |
|---|---|---|---|---|---|
| Frantz et al., *Methods and Benchmark for Detecting Cryptographic API Misuses in Python* (Cryptolation), 10.1109/tse.2024.3377182 | IEEE TSE, 2024 | Inter-procedural data flow with variable inference; 59 modules, 18 misuse rules | 100% precision on PyCryptoBench (1,836 cases, 18 rules × 5 language features); compared against Bandit, Semgrep, Dlint on benchmark and 943 real projects | Misuse, not PQC role or recommendation. Benchmark public: github.com/cryptolation/PyCryptoBench (last push Aug 2021), tool at github.com/franceme/cryptolation | ✔ abstract, ✔ repo existence [PR] |
| Guo et al., *CryptoPyt*, 10.1109/acsac63791.2024.00088 | ACSAC, 2024 | Rewritten AST (PCAST) + taint analysis; 21 libraries, 17 rules | F1 0.80 on PyCryptoBench; recall 99.08% on PCAMD; compared with Cryptolation, LICMA, Bandit, Dlint, Semgrep, CodeQL; 7 CVEs | Misuse rules; the two numbers are different settings. Strongest evidence that Python semantics are solvable | ✔ abstract [PR] |
| Wickert et al., *Python Crypto Misuses in the Wild* (LICMA), 10.1145/3475716.3484195 | ESEM, 2021 | Static rules for 5 Python APIs; 895 projects + 51 MicroPython | 52.26% of projects have ≥1 misuse; API design reduces misuse vs Java/C | Application-vs-dependency attribution matters (the 7%-in-application figure is from the supplied report ○) | ✔ abstract [PR] |
| Acar et al., *Comparing the Usability of Cryptographic APIs*, IEEE S&P 2017 | S&P, 2017 | 256 Python developers, 5 libraries | Simplicity helps but is insufficient; 20% believed insecure code secure | Motivates why role is not obvious from call shape | ✔ abstract [PR] |
| Salis et al., *PyCG*, ICSE-C 2021; Xiang et al., *InferCG*, TOSEM 2026; Zhong, *PyPt*, ESEC/FSE 2022 | various | Static Python call graphs | PyCG precision ~99%, recall ~70%; InferCG adds LLM filtering (+13.9% recall) | Reusable infrastructure for cross-function role evidence | ✔ abstracts [PR] |

### 2.3 Semantic inventories and CBOM

| Publication | Venue, year | Method | Result | Limitation / relevance | Ev. |
|---|---|---|---|---|---|
| Moffie et al., *Cryptoscope*, arXiv:2503.19531 | arXiv (IBM Research), 2025 | Control/data-flow slicing links operations to keys, nonces, random sources | 89/97 labelled Java assets fully matched (92%), precision 97%; CamBench 11/15 | **Java only; Python explicitly future work; no CycloneDX export; remediation suggestions "future"**; no public code found | ✔ full text [pre] |
| Näther & Hirsch, *Hidden Ciphers and Where to Find Them* (Crypsy/Crypistry/Cryben), arXiv:2608.04857, accepted ICICS 2026 (LNCS) | LNCS, 2026 | Classification-driven rules, static scanner, CycloneDX 1.7 output | Cryben: P 0.87, R 0.66, F1 0.75 (0.86 excluding counting-model differences); actionable-weakness precision ≈0.3 because weak-hash alerts "mostly fire on non-security digests"; 52 of 370 real assets are PQ migration candidates | **Ruby and Go; "Java, C/C++, and Python, are not yet demonstrated"; "Crypsy does not compute migration strategies"**; artefacts on a view-only OSF link | ✔ full text [PR/pre] |
| Bögli, Spieler, Kehrer, *BF-CBOM*, 10.1145/3794763.3794831 | ICPC 2026 | Containerised orchestration of CBOM generators | "Striking discrepancies between generated CBOMs" | Preliminary; comparison, not correctness | ✔ abstract [PR] |
| Yamamuro et al., *SoK: Automated Cryptography Discovery and Inventory*, ICISSP 2026 | ICISSP, 2026 | Systematisation of ACDI tool roles and sources | Source, binary, specification are complementary sources | Framework, no tool | ✔ abstract [PR] |
| Cofano et al., *SBOM Generation Tools in the Python Ecosystem*, TrustCom 2024 | TrustCom, 2024 | Four CycloneDX SBOM tools on PyPI | Completeness/correctness issues from metadata inconsistency | Schema validity ≠ content correctness, same lesson for CBOM | ✔ abstract [PR] |
| CycloneDX 1.6 specification (bom-1.6.schema.json) | OWASP/ECMA, 2024 | Schema | `cryptoProperties.algorithmProperties.cryptoFunctions` enum = generate, keygen, encrypt, decrypt, digest, tag, keyderive, **sign, verify, encapsulate, decapsulate**, other, unknown; `primitive` enum includes signature, pke, key-agree, kem | The standard already has slots for role; novelty cannot be "adding role to CBOM" | ✔ schema [std] |

### 2.4 PQC recommendation and automated migration

| Publication | Venue, year | Method | Result | Limitation / relevance | Ev. |
|---|---|---|---|---|---|
| Shaw, *Quantum-Safe Code Auditing* (Quantum-Safe Auditor), arXiv:2604.00560 | arXiv, 2026 | 15 regex classes → LLM (Claude) labels production/test/safe + severity + confidence → VQE "threat score" | 5 repos, 5,775 findings, 602 labelled by the first author alone; precision 71.98% (test-code hits excluded; 49.5% if included), recall defined as 100% because "FN structurally zero" | **Replacement is a static per-algorithm table (RSA → "ML-KEM / ML-DSA", undecided); no role classification; no CBOM**; repo github.com/AnimeshShaw/quantum-safe-auditor (1 star, pushed 26 Sep 2026, MIT) | ✔ full text, ✔ repo [pre] |
| Shaw, *quantum-safe: Hybrid-by-Default Python Cryptography Library*, arXiv:2605.17061 v2 | arXiv, Oct 2026 | Library audit of 9 PQC libraries, 9 dimensions; library ships `qs-audit` import scanner and "a CycloneDX CBOM" | 0 of 7 libraries provide discovery/inventory | Scanner limited to imports; CBOM source and version unstated; no per-operation guidance found | ✔ partial full text [pre] |
| Pallarés de Bonrostro, González-Tablas, González Vasco, *Empirical Evaluation of LLMs for Migration of Code Fragments to PQC*, arXiv:2606.07341 | arXiv, 2026 | 800 paired Python fragments (pyca/cryptography → liboqs-python), six families, functional tests; four models | Fine-tuned GPT-4.1-mini 92.5% functional correctness; 6 real repos: python-jose and google-auth failed | **Fragments' categories labelled manually; no detection step; mapping table: signatures → Dilithium5/SPHINCS+, key exchange → Kyber1024.** Dataset public: DOI 10.21950/7GK4MJ. Code not public | ✔ full text [pre] |
| Wahlang et al., *ccPASTpqc*, CODS-COMAD 2025 | CODS-COMAD, 2025 | Code LMs translate vulnerable code | BLEU 0.925 | BLEU is not correctness | ✔ abstract [PR] |
| Strauss et al., *Assessing and Enhancing Quantum Readiness in Mobile Apps*, arXiv:2506.00790 | arXiv, 2025 | 4,018 Android apps, LLM migration trials | Hash changes succeed; PQC upgrades failed | Android/Java | ○ [pre] |
| Rattanavipanon et al., *Toolchain for Migrating Executables* (QED), 10.1109/access.2024.3524309 | IEEE Access, 2024/25 | Binary/API/trace analysis | >90% analyst-workload reduction | Binaries, not Python source | ○ [PR] |
| "PQC Migration Assistant", IRJMETS 2026 | IRJMETS, 2026 | Regex detection, rule-based risk, advisory | Detects RSA/ECC/AES/SHA | Low-tier venue; regex; illustrates the crowded "basic scanner" space | ✔ abstract |
| Nyirongo et al., *API Replacement Refactorings* (AKIRA), PACMSE 2026 | FSE/PACMSE, 2026 | Mining + heuristics for API replacement | 88–90% P/R | General refactoring; shows recommendation evaluation methodology | ✔ abstract [PR] |

### 2.5 Evaluation methodology that the project must follow

| Publication | Why it matters here | Ev. |
|---|---|---|
| Ami et al., *Why Crypto-detectors Fail* / MASC (IEEE S&P 2022; extended in ACM TOPS 2026) | Mutation operators exposed 19 undocumented flaws in 9 detectors. Apply the same idea to *role inference and recommendation invariance* | ✔ abstract [PR] |
| Chen et al., *Towards Precise Reporting of Cryptographic Misuses*, NDSS 2024 | Rule violations are not vulnerabilities; false-alarm patterns from rules, models, implementations. Directly relevant to "RSA found" ≠ "RSA needs ML-KEM" | ✔ abstract [PR] |
| Xia et al., *Beyond Static Pattern Matching?*, FSE 2025 | Direct LLM use yields >50% false positives initially; validation raises recall to ~90%. Any LLM component needs a verifier | ✔ abstract [PR] |
| Masood et al., 2024 (arXiv) / SECRYPT 2025 | GPT-4o-mini beats static tools on CryptoAPI and MASC sets, not on OWASP. LLM baseline is credible but dataset-sensitive | ✔ abstract |
| Firouzi et al., SANER-C 2026 | Semgrep and CodeQL matched human ground truth on only 65% and 61% of samples. Do not use a scanner as its own oracle | ✔ abstract [PR] |
| Rathnasuriya et al., *When to Answer and When to Defer*, ICSE-C 2026; Oehri et al., UniCR 2025 | Selective prediction / risk–coverage framing for code predictions; gives the metric vocabulary for abstention | ✔ abstract [PR/pre] |
| Guo et al., *Mitigating False Positive Static Analysis Warnings*, TSE 2023; Yedida et al., TSE 2023; Tahaei et al., CHI 2021 | Actionability and developer comprehension of security warnings | ✔ abstract [PR] |
| Afrose et al., CryptoAPI-Bench 2019 / TSE 2022; Wickramasinghe et al., IMC 2026 | Benchmark design with true negatives; Internet measurement shows hybrid key exchange converged on X25519MLKEM768 while **no PQ signature deployment** was observed, so key-establishment and signature migrations are at different maturity and must be recommended differently | ○ / ✔ abstract [PR] |

### 2.6 Standards (do not confuse standardisation with invention)

| Document | Status and date | Relevance | Ev. |
|---|---|---|---|
| FIPS 203 ML-KEM; FIPS 204 ML-DSA | Final, 13 Aug 2024 | Target primitives: KEM for key establishment, signature for authentication/integrity | ✔ NIST pages [std] |
| SP 800-227 *Recommendations for Key-Encapsulation Mechanisms* | Final, Sep 2025 | KEM usage and hybrid guidance; a KEM is not a drop-in for RSA encryption | ✔ NIST page [std] |
| NIST IR 8547 *Transition to Post-Quantum Cryptography Standards* | Final, Oct 2026 (NIST page); secondary sources report deprecation after 2030 and disallowance after 2035 for quantum-vulnerable public-key algorithms | Motivation and timeline; verify the exact tables in the document before quoting dates | ✔ page, ◐ content [std] |
| CycloneDX 1.6 (CBOM) | 2024; 1.7 extends CBOM | Output format | ✔ schema [std] |
| RFC on ML-KEM hybrid key exchange in SSH (Kampanakis, Stebila, Hansen) | Listed in the supplied report as RFC 10042 | Protocol-level hybrid construction; **verify the RFC number before citing** | ○ |

### 2.7 Tools and products (market investigation)

| Tool (version, date inspected) | Python RSA/ECC detection | CBOM | PQC recommendation | Context / role | Evaluation published | Ev. |
|---|---|---|---|---|---|---|
| **CBOMkit 2.3.0 + sonar-cryptography 1.7.0** (PQCA/cbomkit, Linux Foundation; Apache-2.0) | Yes, pyca/cryptography only ("100%"); SonarQube plugin with builder-pattern rules over Sonar's Python frontend | CycloneDX 1.6 with `cryptoFunctions`, `primitive`, `parameterSetIdentifier`, padding, `evidence.occurrences` (line) | None. "Quantum-safe" compliance check is an OPA whitelist of algorithm names, described as "proof of concept"; unmatched components default to quantum-safe | Operation captured partially (see 2.8) | None found | ✔ repo, ✔ source [doc/repo] |
| **PostQuant 0.7.0** (4 Mar 2026; TypeScript, tree-sitter; MIT; 0 stars) | Yes: regex + AST for Python/JS; import/alias resolver; local variable resolver; "No cross-function data flow" | Yes (`--format cbom`), CycloneDX version unstated | README says it "tells you what to migrate to", but no mapping found; "Migration playbook engine" is a *planned* roadmap item | Heuristics: nearby identifiers (password, checksum), file paths, test-scope flags; "errs on the side of flagging" | None (anecdotal grades) | ✔ repo [doc/repo] |
| **pqcheck 0.1.0** (PyPI, 13 Jul 2026; Python; CryptoCT) | Yes: AST over `hashlib`, pyca/cryptography (incl. legacy paths), PyCryptodome; Go via go/types + tree-sitter | CycloneDX 1.6 + SARIF 2.1.0; YAML policy engine; confidence demotes displayed severity | Yes, by algorithm: "RSA [banned/critical] → Shor → migrate to ML-KEM-768" regardless of use | README limitation, verbatim: "Usage-context blindness: a symbol match carries no intent. 'RSA verifying a third-party webhook' reads the same as 'RSA encrypting data at rest'"; context-scoped policy rules "parsed but not shipped … until detectors emit context" | Detection-level: 255 HIGH/CRITICAL findings, 0 FP on a 10-repo tuning set; held-out 6 repos recall 0.989, precision 0.99; authors note the held-out set is "no longer strictly untouched" | ✔ PyPI metadata/README [doc] |
| **pqc-posture 0.4.0 / qsafe 1.2.0** (same project, 25–26 Mar 2026; Python; MIT; solo author) | 131 regex patterns, 18 groups; pattern lists separate "Key Exchange: RSA (18 patterns)" from "Signatures: RSA Signature (5 patterns)" | CycloneDX 1.6 + SARIF | Yes, per pattern (e.g. "ECDSA → ML-DSA 65") | Test-vs-production split by path | Only self-reported grades; "FastAPI's zero findings also validate scanner precision" is not an evaluation | ✔ PyPI metadata/README [doc] |
| **Quantum-Safe Auditor** (AnimeshShaw, pushed 26 Sep 2026; MIT; 1 star) | Regex, 12 languages incl. Python; LLM second pass | No CBOM/CycloneDX | By algorithm name (RSA → ML-KEM/FIPS 203, ECDSA → ML-DSA) | LLM labels production/test/safe + severity | Yes (Section 2.4), single labeller, FN undefined | ✔ repo, ✔ paper [pre/repo] |
| **IBM Quantum Safe Explorer** (commercial) | IBM pages list Java, Python, C/C++, Dart among scanned languages | CBOM (IBM originated the schema) | Remediation handled by sibling products (Advisor, Remediator); locates code for developers | Not documented publicly at call-site level | None public | ◐ vendor pages [doc] |
| **SandboxAQ AQtive Guard** (commercial) | No Python source scanning found; data sources are file/filesystem scanners, Java tracer, network analyser, cloud connectors | CBOM data source exists | Rule set distinguishes "Use of quantum-vulnerable key-establishment scheme" (…-68), "Offered quantum-vulnerable signature algorithms…", "Quantum-vulnerable public-key cryptography operation" | Rule-level role split exists at protocol/network evidence level | Login-gated | ◐ nav only [doc] |
| **cdxgen** (CycloneDX) | `cbom` command for Java and Python (atom-based) | CycloneDX 1.6 | None | Unknown | None found | ◐ README mirror [doc] |
| **GitHub advanced-security/cbom-action** (MIT; 16 stars) | CodeQL-based; language list not stated in README | Output format not stated | None | Unknown | None | ✔ repo [repo] |
| **Semgrep registry** | Weak-RSA-key-size rules exist (Kotlin, Go); **no quantum-vulnerability ruleset found** (search 12 Nov 2026; a vendor blog also states none ships) | No | No | CE is intraprocedural by design; cross-file dataflow for Python is a paid Pro feature | n/a | ✔ docs, ◐ registry [doc] |
| **Cryptoscope** (IBM Research) | Java only; Python future work | Model "consistent with" CBOM, no export | Future work | Links operations to key material (Java) | Yes (Java) | ✔ paper [pre] |
| **Crypsy** | Ruby/Go | CycloneDX 1.7 | "does not compute migration strategies" | Classification of material/artifacts/invocations | Yes | ✔ paper [PR] |
| crypto-scanner (Quantum Shield Labs), qproof, qorex, quantumshield-pqc, pqaudit (npm), foxguard, Mondoo xgrep CBOM, OpenText Fortify PQ rules, Moderne OpenRewrite (Java) | Assorted regex/AST scanners and vendor features surfaced by search | Several claim CycloneDX 1.6 | Several claim "NIST PQC migration guidance" | Not inspected | Not inspected | ◐ search only |

The "Crypto Scanner – TT Security Tools" item in the ChatGPT reply could not be traced; the only "Crypto Scanner" found is a PyPI CLI by Quantum Shield Labs. Treat the ChatGPT attribution as unverified.

### 2.8 Source-level findings that shape the novelty claim

**CBOMkit's pyca/cryptography asymmetric rules (read from `python/src/main/java/com/ibm/plugin/rules/detection/asymmetric/*.java` and `keyagreement/PycaKeyAgreement.java`):**
- RSA: `generate_private_key` (keygen), `sign` with PSS or PKCS1v15 (`SignatureAction.SIGN`), `decrypt` with OAEP or PKCS1v15 (`CipherAction.DECRYPT`). `VERIFY_RSA` is commented out. No public-key `encrypt` rule.
- EC: `generate_private_key`, `derive_private_key`, `sign` (ECDSA), `exchange` under `KeyAgreementContext` (ECDH). No verify.
- DH: parameter and key generation only; no `exchange`. DSA: keygen and sign; no verify. Ed25519/Ed448 and X25519/X448: keygen only; no sign, verify or exchange.
- The sign/decrypt/exchange rules match only receiver objects typed as the result of `generate_private_key`. Keys obtained via `load_pem_private_key`, `load_der_…`, JWK parsing, function parameters or attributes are outside the match.
- No PyCryptodome rules exist; the Python rule set registers only `Pyca*` classes.

Consequence: the one open, rule-engine-based tool that *does* emit `cryptoFunctions` cannot assign a role to the most common production shape (a key loaded from storage and used elsewhere), and cannot see verify or encrypt at all. This is a concrete, source-verified gap, not an inference from abstracts.

**pqcheck** documents role blindness as a known limitation (quoted above) and still emits an operation-independent recommendation. **Quantum-Safe Auditor** leaves RSA's target undecided ("ML-KEM / ML-DSA"). **pqc-posture** splits RSA patterns into "key exchange" and "signature" buckets by regex, which is a role guess from surface syntax with no evaluation. **PostQuant** has not implemented recommendations. **Crypsy** and **Cryptoscope** explicitly leave migration strategy to future work.

---

## 3. Phase 3 — Research-gap identification

### 3.1 Research-gap matrix

| Existing research / tool | Functionality implemented | Methodology | Limitations (evidence) | What this project would contribute differently | Citations |
|---|---|---|---|---|---|
| Base paper (Zhang 2026) | Vision: enriched CBOM with call-graph, data-flow, protocol roles (P1) | Position paper | No implementation, metrics or definitions | Operationalise "protocol role" for Python call sites and measure it | ✔ Sec. 1 |
| Cryptolation (TSE 2024) | Inter-procedural misuse detection, PyCryptoBench | Data flow, variable inference | Misuse rules; no role, no PQC, no recommendation | Reuse its language-feature taxonomy for benchmark design; add role labels | ✔ |
| CryptoPyt (ACSAC 2024) | Taint-based misuse detection, 21 libraries | PCAST + taint | Same as above | Same; shows alias/wrapper handling is feasible in Python | ✔ |
| CBOMkit / sonar-cryptography 1.7.0 | Python inventory with cryptoFunctions, CycloneDX 1.6 | Rule engine on Sonar AST | Roles only for in-place generated keys; no verify/encrypt; no PyCryptodome; no recommendation; whitelist "quantum-safe" check defaults to safe | Role inference under key provenance; recommendation with abstention; recommendation-level evaluation | ✔ source |
| PostQuant 0.7.0 | Alias-aware AST detection, CBOM, context heuristics | tree-sitter + regex | No data flow; recommendations unimplemented; no evaluation | Evidence-based role inference and measured recommendations | ✔ repo |
| pqcheck 0.1.0 | AST detection (pyca, PyCryptodome, hashlib), CycloneDX 1.6, policy, confidence | AST, catalog | Self-declared "usage-context blindness"; name-based recommendation; detection-only metrics | Exactly the missing "context" layer, plus recommendation metrics | ✔ README |
| pqc-posture / qsafe | Regex detection, CBOM, per-pattern recommendation | Regex | No semantics; no evaluation | Semantic role inference and real evaluation | ✔ README |
| Quantum-Safe Auditor | Regex + LLM context + per-algorithm replacement | Regex, LLM, VQE score | Single-labeller evaluation; FN undefined; RSA target undecided; no CBOM | Role-determined target; defined FN via benchmark; CBOM | ✔ paper |
| Cryptoscope | Operation-to-key linking inventory (Java) | Slicing | Java only; no CBOM export; remediation future | Python; recommendation layer | ✔ paper |
| Crypsy | Discovery + weakness assessment, CycloneDX 1.7 | Rule repository | Ruby/Go; "does not compute migration strategies"; actionable precision ≈0.3 | Python; role-aware recommendation | ✔ paper |
| de Bonrostro et al. 2026 | LLM migration of fragments; public dataset | Fine-tuning + functional tests | Categories labelled by hand; no detection | Automate the category (role) step they do manually; reuse their dataset as a labelled source | ✔ paper |
| BF-CBOM (ICPC 2026) | Comparative CBOM analysis | Orchestration | Discrepancies observed, not adjudicated | Correctness-adjudicated comparison on Python | ✔ abstract |
| AQtive Guard | Role-split rules at protocol/network evidence level | Commercial | No Python source evidence; closed | Open, source-level, evaluated | ◐ |
| IBM Quantum Safe Explorer | Multi-language scanning, CBOM | Commercial | No public evaluation; remediation in other products | Open, evaluated | ◐ |
| Semgrep registry | Weak-key rules | Pattern rules | No PQ ruleset; CE is intraprocedural | PQ candidate rules are an implementation step, not a contribution | ✔ docs |

### 3.2 Is "Semgrep + CBOM + PQC recommendations" already established?

Yes, at workflow level. pqcheck, pqc-posture/qsafe, PostQuant and Quantum-Safe Auditor each combine source detection, a CBOM or structured inventory, and some replacement guidance; CBOMkit and cdxgen provide inventory and CBOM. None of them uses Semgrep specifically, and no public Semgrep PQ ruleset was found, but choosing Semgrep as the candidate detector is an engineering decision. **The combination alone is not a publishable novelty and must not be presented as one.**

### 3.3 Candidate research gaps (seven, ranked by evidence strength)

- **RG1 — Role inference under realistic key provenance.** No inspected Python tool assigns sign/verify/key-establishment/encryption roles when the key is loaded, deserialised, passed as a parameter, stored on an object, or reached through an alias or wrapper. CBOMkit's rules prove the gap in code; pqcheck admits it in prose.
- **RG2 — Recommendation correctness has never been measured.** Every published number is detection precision/recall (Shaw, pqcheck, Crypsy) or migrated-code functional correctness given a known category (de Bonrostro). Nobody reports "the recommended PQC class was right for this call site".
- **RG3 — No abstention.** All tools emit a recommendation for every hit. Selective-prediction methodology (risk–coverage) is absent from the PQC-scanner literature.
- **RG4 — No robustness evaluation of PQC scanners or their recommendations.** MASC exists for misuse detectors (Java). Nothing equivalent exists for role/recommendation invariance under aliasing, wrapping, cross-function flow or key loading.
- **RG5 — CBOM role and evidence fields are emitted but never validated.** CycloneDX 1.6 has `cryptoFunctions` and evidence occurrences; BF-CBOM shows generators disagree; nobody adjudicates which is correct at the call-site level.
- **RG6 — Python coverage holes in the only rule-engine open tool** (no PyCryptodome, no verify/encrypt, no DH/X25519 exchange). Engineering-flavoured, but measurable.
- **RG7 — Scope attribution** (application vs vendored dependency vs test) is handled by heuristics (PostQuant, pqc-posture) and studied for misuse (LICMA) but not for PQC recommendations. Crowded; moderate.

---

## 4. Phase 4 — Novelty candidates

Thirteen fields per candidate, as requested. Novelty confidence is relative to the evidence inspected here and the supplied Consensus report; it is not a claim of worldwide first invention.

### C1 — Role-aware PQC recommendation with evidence-gated abstention (recommended main contribution)

1. **Technical idea.** For each detected RSA/ECC/DH call site, infer a *cryptographic role* ∈ {SIGN, VERIFY, KEY_ESTABLISHMENT, PK_ENCRYPT, PK_DECRYPT, KEY_MATERIAL_ONLY (generation/serialisation/format conversion), PROTOCOL_CONFIG (TLS/SSH contexts), UNKNOWN} from a fixed evidence set: the API method and its padding/hash arguments (PSS/PKCS1v15-with-sign vs OAEP), the key object's provenance (generated, loaded from PEM/DER/JWK/env, parameter, attribute), downstream sinks (JWT `alg`, SSL contexts, HTTP signature headers), and intra/inter-procedural flow. A deterministic policy maps role → recommendation class (SIGN/VERIFY → ML-DSA family with size/format impact note; KEY_ESTABLISHMENT → ML-KEM-based redesign, hybrid where a protocol is involved; PK_ENCRYPT/DECRYPT → KEM + AEAD design review, explicitly "not a drop-in"; KEY_MATERIAL_ONLY → inventory only; PROTOCOL_CONFIG → library/protocol upgrade; UNKNOWN → **abstain: "insufficient evidence"**). Each role carries an evidence score; abstention is a threshold on that score.
2. **Problem solved.** ML-KEM and ML-DSA are not interchangeable; name-based mappings produce wrong or undecidable advice (RSA → "ML-KEM / ML-DSA").
3. **Why existing work is insufficient.** Section 2.8: name-based (pqcheck, QSA), regex buckets (pqc-posture), unimplemented (PostQuant), partial operation capture (CBOMkit), out of scope (Crypsy, Cryptoscope).
4. **Closest work.** CBOMkit sonar-cryptography; pqcheck; Quantum-Safe Auditor; Cryptoscope; de Bonrostro et al.
5. **Exact difference.** CBOMkit: roles only for in-place keys, no verify/encrypt, no recommendation, no abstention. pqcheck: no role at all. QSA: LLM context is production/test/safe, not role; mapping by name. Cryptoscope: Java, inventory only. de Bonrostro: role labelled manually, then migrates; we automate and evaluate that labelling step.
6. **Evidence for the gap.** Source inspection of CBOMkit rules; pqcheck README quote; QSA Table 1; Crypsy Sec. 7.2 quote; Cryptoscope conclusion quote; base paper P1 text ("which protocol roles they implement").
7. **Implementation.** Semgrep CE rules (pinned version) emit candidate sites as JSON → Python semantic layer (`ast` + symbol table + def-use chains; PyCG for cross-function reachability; Semgrep intraprocedural taint for intra-function flows) resolves key provenance and arguments → rule-based role classifier with explicit evidence weights → policy engine → CycloneDX 1.6 CBOM via `cyclonedx-python-lib` (schema-validated) with `cryptoFunctions`, `evidence.occurrences`, and `properties` for role evidence, score, recommendation class and abstention reason.
8. **Validation.** Benchmark with independently labelled role ground truth (two annotators, Cohen's κ reported), true negatives, cross-function/alias/wrapper/loaded-key cases; held-out real repositories; compare (a) algorithm-name mapping, (b) CBOMkit `cryptoFunctions` → mapping, (c) pqcheck, (d) PostQuant, (e) QSA regex stage (and its LLM stage if budget allows), (f) ours without abstention, (g) ours with abstention; ablate each evidence source.
9. **Metrics.** Detection P/R/F1; role macro-F1 and confusion matrix; recommendation correctness; *harmful-recommendation rate* (e.g. KEM suggested for a signing site); selective risk vs coverage curve and area under it; abstention rate; per-feature breakdown (alias, wrapper, loaded key, cross-function).
10. **Complexity.** Medium. The semantic layer must stay bounded (two libraries, enumerated APIs, intra-module plus one level of inter-procedural resolution).
11. **Risks and reviewer objections.** "Roles are trivially read from method names" (answer: show the loaded-key/wrapper/verify cases where CBOMkit and name-mapping fail, with numbers); "abstention hides errors" (answer: report coverage with every error figure, and the risk–coverage curve); "benchmark is synthetic" (answer: add held-out real repos with double annotation); "LLM would do this" (answer: include an LLM baseline with Xia-style validation and report cost and variance).
12. **Novelty confidence.** Moderate-to-high. No inspected paper or tool evaluates role-conditioned recommendations with abstention for Python; the search was bounded (Section 0).
13. **Extension of the base paper.** Directly instantiates P1's "protocol roles" link and converts G1 ("we know what cryptography we use" → "we know how to safely transform this code") into a measured capability; the abstention output feeds P2 by marking sites that need human analysis before any refactoring pattern applies.

### C2 — Key-provenance-aware detection (technical core of C1; can be a separate contribution if evaluated independently)

1. **Idea.** Resolve where a key object comes from (generation, `load_pem_*`, `load_der_*`, `serialization`, JWK/JWT libraries, environment/KMS stubs, parameters, class attributes) and propagate the key's algorithm and type to use sites across aliases and one level of calls.
2. **Problem.** Production code rarely generates and uses a key in the same function; CBOMkit's rules only match that shape.
3. **Insufficiency of existing work.** Verified in CBOMkit source; PostQuant has "no cross-function data flow"; pqcheck has "no dataflow analysis"; Cryptolation/CryptoPyt track flows for misuse rules but not key provenance for PQC roles.
4. **Closest work.** Cryptolation; CryptoPyt; CBOMkit; Cryptoscope (Java slicing); PyCG.
5. **Difference.** Target property (key provenance → role) and language (Python) differ from Cryptoscope; purpose differs from Cryptolation/CryptoPyt (misuse).
6. **Evidence.** Section 2.8.
7. **Implementation.** Def-use chains on `ast`, module-level symbol resolution, PyCG call edges, Semgrep taint sources for loaders.
8. **Validation.** Provenance-link accuracy on labelled cases; ablation inside C1.
9. **Metrics.** Provenance accuracy (correct source kind and location), role-F1 delta attributable to provenance.
10. **Complexity.** Medium.
11. **Risks.** Dynamic dispatch, `getattr`, dict lookups remain unresolved → must be counted as abstentions, not ignored.
12. **Confidence.** Moderate (data-flow for Python crypto exists; its use for PQC role is new in the inspected evidence).
13. **Base-paper link.** P1 "dataflow slices" and "call graphs".

### C3 — Recommendation-robustness benchmark (PyPQC-RoleBench) with semantics-preserving transformations

1. **Idea.** A public benchmark of Python RSA/ECC/DH cases with role labels, each instantiated through transformation operators (import aliasing, wrapper function, class method, key loaded vs generated, cross-file call, dictionary-driven algorithm selection, test-vs-production placement, negatives such as hashing-only or format conversion). A scanner's output must be invariant across transformations of the same base case.
2. **Problem.** No benchmark exists for PQC-scanner *recommendations*; PyCryptoBench covers misuse rules.
3. **Insufficiency.** MASC targets Java misuse detectors; PyCryptoBench has no role or PQC labels; de Bonrostro's dataset has category labels but no detection variants or negatives.
4. **Closest work.** MASC; PyCryptoBench; CryptoAPI-Bench; de Bonrostro dataset; Olaiya & Nadkarni 2025 (unnatural misuse).
5. **Difference.** Labels are role and recommendation class; operators target Python idioms; invariance is measured on recommendations, not alarms.
6. **Evidence.** Section 2.5; absence of any such artefact in inspected tools' repositories.
7. **Implementation.** Template cases × operators generated by script; manual review of a sample; all cases executable where possible.
8. **Validation.** Run all baselines; report invariance rate and failure taxonomy.
9. **Metrics.** Mutation-survival (invariance) rate per operator; role-F1 per operator.
10. **Complexity.** Low-to-medium; mostly careful design.
11. **Risks.** "Synthetic" objection; mitigate by seeding templates from real repository patterns and pairing with held-out real repos.
12. **Confidence.** Moderate-to-high for the artefact; methodology itself is established (MASC), so the claim is the artefact and the findings, not the method.
13. **Base-paper link.** P3's call for metamorphic testing, applied to the detection pillar.

### C4 — Evidence-traceable, role-annotated CBOM with provenance-correctness evaluation

1. **Idea.** Emit CycloneDX 1.6 CBOMs where each asset carries `cryptoFunctions` from inferred role, `evidence.occurrences` for every contributing site (use site, key source site), and properties for evidence score, recommendation class and abstention reason; evaluate whether the links are *correct*, not merely schema-valid.
2. **Problem.** CBOMs disagree (BF-CBOM) and are rarely checked for link correctness.
3. **Insufficiency.** CBOMkit emits occurrences but is not evaluated for them; Crypsy evaluates discovery, not links; SATAM (Hirsch & Raab) is architectural.
4. **Closest work.** CBOMkit; Crypsy; BF-CBOM; Cryptoscope; Hirsch & Raab 2026.
5. **Difference.** Link-level correctness metric and abstention/evidence fields.
6. **Evidence.** CycloneDX schema (slots exist); BF-CBOM discrepancy finding.
7. **Implementation.** `cyclonedx-python-lib`, schema validation in CI.
8. **Validation.** Manual adjudication of a sample of asset→occurrence links; cross-tool comparison with CBOMkit and pqcheck outputs on the same repos.
9. **Metrics.** Link precision/recall; schema validity rate; agreement with other generators.
10. **Complexity.** Low.
11. **Risks.** Seen as engineering unless the correctness evaluation is substantive.
12. **Confidence.** Moderate; strongest as a supporting contribution.
13. **Base-paper link.** P1's "enriched CBOM".

### C5 — LLM role classification versus deterministic inference (ablation/supporting study)

1. **Idea.** Compare an LLM asked to label role for each candidate (with Xia-style validation) against the deterministic classifier; test a hybrid where the LLM only adjudicates abstained cases.
2. **Problem.** Unknown whether LLM context understanding beats static evidence for roles.
3. **Insufficiency.** Shaw uses an LLM for production/test/safe, not role; Xia et al. and Masood et al. study misuse, not PQC roles.
4. **Closest work.** Shaw 2026; Xia et al. 2025; Masood et al.; InferCG.
5. **Difference.** Task (role) and evaluation (recommendation correctness, risk–coverage).
6. **Evidence.** Section 2.5.
7. **Implementation.** Prompted model with fixed schema; cache; cost logging.
8. **Validation.** Same benchmark; variance across runs.
9. **Metrics.** As C1 plus cost and run-to-run agreement.
10. **Complexity.** Low-to-medium; needs API budget.
11. **Risks.** Non-reproducibility across model versions; mitigate by pinning model id and releasing prompts/outputs.
12. **Confidence.** Moderate.
13. **Base-paper link.** P1's "ML-assisted scanning".

### C6 — Scope- and dependency-aware recommendation prioritisation

1. **Idea.** Attribute each site to application, vendored dependency, site-packages, or test scope; prioritise recommendations accordingly and report dependency-only exposure separately.
2. **Problem.** Reports mix test fixtures and third-party code with application code (QSA's 188 test findings; PostQuant's test-scope flags).
3. **Insufficiency.** Heuristic path rules only; no evaluation of their effect on recommendation quality.
4. **Closest work.** LICMA; Hasan et al.; PostQuant; pqc-posture.
5. **Difference.** Measured effect on recommendation precision and coverage.
6. **Evidence.** Sections 2.2, 2.7.
7. **Implementation.** Repository layout analysis, pytest/unittest detection, import-origin resolution.
8. **Validation.** Before/after on real repos.
9. **Metrics.** Precision/coverage by scope.
10. **Complexity.** Low.
11. **Risks.** Crowded; incremental.
12. **Confidence.** Low-to-moderate. Include as a feature, not a headline.
13. **Base-paper link.** P1's "transitive dependencies in the software supply chain".

**Considered and deprioritised.** *Bounded migration validation* (one RSA-PSS→ML-DSA pattern with differential tests, base paper P3): valuable but already actively studied (de Bonrostro; Strauss) and expensive; keep as an optional stretch goal for one pattern. *Multi-generator CBOM reconciliation*: replication of BF-CBOM for Python; low novelty, useful as part of C4's evaluation rather than a contribution.

---

## 5. Phase 5 — Red-team review (strict reviewer stance)

| Objection | Honest assessment | Evidence-backed response the paper must contain |
|---|---|---|
| "This system already exists." | Partly true for detection + CBOM + name-based advice (Section 3.2). | Table comparing pinned versions of CBOMkit, pqcheck, PostQuant, pqc-posture, QSA on the same labelled cases; show their role/recommendation outputs. Quote pqcheck's own limitation. |
| "Novelty is just integrating Semgrep, a CBOM library and a lookup table." | True if role inference is shallow. | Role inference must handle loaded keys, aliases, wrappers and cross-function flow, and the ablation must show the name-mapping baseline failing on them. |
| "Role is obvious from the method name (`sign` vs `exchange`)." | Often true for in-place code; false for loaded keys, PKCS1v15 used for both signing and encryption, `verify` absent from CBOMkit, JWT/JOSE wrappers, and format-conversion calls. | Report the fraction of real-repository sites where the method name alone is insufficient or misleading; this number is itself a finding. |
| "Abstention lets the tool look accurate by refusing." | Legitimate. | Never report an error rate without its coverage; publish the risk–coverage curve; compare at equal coverage. |
| "Is this research or engineering?" | Research only if the questions in Section 6.8 are answered with controlled experiments and released artefacts. | Pre-register hypotheses (Section 6.16); release benchmark, labels, scripts, pinned tool versions. |
| "Comparable commercial tools make it redundant." | IBM QSE and AQtive Guard are closed and unevaluated publicly; AQtive Guard's role split is at network/protocol evidence level. | State clearly that no public, evaluated, source-level Python role-aware recommender was found; invite comparison. |
| "Results are not reproducible (LLM components, moving tools)." | Real risk. | Deterministic core; LLM only as a pinned, optional baseline; Docker image with pinned Semgrep, CBOMkit, pqcheck, PostQuant versions. |
| "Ground truth is biased (authors label their own output)." | Shaw's single-labeller protocol is the cautionary example. | Independent double annotation, κ reported, labelling guide published, true negatives included, held-out repos frozen before tuning. |
| "Does it extend the base paper or just cite it?" | It extends P1 specifically. | Map every module to G1/P1 (and the optional validation step to P3); state explicitly what is *not* addressed (P2 refactoring engine, side-channel analysis). |
| "Two libraries and Python-only is too narrow." | It is narrow by design. | Justify with Python's share of cryptographic misuse studies and the migration dataset; declare generalisation as future work. |
| "Recommending 'ML-KEM-based redesign' is not actionable." | A recommendation class is not a patch. | Position the output as the input to P2 patterns and human review; give concrete class definitions and the design-review checklist per class (SP 800-227 for KEM use). |

No candidate was found to be already established in the inspected evidence at the level of *evaluated, role-conditioned recommendation with abstention*. C6 and the two deprioritised ideas were judged too close to existing work to lead.

---

## 6. Phase 6 — Final project recommendation

**1. Research problem statement.** Existing scanners find RSA/ECC in Python code and attach a PQC replacement by algorithm name, which is unsafe because the correct post-quantum target depends on the cryptographic role of the call site, and that role is frequently not determinable from the call alone. We ask whether bounded, evidence-based role inference with explicit abstention produces more correct PQC migration recommendations than name-based mapping, at what coverage cost, and how robust it is to realistic Python code variation.

**2. Motivation.** NIST IR 8547 (final Oct 2026) sets deprecation and disallowance dates for quantum-vulnerable public-key cryptography; FIPS 203/204 define targets with different purposes; measurement studies show key-exchange migration advancing while signature migration has barely begun, so advice must be role-specific; the base paper identifies the absence of code-level semantics (G1) as the first gap.

**3. Base paper summary.** Section 1.

**4. Research gap.** RG1–RG3 (Section 3.3), with RG4–RG5 as supporting gaps.

**5. Main novelty contribution.** C1 with C2 as its mechanism: role-aware PQC migration recommendation for Python RSA/ECC/DH call sites under realistic key provenance, with evidence-gated abstention, evaluated at the recommendation level.

**6. Supporting contributions.** C3 (PyPQC-RoleBench robustness benchmark) and C4 (evidence-traceable, role-annotated CycloneDX 1.6 CBOM with link-correctness evaluation). Optional stretch: one validated migration pattern (RSA-PSS sign → ML-DSA) with differential tests, aligned with P3.

**7. Research objectives.**
- O1: Define a role taxonomy and evidence model for Python asymmetric-crypto call sites in pyca/cryptography and PyCryptodome.
- O2: Implement Semgrep candidate detection plus a bounded semantic layer resolving key provenance and arguments.
- O3: Implement a role→recommendation policy with abstention and CBOM export.
- O4: Build and release a labelled benchmark with transformation operators and a held-out real-world set.
- O5: Quantify recommendation correctness, risk–coverage and robustness against baselines.

**8. Research questions.**
- RQ1: How often is the cryptographic role of an RSA/ECC/DH call site in real Python repositories not determinable from the algorithm name and method name alone, and what evidence resolves it?
- RQ2: Does bounded role inference reduce incorrect and harmful PQC recommendations compared with algorithm-name mapping and with the operation fields emitted by CBOMkit?
- RQ3: What recommendation coverage remains at fixed error budgets when uncertain roles trigger abstention?
- RQ4: Are role inference and recommendations invariant under aliasing, wrapping, key loading and cross-function transformations, and where do they break?
- RQ5 (optional): Does an LLM role classifier, with validation, outperform or complement the deterministic classifier, at what cost and variance?

**9. System architecture.** Python repository → **Module A** Semgrep candidate detection (rules for pyca/cryptography and PyCryptodome asymmetric APIs, loaders, JWT/JOSE wrappers; JSON output) → **Module B** semantic layer (ast/symtable, def-use, alias and import resolution, PyCG edges, Semgrep intraprocedural taint for loaders → uses) → **Module C** role classifier (evidence table → role + score) → **Module D** policy engine (role → recommendation class or abstain; NIST mapping with per-class design notes) → **Module E** CBOM exporter (CycloneDX 1.6, schema-validated, `cryptoFunctions`, occurrences, properties) and SARIF for IDE/CI → **Module F** evaluation harness (benchmark runner, baselines, metrics, risk–coverage plots).

**10. Implementation modules (detail).**
- A: ~25–40 Semgrep rules; each rule tagged with API, library, candidate operation; unit-tested with Semgrep's rule test format.
- B: key-provenance resolver (generated / loaded / parameter / attribute / unknown), argument resolver (padding, hash, curve, key size with constant propagation), alias/wrapper unwrapping (one call level), scope attribution (app/test/vendored).
- C: evidence rules with weights; documented decision table; outputs role, score, contributing sites.
- D: policy YAML (role → class, rationale, standards reference, abstention threshold); configurable.
- E: CBOM builder; validation against `bom-1.6.schema.json`; comparison script for CBOMkit/pqcheck outputs.
- F: dataset generator (templates × operators), annotation guide, metrics (sklearn), plots.

**11. Technology stack.** Python 3.12; Semgrep CE (pin the exact release; CE is intraprocedural by design, cross-file is Pro); `ast`, `symtable`; PyCG (or Scalpel) for call graphs; `cyclonedx-python-lib` for CBOM; `jsonschema`; pytest; optional `liboqs-python` for the stretch validation; Docker for pinned baselines (CBOMkit via its Docker image, pqcheck 0.1.0, PostQuant 0.7.0, pqc-posture 0.4.0, QSA regex stage); optional LLM API with pinned model id.

**12. Experimental methodology.**
- Freeze role taxonomy and labelling guide before building the classifier.
- Build PyPQC-RoleBench: ~60 base cases × 6–8 operators ≈ 400 cases, with ≥25% true negatives (hash-only, symmetric-only, format conversion, PQC already present).
- Select 8–12 real repositories (candidates: PyJWT, python-jose, authlib, paramiko, Netflix Lemur, google-auth, sigstore-python, certbot/josepy, pyOpenSSL-based services); freeze the list and commit hashes before tuning; double-annotate a stratified sample of candidate sites (target ≥300), report κ.
- Run baselines and ablations (pattern-only; +alias; +provenance; +abstention; LLM variant).
- Report per-operator and per-provenance-kind results; publish risk–coverage curves; release everything.

**13. Baseline systems.** (a) Semgrep-only with algorithm-name mapping (the lecturer's literal problem statement, as the floor); (b) CBOMkit 1.7.0 `cryptoFunctions` → mapping; (c) pqcheck 0.1.0; (d) PostQuant 0.7.0 (detection only); (e) pqc-posture 0.4.0; (f) Quantum-Safe Auditor regex stage, and LLM stage if budget allows; (g) ours without abstention.

**14. Dataset and test-case strategy.** Synthetic benchmark seeded from (i) PyCryptoBench's language-feature categories, (ii) de Bonrostro et al.'s public pre-quantum fragments (DOI 10.21950/7GK4MJ; signature and key-exchange families, pyca/cryptography) relabelled by role, (iii) idioms harvested from the real repositories; held-out real repositories as above; MASC-style operators for robustness.

**15. Evaluation metrics.** Detection P/R/F1; role macro-F1 and confusion matrix; recommendation correctness; harmful-recommendation rate; selective risk at fixed coverages (e.g. 70%, 80%, 90%) and area under the risk–coverage curve; abstention rate; provenance-link precision/recall; invariance rate per operator; runtime per kLOC; κ for labels.

**16. Expected results — hypotheses, not achieved results.**
- H1: On real repositories, a material fraction of RSA/EC sites (hypothesised 20–40%) have a role not determinable from algorithm and method name alone (loaded keys, PKCS1v15 ambiguity, wrappers).
- H2: Name-based mapping yields a non-trivial harmful-recommendation rate on those sites; role inference reduces incorrect recommendations substantially (hypothesised ≥50% relative reduction) at equal coverage.
- H3: Abstention lowers residual error further while retaining most coverage (hypothesised ≥75% coverage at a low error budget).
- H4: Pattern-only systems lose role accuracy sharply under wrapper, alias and loaded-key operators; the semantic layer recovers most of it.
- H5 (optional): The LLM classifier is competitive on synthetic cases but less stable on real code; the hybrid (LLM on abstained cases only) improves coverage at bounded cost.
All numbers above are targets to be tested, and the paper must report whichever way they fall.

**17. Limitations (to be stated up front).** Python only; two libraries and an enumerated API set; static analysis only (no runtime dispatch, no C extensions, no binaries); recommendations are migration *classes*, not code changes; protocol-level cryptography (TLS/SSH) is classified, not analysed; benchmark partly synthetic; competitor versions pinned to a date; LLM results tied to a model id.

**18. Publication potential.** Realistic targets: ICSE/FSE co-located workshops on quantum software engineering (Q-SE), ESEM or EASE short/registered-report tracks, SANER/ICPC/MSR tool or data tracks (benchmark + tool), IEEE QCE software track, ARES/ICISSP; a journal version (e.g. IEEE Access, JSS) if the real-world study is substantial. Positioning: "evidence-grounded, role-aware PQC migration recommendations for Python", citing the base paper as the framework and reporting the measured gap between name-based and role-based advice.

### 6.1 Comparison: base paper vs closest research vs existing tools vs proposed system

| Capability | Base paper (Zhang 2026) | Closest research (Cryptolation/CryptoPyt; Cryptoscope; Crypsy; de Bonrostro) | Existing tools (CBOMkit; pqcheck; PostQuant; pqc-posture; QSA) | Proposed system |
|---|---|---|---|---|
| Python RSA/ECC detection | Envisioned (P1) | Yes (misuse-oriented, pyca etc.) / Java / Ruby-Go / assumes given | Yes (pyca only; AST; AST; regex; regex) | Yes: Semgrep + semantic layer, pyca + PyCryptodome |
| Alias/wrapper/cross-function handling | Envisioned (call graphs, slices) | Yes (Cryptolation, CryptoPyt) / Java | Partial (PostQuant alias only; others none) | Yes, bounded, and *measured per operator* |
| Key provenance (loaded vs generated) | Implied by "dataflow slices" | Cryptoscope (Java) | CBOMkit: generated only | Yes, explicit provenance kinds |
| Role classification | Named as "protocol roles" | Not for PQC roles | CBOMkit partial; pqc-posture regex buckets; others none | Yes, with evidence score |
| CBOM | "Enriched CBOM" envisioned | Crypsy 1.7; Cryptoscope none | CBOMkit 1.6 (cryptoFunctions); pqcheck 1.6; PostQuant; pqc-posture 1.6 | 1.6 with role, evidence, score, abstention, link-correctness evaluation |
| PQC recommendation | RSA→ML-DSA example | None ("does not compute migration strategies") | Name-based (pqcheck, QSA), regex (pqc-posture), planned (PostQuant), none (CBOMkit) | Role-conditioned classes with rationale |
| Abstention | — | — | None | Yes, evidence-gated |
| Recommendation-level evaluation | — | None | None (detection metrics only) | Yes: correctness, harmful rate, risk–coverage |
| Robustness benchmark | Metamorphic testing envisioned (P3) | MASC (Java misuse) | None | PyPQC-RoleBench |

### 6.2 Attribution of functionality

| Inherited from the base paper | Integrated from existing technology | Proposed contribution |
|---|---|---|
| Problem framing (QSSE, G1), the goal of CBOMs enriched with call-graph, data-flow and protocol-role links (P1), the idea that detection must feed refactoring and verification (P2, P3) | Semgrep CE as candidate detector; CycloneDX 1.6 schema and `cyclonedx-python-lib`; Python `ast`/symtable; PyCG call graphs; NIST FIPS 203/204, SP 800-227 and IR 8547 as the mapping authority; MASC-style mutation methodology; selective-prediction metrics; PyCryptoBench and the de Bonrostro dataset as seeds | Role taxonomy and evidence model for Python call sites; key-provenance-aware role inference; role→recommendation policy with evidence-gated abstention; recommendation-level and risk–coverage evaluation; PyPQC-RoleBench; link-correctness evaluation of the role-annotated CBOM; measured comparison against pinned CBOMkit, pqcheck, PostQuant, pqc-posture and QSA |

---

## 7. Honest assessment and go / no-go

**Does the project have sufficient research potential?** Yes, conditionally. The condition is that the team commits to the narrow claim (role-correct recommendations with abstention, measured) and resists widening into "a complete AQuA implementation". The strongest single piece of evidence that a gap exists is not an absence in search results; it is that the two most careful open tools either document the blindness (pqcheck) or exhibit it in source (CBOMkit), and the best-evaluated preprint (Shaw) leaves RSA's target undecided.

**Where it could still fail.** (i) If H1 is false and roles are almost always obvious from method names in real repositories, the contribution shrinks to the robustness benchmark; run a 30-site pilot on two real repositories *before* building the semantic layer to test H1 cheaply. (ii) If annotation is done by the same people who tune the classifier, reviewers will discount the numbers; recruit at least one annotator outside the build team. (iii) If tool versions are not pinned, the comparison will be stale by submission.

**Recommended immediate next steps (still no coding of the scanner).**
1. Confirm the base-paper citation with the lecturer using the Crossref record above.
2. Freeze the role taxonomy, recommendation classes and labelling guide (one page each).
3. Run the H1 pilot: manually classify roles for ~30 RSA/EC sites in two repositories (e.g. python-jose, Lemur) and record what evidence was needed; this is also the first benchmark seed.
4. Pin and containerise the five baseline tools; capture their outputs on the pilot sites.
5. Only then start Module A (Semgrep rules), which the lecturer's statement requires anyway.

---

## 8. References

Peer-reviewed [PR], preprint [pre], standard/government [std], documentation/repository [doc]. Items marked ○ are relayed from the supplied Consensus report and were not re-verified in this session.

**Base paper**
- Zhang, L. (2026). Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography Migration. *Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering (ICSE-Companion '26)*, Posters, 402–403. ACM. https://doi.org/10.1145/3774748.3795653 [PR, ✔ Crossref]. Open-access copy: arXiv:2602.05759 (v2, 7 May 2026), https://arxiv.org/abs/2602.05759.

**Detection and Python analysis**
- Frantz, M., Xiao, Y., Pias, T. S., Meng, N., Yao, D. (2024). Methods and Benchmark for Detecting Cryptographic API Misuses in Python. *IEEE TSE* 50, 1118–1129. https://doi.org/10.1109/tse.2024.3377182 [PR]. Benchmark: https://github.com/cryptolation/PyCryptoBench ; tool: https://github.com/franceme/cryptolation [doc].
- Guo, X. et al. (2024). CryptoPyt: Unraveling Python Cryptographic APIs Misuse with Precise Static Taint Analysis. *ACSAC*, 1075–1091. https://doi.org/10.1109/acsac63791.2024.00088 [PR].
- Wickert, A.-K., Baumgärtner, L., Breitfelder, F., Mezini, M. (2021). Python Crypto Misuses in the Wild. *ESEM*. https://doi.org/10.1145/3475716.3484195 [PR].
- Acar, Y. et al. (2017). Comparing the Usability of Cryptographic APIs. *IEEE S&P*. [PR]
- Salis, V. et al. (2021). PyCG: Practical Call Graph Generation in Python. *ICSE*. [PR]; Xiang, D. et al. (2026). InferCG. *ACM TOSEM*. [PR]; Zhong, J. (2022). PyPt. *ESEC/FSE*. [PR]
- Moffie, M. et al. (2025). Cryptoscope: Analyzing cryptographic usages in modern software. arXiv:2503.19531. https://doi.org/10.48550/arxiv.2503.19531 [pre].
- Näther, C., Hirsch, E. (2026). Hidden Ciphers and Where to Find Them. *LNCS* (ICICS 2026). https://doi.org/10.1007/978-981-92-6837-5_18 ; arXiv:2608.04857 [PR/pre].
- Bögli, R., Spieler, J., Kehrer, T. (2026). BF-CBOM. *ICPC*, 463–467. https://doi.org/10.1145/3794763.3794831 [PR].
- Yamamuro, H., Uemura, S., Fukushima, K. (2026). SoK: Challenges for Implementing Automated Cryptography Discovery and Inventory Tool. *ICISSP*, 157–168. https://doi.org/10.5220/0014227100004061 [PR].
- Cofano, S. et al. (2024). SBOM Generation Tools in the Python Ecosystem. *TrustCom*. [PR]

**Recommendation, migration, agility**
- Shaw, A. (2026). Quantum-Safe Code Auditing. arXiv:2604.00560. https://doi.org/10.48550/arxiv.2604.00560 [pre]. Repository: https://github.com/AnimeshShaw/quantum-safe-auditor [doc].
- Shaw, A. (2026). quantum-safe: Bridging the Post-Quantum Production Gap with a Hybrid-by-Default Python Cryptography Library. arXiv:2605.17061 (v2). [pre]. Repository: https://github.com/AnimeshShaw/quantum-safe-py.
- Pallarés de Bonrostro, J., González-Tablas, A. I., González Vasco, M. I. (2026). Empirical Evaluation of LLMs for Migration of Code Fragments to PQC. arXiv:2606.07341 [pre]. Dataset: https://doi.org/10.21950/7GK4MJ.
- Wahlang, R. et al. (2025). ccPASTpqc. *CODS-COMAD*. [PR]
- Strauss, J. et al. (2025). Assessing and Enhancing Quantum Readiness in Mobile Apps. arXiv:2506.00790 [pre] ○.
- Rattanavipanon, N., Suaboot, J., Werapun, W. (2024). A Toolchain for Assisting Migration of Software Executables Towards PQC. *IEEE Access* 13, 4368–4380. https://doi.org/10.1109/access.2024.3524309 [PR] ○.
- Näther, C. et al. (2024). Migrating Software Systems Toward PQC — A Systematic Literature Review. *IEEE Access* 12, 132107–132126. https://doi.org/10.1109/access.2024.3450306 [PR].
- Hasan, K. F. et al. (2024). A Framework for Migrating to PQC: Security Dependency Analysis and Case Studies. *IEEE Access* 12, 23427–23450. https://doi.org/10.1109/access.2024.3360412 [PR].
- Rameshan, N., Messmer, G. (2026). An Assessment Framework for Application-Level Cryptographic Agility. arXiv:2606.13425 [pre].
- El Bizri, M. et al. (2026). Institutional Approaches to PQC. *IEEE Access* [PR].
- Wanko Naa, F. et al. (2026). A Capability-Driven Framework for Prioritizing PQC Migration. *SECRYPT* [PR].
- Sharma, S. et al. (2026). Dependency-Aware PQC Migration Planning. *ICAISET* [PR].
- Zhang, L., Miranskyy, A., Rjaibi, W. (2020). Quantum Advantage and the Y2K Bug. *IEEE Software* 38(2), 80–87. https://doi.org/10.1109/ms.2020.2985321 [PR].
- Zhang, L. et al. (2023). Making existing software quantum safe: IBM Db2. *IST* 161, 107249. https://doi.org/10.1016/j.infsof.2023.107249 [PR].
- Von Nethen, N. et al. (2024). PMMP. *EICC*, 144–154. https://doi.org/10.1145/3655693.3655719 [PR].
- Ott, D., Peikert, C. et al. (2019). Identifying Research Challenges in PQC Migration and Cryptographic Agility. arXiv:1909.07353 [pre].
- Joseph, D. et al. (2022). Transitioning organizations to post-quantum cryptography. *Nature* 605, 237–243. https://doi.org/10.1038/s41586-022-04623-2 [PR] ○.
- Ahmed, N., Zhang, L., Gangopadhyay, A. (2025). A Survey of PQC Support in Cryptographic Libraries. *IEEE QCE*, 906–917. https://doi.org/10.1109/qce65121.2025.00102 [PR].
- Wickramasinghe, N. et al. (2026). Mind the Gap: Policy vs Reality in Post-Quantum TLS Deployment. *ACM IMC* [PR].
- Hirsch, E., Raab, K. M. (2026). Architecture-Derived CBOMs (SATAM). *CCIS*. https://doi.org/10.1007/978-3-032-28946-9_2 [PR] ○; Schmitt, N. et al. (2024). On Criteria and Tooling for Cryptographic Inventories. *GI Sicherheit*. https://doi.org/10.18420/sicherheit2024_003 ○; Loebenberger, D. et al. (2024). arXiv:2408.05997 ○; Nzetchuen, E. et al. (2026). *ACM PQCrypto-based Security*. https://doi.org/10.1145/3839338.3857243 ○; Zelenović, J. et al. (2026). arXiv:2605.16549 ○; CARAF (2021). *J. Cybersecurity* 7. https://doi.org/10.1093/cybsec/tyab013 ○.

**Evaluation methodology**
- Ami, A. S. et al. (2022/2026). Why Crypto-detectors Fail: A Systematic Evaluation of Cryptographic Misuse Detection Techniques (MASC). *IEEE S&P 2022*; extended *ACM TOPS* 2026 (the supplied report lists https://doi.org/10.1145/3796221) [PR]. Demo: *ESEC/FSE* 2023.
- Chen, Y. et al. (2024). Towards Precise Reporting of Cryptographic Misuses. *NDSS*. https://doi.org/10.14722/ndss.2024.241032 [PR].
- Xia, Y. et al. (2025). Beyond Static Pattern Matching? *Proc. ACM Softw. Eng.* 2, 113–136. https://doi.org/10.1145/3728875 [PR].
- Masood, Z. et al. (2024/2025). Beyond Static Tools / Beyond Rules. arXiv; *SECRYPT* [pre/PR].
- Firouzi, E. et al. (2026). Persistent Human Feedback, LLMs, and Static Analyzers. *SANER-C* [PR].
- Rathnasuriya, R. et al. (2026). When to Answer and When to Defer. *ICSE-Companion* [PR]; Oehri, M. et al. (2025). UniCR. arXiv [pre].
- Guo, Z. et al. (2023). Mitigating False Positive Static Analysis Warnings. *IEEE TSE* [PR]; Yedida, R. et al. (2023). *IEEE TSE* [PR]; Tahaei, M. et al. (2021). *CHI* [PR].
- Afrose, S. et al. (2019/2022). CryptoAPI-Bench; Evaluation of Static Vulnerability Detection Tools. *SecDev*; *IEEE TSE* 49, 485–497 ○. Zhang, Y. et al. (2022). Are We There Yet? *IEEE TSE* 49, 288–303 ○. Olaiya, V., Nadkarni, A. (2025). arXiv:2510.13102 ○. Chen, T. Y. et al. (2018). Metamorphic Testing. *ACM CSUR* ○; Segura, S. et al. (2016). *IEEE TSE* ○.

**Standards and specifications**
- NIST (2024). FIPS 203, Module-Lattice-Based Key-Encapsulation Mechanism Standard. https://csrc.nist.gov/pubs/fips/203/final (13 Aug 2024) [std].
- NIST (2024). FIPS 204, Module-Lattice-Based Digital Signature Standard. https://csrc.nist.gov/pubs/fips/204/final (13 Aug 2024) [std].
- NIST (2025). SP 800-227, Recommendations for Key-Encapsulation Mechanisms. https://csrc.nist.gov/pubs/sp/800/227/final (Sep 2025) [std].
- NIST (2026). IR 8547, Transition to Post-Quantum Cryptography Standards. https://csrc.nist.gov/pubs/ir/8547/final (Oct 2026) [std]; verify tables before quoting dates.
- OWASP CycloneDX (2024). Bill of Materials Specification v1.6, `bom-1.6.schema.json` (cryptoProperties, cryptoFunctions enum). https://github.com/CycloneDX/specification [std].
- Kampanakis, P., Stebila, D., Hansen, T. PQ/T Hybrid Key Exchange with ML-KEM in SSH (RFC number as given in the supplied report: 10042; verify) ○.

**Tools and documentation (inspected 12 Nov 2026)**
- PQCA/cbomkit CBOMkit 2.3.0 and sonar-cryptography 1.7.0: https://github.com/PQCA/cbomkit ; https://github.com/PQCA/sonar-cryptography (Python rules under `python/src/main/java/com/ibm/plugin/rules/detection/`) [doc].
- PostQuant 0.7.0: https://github.com/postquantdev/postquant [doc].
- pqcheck 0.1.0: https://pypi.org/project/pqcheck/ ; https://github.com/Rafael-Ryu/pqcheck [doc].
- pqc-posture 0.4.0 / qsafe 1.2.0: https://pypi.org/project/pqc-posture/ ; https://pypi.org/project/qsafe/ ; https://github.com/Miles0sage/quantum-mcp [doc].
- GitHub advanced-security/cbom-action: https://github.com/advanced-security/cbom-action [doc]; GitHub blog, Addressing post-quantum cryptography with CodeQL (Dec 2023).
- CycloneDX cdxgen (`cbom` command): https://github.com/CycloneDX/cdxgen [doc].
- Semgrep documentation: Supported languages; Perform cross-file analysis (CE is intraprocedural; Python cross-file dataflow is a Pro feature). https://docs.semgrep.dev/ [doc].
- SandboxAQ AQtive Guard rules reference (login-gated): https://docs.aqtiveguard.com/cryptography-rules-reference/ [doc].
- IBM Quantum Safe Explorer product pages and IBM blog "IBM as client zero" [doc].
