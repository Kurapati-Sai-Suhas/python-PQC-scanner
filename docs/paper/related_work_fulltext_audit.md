# Related-work full-text audit (18 Nov 2026)

**Purpose.** Replace metadata-level confidence with content-level evidence for every related-work claim that supports the research gap, the novelty argument or the baseline description.

**Method:**
- **Full texts.** Retrieved only from legitimate open sources: arXiv (author versions), the publisher's open-access PDF (Dagstuhl LIPIcs, NDSS), and ACM open-access copies mirrored on arXiv. Text was extracted locally and searched with page tracking. Page numbers are PDF page numbers of the copy read, which can differ from the published pagination.
- **Not accessed.** Pages behind bot verification (ACM Digital Library) or a CAPTCHA (SciTePress) were not accessed. No access control was bypassed.
- **Tools.** Tool claims were re-checked against the **pinned source checkouts** in `.cache/baselines/` (commits in `benchmark/baselines_manifest.json`) by read-only search. Nothing was executed.

**Three kinds of evidence are kept apart:**
1. what the **paper or documentation claims**;
2. what the **pinned source implements**;
3. what **our own comparative experiment** has shown. **Our experiment has shown nothing comparative yet:** no labelled evaluation exists. The pilot is circular, and the DV runs are execution-level only.

**Status values:**
- **FULL TEXT VERIFIED**: the claim was checked in the full text at the cited location.
- **SOURCE VERIFIED**: the claim was checked in the pinned code.
- **NOT FULL-TEXT VERIFIED**: no full text was accessible. Only bibliographic metadata is confirmed, and no content claim may rest on it.

## 1. Papers

