# Related-work matrix (provisional)

**Sources:**
- Bibliographic data was verified on 17 Nov 2026 (Crossref, DataCite, NIST PDFs, Ecma, OASIS, JSTOR); see `references.bib`.
- Content claims (method, results, limitations) come from the project's hostile novelty audit (`docs/research/02_hostile_novelty_audit.md`, 12 Nov 2026) and its evidence log. They were **not re-read today**.

**Content level:**
- ✔ = full text or source code inspected on 12 Nov 2026;
- ◐ = abstract or metadata only.

Claims marked ◐ must be re-checked against full text before submission.

**Novelty status: PROVISIONAL.** The final novelty audit (R4-20 sequence) has not been performed. The literature search had known limits: Consensus API top-20 per query; IEEE Xplore and ACM DL not readable by automation; no non-English venues. No "first" claim may be made from this matrix.

## 1. PQC migration and readiness

| Work (bib key) | Method | Relevant contribution | Limitation for our RQ | Difference from this project | Content |
|---|---|---|---|---|---|
| Zhang 2026, ICSE-C poster (`zhang2026qsse`) | Vision paper: Quantum-Safe Software Engineering; AQuA pillars P1 detection, P2 refactoring, P3 verification | Names call-site semantics and "protocol roles" as missing from CBOM-oriented inventories (gap G1) | No definitions, tool, data or metrics | Operationalises part of P1 only: call-site roles, provenance, role-conditioned guidance. P2 and P3 are out of scope. | ✔ |
| Näther et al. 2024, IEEE Access SLR (`nather2024slr`) | Systematic literature review of PQC software migration | Map of migration challenges | Review; no tool | — | ◐ |
| Hasan et al. 2024 (`hasan2024framework`) | Migration framework, security-dependency analysis, case studies | Dependency-centred migration planning | Organisational and system level, not call sites | Site-level role | ◐ |
| Joseph et al. 2022, Nature (`joseph2022transitioning`) | Perspective on organisational PQC transition | Motivation; inventory as the first step | No tooling | — | ◐ |
| Ott et al. 2019 (`ott2019challenges`) | Workshop report on migration and agility challenges | Research agenda | Preprint | — | ◐ |
| Zhang et al. 2023, IST (`zhang2023db2`) | Industrial case study (IBM Db2) | Migration is a software-engineering effort | One system | — | ◐ |
| Rattanavipanon et al. 2025 (`rattanavipanon2025toolchain`) | Toolchain for migrating executables | Binary-level assistance | Binaries, not Python source | Source-level role | ◐ |
| Ahmed et al. 2025, QCE (`ahmed2025survey`) | Survey of PQC support in crypto libraries | Library readiness | Libraries, not application call sites | — | ◐ |
| Von Nethen et al. 2024, EICC (`vonnethen2024pmmp`) | Migration management process (PMMP) | Process model | Process, no analysis | — | ◐ |
| Näther et al. 2026, IEEE Access (`nather2026agility`) | Systematic review of cryptographic agility (48 sources) | Vocabulary | Conceptual | — | ◐ |
| Mehl 2026, ESEM (`mehl2026esem`, dataset `mehl2026zenodo`) | Multi-language scanner (Python `ast`); labels vulnerable / quantum-safe / PQC-ready; 14,508 repositories | Repository-level reference set (n = 19) with precision 1.00, recall 0.93/0.88 | States it does not prescribe migration; no data flow; wrappers not captured; repository-level labels; one annotator | Call-site roles, recommendations, call-site ground truth. Its scanner source is not public, so it is a "not run" baseline. | ✔ |
| Yuan et al. 2026, ASE (`yuan2026pqcwild`) | Ecosystem-scale PQC-support detection (package and repository level, LLM post-verification) | 1.1 M packages; repository-level PQC-support label | Not call sites; no roles | Site-level role and guidance | ◐ |
| Mallick et al. 2026, SACMAT (`mallick2026classifying`) | Runtime-telemetry classifiers: classical vs PQ key exchange and signatures | Treats key exchange vs signature as the primary axis | Dynamic, binaries and protocols | Static, source-level | ✔ |
| Ye et al. 2024, LNCS (`ye2024quantumthreats`) | Keyword-based detection of quantum-vulnerable usage in Python | Early Python quantum-threat discovery | Keyword level; no roles | Role, provenance, abstention | ◐ |