| Reference | Full text accessed? | Source | Pages/sections inspected | Verified contribution | Actual limitation | Effect on our novelty claim |
|---|---|---|---|---|---|---|
| `zhang2026qsse` (base paper) | **Yes** | arXiv 2602.05759 | p. 1 (motivation; gaps G1–G3), p. 2 (P1 text) | Vision: QSSE; inventories "rarely capture … which protocol roles they implement" (p. 2) | No tool, data or metrics | Unchanged. Supports the motivation; we operationalise part of P1. |
| `mehl2026esem` | **Yes** | Dagstuhl LIPIcs PDF (publisher OA) | p. 3 (Sec. 2.1, contributions), p. 5 (Sec. 3.3), p. 7 (Secs. 3.8–3.9), pp. 7–8 (Sec. 4, Table 1) | Multi-language static scanner (Python: 11 libraries, 14 call patterns, p. 5); 14,508 repositories; vulnerable / quantum-safe / PQC-ready | "Measures where source code still relies on quantum-vulnerable public-key primitives rather than prescribing how to migrate" (p. 3). Custom wrappers "not captured" (p. 7). Reference set n = 19 at **repository level**, labelled from README/official docs, "not a line-by-line audit"; P = 1.00, R = 0.93 / 0.88 (p. 8). Multiple independent annotators left to future work (p. 8). | Supports the gap claim **for this paper**: no per-site roles or recommendations. **Correction:** our documents said the artefact has "results only, no scanner source". The Zenodo record (all 4 versions) indeed holds only outputs, but its description links the scanner source at github.com/Lxkasmehl/pqc-scanner (public, MIT; checked via the GitHub API on 18 Nov). The paper itself states the supplement includes the source (p. 1). → owner decision D14. |
| `shaw2026auditing` | **Yes** | arXiv 2604.00560 | p. 1 (abstract), p. 5 (Sec. 4.1, Table 1; Sec. 4.2), p. 7 (Sec. 6.1), p. 8 (Sec. 6.3), p. 10 (Sec. 7) | Regex (15 classes) + LLM enrichment + VQE risk score; 5 repositories; 602 labelled findings; P 71.98%, R 100%, F1 83.71% | Table 1 (p. 5): RSA (all sizes) → "ML-KEM (FIPS 203) / ML-DSA (FIPS 204)"; PKCS#1 v1.5 → "OAEP / ML-KEM". Regex confidence fixed at 0.5; LLM-enriched findings receive an LLM-reported confidence ≥ 0.7 (p. 5). Labels by the first author only (p. 7). False negatives "structurally zero", so recall = 100% by construction (p. 8). | Supports the gap (dual target; no role inference). **Corrected wording:** confidence is not a "tier constant" but 0.5 (regex) or an LLM-reported value. Note: python-jose, one of our development repositories, is in its corpus. |
| `pallares2026llm` | **Yes** | arXiv 2606.07341 | p. 1 (abstract), p. 3 (C1), p. 5 (related work), p. 6 (language choice), pp. 7–8 (categories, targets) | 800 synthetic, executable pre/post-PQC Python pairs; LLM migration evaluated by functional tests | The migration target is fixed per category by the dataset design (e.g. Dilithium for signatures, p. 8). Libraries: PyCA/cryptography and liboqs-python (p. 6). | Supports the gap ("deciding the target per site" is not their task). **Corrections:** "category labelled by hand" → "category fixed by dataset construction"; "pyca only" → "PyCA/cryptography + liboqs-python". |
| `moffie2025cryptoscope` | **Yes** | arXiv 2503.19531 | p. 2 (use cases incl. remediation), pp. 3–5 (slicing pipeline; the type-identification stage differs for Java and Python, p. 5), p. 6 (evaluation set) | Inventory by data/control-flow slicing linking API calls to parameters and objects | Evaluation on **seven Java** applications, with an LLM-assisted reference inventory (p. 6). No per-site migration target is evaluated. | **Correction:** "Java only; Python future work" is too strong. The design mentions Python (p. 5); the *evaluation* is Java only. The gap claim holds for its evaluated scope. |
| `nather2026hiddenciphers` | **Yes** | arXiv 2608.04857 | p. 1 (abstract), p. 3 (related work), pp. 9–10 (rules: Ruby, Go; TLS/SSH configuration formats), p. 13 (benchmark), p. 16 (migration candidates) | Static discovery and assessment (Crypsy); CycloneDX 1.7; F1 0.75 on its benchmark (p. 1) | Source rules for Ruby and Go only (pp. 9–10). Its 52 "post-quantum migration candidates" get a collective statement, "would require replacement with … ML-KEM, ML-DSA, or SLH-DSA" (p. 16), not a per-site role-specific target. | Supports the gap for Python and for per-site targets. **New nuance:** it discovers TLS/SSH *configuration* assets, which is related to our undetected PROTOCOL_CONFIG role (W4). |
| `mallick2026classifying` | **Yes** | arXiv 2503.17830 | p. 1 (abstract) | Classifies classical vs PQ key exchange and signatures from computational workload: 98% / 100% (p. 1) | Dynamic, implementation-level | Unchanged: no overlap with static source analysis |
| `nather2024slr` | **Yes** | arXiv 2404.12854 | p. 1 (abstract) | SLR of migration approaches **for IP networks**: process phases, roles of people, real-world migrations | Process and organisation level | **Correction:** scope is IP-network migration, not software systems in general. No effect on the gap. |
| `hasan2024framework` | **Yes** | arXiv 2307.06520 | p. 1 (abstract) | Enterprise migration framework using organisational inventories; graph-theoretic case studies | Organisational level, not code | Unchanged |
| `zhang2023db2` | **Yes** | arXiv 2110.08661 | p. 1 (abstract) | 7E roadmap (Y2K analogy); IBM Db2 case study | One system | Unchanged |
| `rattanavipanon2025toolchain` | **Yes** | arXiv 2409.07852 | pp. 1–2 (abstract, introduction, contributions) | QED: detection of quantum-vulnerable **executables** (binaries) | Binary level. Its stated output is the set of quantum-vulnerable executables (pp. 1–2); no per-site migration target was found in the inspected pages. | Unchanged; scope differs |
| `ahmed2025survey` | **Yes** | arXiv 2508.16078 | p. 1 (abstract) | PQC support in nine C/C++/Java libraries (documentation-based, early 2025) | Libraries, not applications | Unchanged |
| `nather2026agility` | **Yes** | arXiv 2411.08781 | p. 1 (abstract) | Systematic review of crypto-agility definitions (48 of 84 sources) | Conceptual | Unchanged |
| `wickert2021licma` | **Yes** | arXiv 2109.01109 | p. 1 (abstract) | LICMA: misuse of 5 Python crypto APIs; 895 projects + 51 MicroPython; 52.26% have ≥ 1 misuse | Misuse, not PQC | Unchanged |
| `ami2026mutation` (TOPS) | **Yes** | arXiv 2107.07065 v6 (ACM-format TOPS version, Feb 2026) | p. 1 (abstract) | MASC: 107 misuse cases, 19 usage-based mutation operators, 3 scopes; 14 detectors | Misuse detectors (Java-centred) | Unchanged: method precedent for our invariance operators |
| `ami2022masc` (S&P 2022) | **No** (only its extension read) | — | — | Known only through the extension's p. 1 ("evaluated nine major crypto-detectors … 19 undocumented flaws") | — | Cite the TOPS version for content claims |
| `chen2024precise` | **Yes** | NDSS PDF (OA) | pp. 1–2 | False positives of static misuse detectors on real app code; manually crafted benchmarks (CryptoAPI-Bench, CamBench) "lack the intricacies of real-world applications" (p. 2) | Misuse | **Correction:** our draft said Chen et al. "warned about benchmark gaming". The paper does not say that. It shows that crafted benchmarks miss real-world false positives. Reworded. |
| `xia2025beyond` | **Yes** | ACM OA PDF via arXiv 2407.16576 | p. 2 (abstract) | First systematic study of LLMs for crypto-API misuse detection; instability of direct LLM use | Misuse | Unchanged |
| `mousavi2025misuse` | **Yes** | arXiv 2306.08869 v4 | pp. 1–2 | Systematic review of security-API misuse detection | Review | Unchanged |
| `salis2021pycg` | **Yes** | arXiv 2103.00587 | p. 1 (abstract) | Static inter-procedural call-graph generation for Python | General purpose | Unchanged; pqscan does not use PyCG (verified in code) |
| `rathnasuriya2026defer` | **Yes** | arXiv 2605.19369 | p. 1 (abstract) | Uncertainty estimation, calibration and tool-based abstention for code language models | ML predictions, not static analysis | Unchanged: abstention is established |
| `yuan2026pqcwild` | **No** | ACM DL: bot verification; no preprint found | — | Metadata only (Crossref) | — | **NOT FULL-TEXT VERIFIED.** It is the closest PQC-readiness competitor, so absence claims cannot cover it. All content descriptions removed from the draft except the title-level scope. |
| `bogli2026bfcbom` | **No** | ACM DL bot verification; no preprint found | — | Metadata only | — | NOT FULL-TEXT VERIFIED; the "generators disagree" description withdrawn |
| `lee2026taxonomy` | **No** | ACM DL bot verification | — | Metadata only | — | NOT FULL-TEXT VERIFIED; content description withdrawn |
| `vonnethen2024pmmp` | **No** | ACM DL bot verification | — | Metadata only | — | NOT FULL-TEXT VERIFIED (cited only as a process model, from its title) |
| `yamamuro2026sok` | **No** | SciTePress download behind a CAPTCHA (not bypassed) | — | Metadata only | — | NOT FULL-TEXT VERIFIED |
| `schmitt2024inventories` | **No** | GI Digital Library timed out twice | — | Metadata only | — | NOT FULL-TEXT VERIFIED |
| `frantz2024cryptolation`, `guo2024cryptopyt`, `cho2025cryptbara`, `kruger2021crysl`, `ye2024quantumthreats`, `joseph2022transitioning` | **No** | No open-access copy found (Semantic Scholar, arXiv title search) | — | Metadata only | — | NOT FULL-TEXT VERIFIED. Cryptbara and CryptoPyt are the closest Python inter-procedural analyses; we may describe them only by title-level scope ("Python cryptographic API misuse detection"). |
| `chow1970reject` | **No** | MIT DSpace rate-limited (429) | — | Metadata only | — | NOT FULL-TEXT VERIFIED; cited only as the classical reject-option reference, from its title |
| `ott2019challenges` | Not attempted (low relevance) | — | — | Metadata only | — | Cited only for its title-level topic |