## 2. Cryptographic API detection and misuse (Python and general)

| Work | Method | Relevant contribution | Limitation for our RQ | Difference | Content |
|---|---|---|---|---|---|
| Frantz et al. 2024, TSE (`frantz2024cryptolation`) | Cryptolation: inter-procedural Python misuse detection; PyCryptoBench | Python variable inference across functions | Misuse rules, not PQC role or migration | We reuse the idea of bounded inter-procedural resolution for roles | ◐ paper / ✔ repository |
| Guo et al. 2024, ACSAC (`guo2024cryptopyt`) | CryptoPyt: static taint analysis of Python crypto APIs | Precise Python crypto data flow | Misuse; code not located | Role for migration | ◐ |
| Cho et al. 2025, ASE (`cho2025cryptbara`) | Cryptbara: dependency extraction plus LLM | Inter-procedural crypto-object context in Python | Misuse; LLM-dependent | Deterministic role evidence | ◐ |
| Wickert et al. 2021, ESEM (`wickert2021licma`) | LICMA: Python crypto misuses in the wild | Prevalence of Python misuse | Misuse | — | ◐ |
| Krüger et al. 2021, TSE (`kruger2021crysl`) | CrySL specification language; typestate (Java) | Specifying correct API usage | Java; misuse | Provenance-style evidence for Python roles | ◐ |
| Ami et al. 2022, S&P (`ami2022masc`); Ami et al. 2026, TOPS (`ami2026mutation`) | Mutation-based evaluation of misuse detectors | Detectors break under semantics-preserving changes | Java misuse detectors | Method precedent for our invariance operators (RQ4, Dataset A) | ◐ |
| Chen et al. 2024, NDSS (`chen2024precise`) | Precise misuse reporting | Warns about benchmark gaming | Misuse | Motivates the frozen held-out split | ◐ |
| Xia et al. 2025, PACMSE/ISSTA (`xia2025beyond`) | LLM-based misuse detection | LLM vs static comparison | Misuse | — | ◐ |
| Mousavi et al. 2025, CSUR (`mousavi2025misuse`) | Systematic review of security-API misuse detection | Field overview | Review | — | ◐ |
| Moffie et al. 2025 (`moffie2025cryptoscope`) | Cryptoscope: slicing to key material (Java) | Links operations to key material | Java; no migration strategy | Python; role-conditioned guidance | ✔ |
| Näther & Hirsch 2026, LNCS (`nather2026hiddenciphers`) | Static discovery and assessment of cryptographic assets (Ruby/Go); CBOM 1.7 | Semantic inventory | Not Python; computes no migration strategy | Python; recommendation | ✔ (arXiv) |
| Salis et al. 2021, ICSE (`salis2021pycg`) | PyCG Python call graphs | Call-graph construction | General purpose | pqscan uses its own bounded resolver (depth ≤ 2), not PyCG | ◐ |

## 3. Cryptographic role inference and key provenance

| Work / tool | What it does with role or provenance | Limitation (from the 12 Nov source inspection) | Content |
|---|---|---|---|
| CBOMkit / sonar-cryptography 1.7.0 | Captures pyca `sign`/`decrypt`/`exchange` only when the receiver is the literal result of `generate_private_key` | No verify (commented out), no public-key encrypt, no key loaders, no PyCryptodome | ✔ source |
| pqcheck (`tool_pqcheck`) | Maps families to targets by policy | No method calls; RSA → ML-KEM always; `context` field parsed but not evaluated | ✔ source |
| pqc-audit (`tool_pqcaudit`) | Hard-coded `Usage` per rule | Key-generation rules only; RSA/EC → "ML-KEM / ML-DSA" (undecided); no loaders; no unknown outcome | ✔ source |
| PostQuant (`tool_postquant`) | Nearby-word heuristics; category per library | Role assigned by library, not by use | ✔ source |
| qsafe / pqc-posture (`tool_qsafe`) | Regex buckets → targets | Regex; no data flow | ✔ source |
| Quantum-Safe Auditor (`tool_qsaregex`, `shaw2026auditing`) | Regex plus LLM context labels; RSA → "ML-KEM / ML-DSA" | No role inference; single-labeller evaluation | ✔ paper and source |
| CodeQL Python models | Algorithm and block mode | Operation kind not exposed; no key loaders | ✔ source |
| Lee et al. 2026 (`lee2026taxonomy`) | Taxonomy and inventory schema with role-like categories and triage rules | No tool, no experiments | ◐ |