## 2. Pinned baseline tools (source verified, read-only)

| Tool @ pinned commit | What its documentation claims | What the pinned source implements (file:line) | What our experiment has shown |
|---|---|---|---|
| pqcheck @ 3e99c74 | README: "usage-context blindness: a symbol match carries no intent"; context-scoped policy rules "parsed but not shipped" (README.md:141–147); data flow stops at single assignment (README.md:124–128) | Bundled policies map RSA (family asymmetric-encryption) → "migrate to ML-KEM-768" (`src/pqcheck/policy/defaults/br-drex-piloto.yaml:43`; same in `br-bcb-conservative.yaml:45`) | Ran 60/60 on DV (execution only). No correctness result. |
| pqc-audit @ b5ccaac | MCP docstring: "key exchange → ML-KEM, signatures → ML-DSA" (`interfaces/mcp_server.py:45`) | pyca/PyCryptodome RSA keygen → `ML_KEM_DSA` = "ML-KEM (key establishment) / ML-DSA (signatures)" (`knowledge/code.py:103,123`; `knowledge/targets.py:15`); EC keygen → `ML_KEM_ECDH_DSA` (`code.py:105,125`). The role is a per-rule constant (`Usage`). | as above |
| PostQuant @ 4dc61b7 | — | pyca `rsa.generate_private_key` → category `asymmetric-encryption`, migration "ML-KEM … for encryption or ML-DSA … for signatures" (`src/scanner/code/ast/patterns/python.ts:14–25`). PyCryptodome `RSA.generate` → category `digital-signature`, "Migrate to ML-DSA" (`python.ts:28–39`). **Role by library, not by use.** | as above |
| qsafe (quantum-mcp) @ ff4f6dc | — | pyca `rsa.generate_private_key` → "RSA Key Exchange", migration "ML-KEM 768" (`ast_analyzer.py:26–33`); `PKCS1_OAEP.new` → "RSA Key Exchange" (`ast_analyzer.py:179–180`) | as above |
| Quantum-Safe Auditor (regex) @ 4d69550 | Paper Table 1: RSA → "ML-KEM / ML-DSA" (Shaw p. 5) | Not re-inspected at source today; the paper's table is the evidence | as above |
| pqblocks-scan @ 3d1eccf | — | PQC algorithm tables (`models.py:136–174`); role handling not re-inspected today | as above |
| CBOMkit / sonar-cryptography 1.7.0 | — | Not pinned locally (not run, owner decision D4 = A). Claims rest on the 12 Nov source inspection (`docs/research/02_audit_evidence_log.md`) and are **not re-verified today**. | not run |
| Mehl scanner | Paper p. 3: does not prescribe migration | Source public at github.com/Lxkasmehl/pqc-scanner (MIT); **not inspected or run** | not run (protocol: reported separately) → D14 |

## 3. Absence claims, rescoped

**Withdrawn wording:** "no existing system …", "nobody …", "the first …".

**Allowed wording (exact scope):**
> Among the works whose full text we inspected (20 papers, Sec. 1) and the six pinned baseline tools whose source we inspected, none (i) infers a site-level cryptographic role from key provenance and consumers, (ii) conditions the PQC target on that role with an explicit abstain outcome, or (iii) measures per-site recommendation correctness. Several works could not be inspected in full text, notably Yuan et al. (ASE 2026), CryptoPyt, Cryptbara, Cryptolation, BF-CBOM and Lee et al. (WWW 2026), so this statement does not extend to them.

## 4. Effect on the novelty argument

- **More defensible, narrower in certainty.**
  - Supporting evidence is now verified at page or line level for the closest PQC tools and papers.
  - The absence claim is scoped to an explicit inspected set.
  - Four inaccuracies in our own descriptions were corrected: Shaw's confidence, Pallarés's category and libraries, Cryptoscope's language scope, Chen's message.
- **Weaker points:**
  - The closest PQC-readiness competitor (Yuan et al., ASE 2026) and the closest Python inter-procedural analyses (CryptoPyt, Cryptbara) remain unverified. A reviewer could find overlap there.
  - Mehl's scanner source is public, so "not runnable" is no longer an accurate justification for excluding it (D14).
- **Unchanged:** our contribution claims C1–C4 are design and implementation artefacts, and C5 needs the evaluation. Nothing found contradicts the research gap as rescoped.