**Reading (provisional).** No inspected Python-capable tool combines receiver provenance, method, arguments and consumer sinks into a site-level role with an explicit abstain outcome. That is a statement about the inspected set (Sec. 3 of the novelty audit), not about all existing work.

## 4. Crypto inventory and CBOM

| Work | Contribution | Limitation for our RQ | Content |
|---|---|---|---|
| ECMA-424 / CycloneDX 1.6 (`ecma2024ecma424`) | Standard schema with `cryptoProperties` and the `cryptoFunctions` enum | No key-agreement function value; no PSS padding value. pqscan maps these to `other` plus properties. | ✔ schema |
| Bögli et al. 2026, ICPC (`bogli2026bfcbom`) | Comparative CBOM analysis at scale; generators disagree | Inventory consistency, not correctness of migration guidance | ◐ |
| Yamamuro et al. 2026, ICISSP (`yamamuro2026sok`) | SoK of discovery and inventory tools | Survey | ◐ |
| Schmitt et al. 2024, GI Sicherheit (`schmitt2024inventories`) | Criteria and tooling for crypto inventories | Criteria | ○ (relayed; content not re-read) |

CBOM generation, Semgrep detection and abstention are **not** claimed as contributions (novelty audit Secs. 5.1, 5.10, 5.11).

## 5. Migration correctness

| Work | Contribution | Limitation for our RQ | Content |
|---|---|---|---|
| Pallarés de Bonrostro et al. 2026 (`pallares2026llm`) | LLM migration of code fragments to PQC; functional correctness | Migration category labelled by hand; fragment level; pyca only | ✔ |
| Shaw 2026 (`shaw2026auditing`) | Risk scoring with LLM assistance | Detection-level evaluation; confidence values assigned, not estimated | ✔ |
| Mehl 2026; Yuan et al. 2026 | Readiness measurement | Detection or readiness labels; recommendations are not judged | ✔ / ◐ |

**Reading (provisional).** In the inspected literature, published numbers measure detection or readiness, not whether a recommendation is correct for the site's role. This is the gap our evaluation design targets (RQ1–RQ3). **No measurement has been made yet.**

## 6. Abstention and selective recommendation

| Work | Contribution | Relevance | Content |
|---|---|---|---|
| Chow 1970, IEEE T-IT (`chow1970reject`) | Optimal error–reject trade-off | Classical basis of abstention | ✔ metadata |
| Rathnasuriya & Yang 2026, ICSE-C (`rathnasuriya2026defer`) | Answer-or-defer framework for code predictions | Abstention in SE tooling | ◐ |

Abstention is an established method. Our use of it (evidence-tier gating with coverage-matched comparison) is evaluation discipline, **not** a novelty claim.

## 7. Where the contribution may lie (provisional; final novelty audit pending)

1. An **operational role taxonomy** for Python RSA/EC/Ed/X call sites, with a frozen key-provenance taxonomy and an evidence-tier model (T0–T3). It is implemented and tested.
2. **Role-conditioned migration guidance with explicit non-migration classes**: inventory, protocol review, approved hybrid, abstain. Public-key encryption is treated as a KEM-DEM redesign, citing FIPS 203, FIPS 204, SP 800-227 and IR 8547.
3. A **pre-registered, coverage-matched evaluation design** for recommendation correctness. It covers repository-level matching, a re-matching bootstrap, a coverage-gap guard, a feasibility gate and Holm control. It is calibrated by simulation and differentially verified.
4. **Planned (not yet produced):** a role-labelled real-world benchmark and the measurements of RQ1–RQ4.

Items 1–3 exist now as design and implementation. Item 4 is the empirical contribution, and it does not exist yet.
