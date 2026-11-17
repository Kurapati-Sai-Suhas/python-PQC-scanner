# Related-work matrix (provisional; updated 18 Nov 2026 after the full-text audit)

**Two separate verification layers:**
- **Bibliographic metadata:** all entries were verified on 17 Nov 2026 (`references.bib`).
- **Content:** verified on 18 Nov 2026 in `related_work_fulltext_audit.md`, with page numbers and, for tools, file:line.

**Content status:**
- **FT** = full text verified;
- **SRC** = pinned source verified;
- **NFT** = NOT FULL-TEXT VERIFIED (metadata only; no content claim may rest on it);
- **(12 Nov)** = source inspection from the earlier novelty audit, not re-checked.

**Novelty status: PROVISIONAL.** The final novelty audit has not been done. Absence claims are scoped to the inspected set (audit Sec. 3).

## 1. PQC migration and readiness

| Work (bib key) | Method | Relevant verified content | Limitation for our RQ | Difference from this project | Status |
|---|---|---|---|---|---|
| Zhang 2026 (`zhang2026qsse`) | Vision paper; QSSE; AQuA pillars P1–P3 | Inventories rarely capture "which protocol roles they implement" (p. 2) | No tool, data or metrics | Operationalises part of P1 | FT |
| Mehl 2026 (`mehl2026esem`; dataset `mehl2026zenodo`) | Static multi-language scanner; vulnerable / quantum-safe / PQC-ready; 14,508 repositories | Does not prescribe migration (p. 3); wrappers not captured (p. 7); repository-level reference set n = 19, P 1.00 / R 0.93, 0.88 (p. 8) | Repository-level labels from documentation; no roles or recommendations | Per-site roles, guidance and labels | FT. Scanner source public on GitHub (D14). |
| Yuan et al. 2026 (`yuan2026pqcwild`) | (title) readiness of open-source ecosystems for PQC | — | — | — | **NFT**: no content claims |
| Mallick et al. 2026 (`mallick2026classifying`) | Runtime-workload classifiers | Classical vs PQ key exchange 98%, signatures 100% (p. 1) | Dynamic, implementation-level | Static source analysis | FT |
| Näther et al. 2024 (`nather2024slr`) | SLR of PQC migration **of IP networks** | Process phases and people roles (p. 1) | Process level | — | FT |
| Hasan et al. 2024 (`hasan2024framework`) | Enterprise migration framework using inventories | (p. 1) | Organisational | Site level | FT |
| Zhang et al. 2023 (`zhang2023db2`), Zhang et al. 2021 (`zhang2021y2k`) | 7E roadmap; Db2 case study; Y2K analogy | (p. 1) | One system | — | FT (2023) / NFT (2021) |
| Rattanavipanon et al. 2025 (`rattanavipanon2025toolchain`) | QED: detects quantum-vulnerable executables | (pp. 1–2) | Binaries | Source level, role | FT |
| Ahmed et al. 2025 (`ahmed2025survey`) | PQC support in nine libraries | (p. 1) | Libraries | — | FT |
| Näther et al. 2026 (`nather2026agility`) | Crypto-agility definitions review | (p. 1) | Conceptual | — | FT |
| Von Nethen et al. 2024 (`vonnethen2024pmmp`); Joseph et al. 2022 (`joseph2022transitioning`); Ott et al. 2019 (`ott2019challenges`); Ye et al. 2024 (`ye2024quantumthreats`) | (titles) process model; organisational transition; research challenges; Python quantum-threat discovery | — | — | — | **NFT**: title-level citation only |

## 2. Cryptographic API detection and misuse

| Work | Verified content | Limitation | Status |
|---|---|---|---|
| Ami et al. 2026, TOPS (`ami2026mutation`); Ami et al. 2022, S&P (`ami2022masc`) | MASC: 107 misuse cases, 19 usage-based mutation operators; detectors show undocumented flaws (TOPS p. 1) | Misuse detectors | FT (TOPS); 2022 version known via TOPS only |
| Chen et al. 2024 (`chen2024precise`) | False positives of misuse detectors on real code; crafted benchmarks lack real-world intricacies (pp. 1–2) | Misuse | FT. Our earlier "benchmark gaming" wording withdrawn. |
| Wickert et al. 2021 (`wickert2021licma`) | 895 Python projects; 52.26% with ≥ 1 misuse (p. 1) | Misuse | FT |
| Xia et al. 2025 (`xia2025beyond`) | LLMs for misuse detection; instability of direct use (p. 2) | Misuse | FT |
| Mousavi et al. 2025 (`mousavi2025misuse`) | Systematic review | Review | FT |
| Moffie et al. 2025 (`moffie2025cryptoscope`) | Slicing-based inventory linking calls, parameters and objects (pp. 3–5); Python in the design (p. 5); **evaluated on 7 Java applications** (p. 6) | No per-site migration target evaluated | FT |
| Näther & Hirsch 2026 (`nather2026hiddenciphers`) | Crypsy: Ruby and Go source rules plus TLS/SSH configuration formats (pp. 9–10); collective "ML-KEM, ML-DSA, or SLH-DSA" statement for 52 candidates (p. 16) | Not Python; no per-site role-conditioned target | FT |
| Salis et al. 2021 (`salis2021pycg`) | Python call graphs (p. 1) | General purpose; not used by pqscan | FT |
| Frantz et al. 2024 (`frantz2024cryptolation`), Guo et al. 2024 (`guo2024cryptopyt`), Cho et al. 2025 (`cho2025cryptbara`), Krüger et al. 2021 (`kruger2021crysl`) | (titles) Python / Java crypto-API misuse detection | — | **NFT**: title-level scope only. These are the closest Python inter-procedural analyses; overlap with our provenance tracing cannot be excluded. |

## 3. Role and provenance in existing PQC tools (pinned source)

| Tool @ commit | Verified behaviour | Status |
|---|---|---|
| pqcheck @ 3e99c74 | RSA → "migrate to ML-KEM-768" (`policy/defaults/br-drex-piloto.yaml:43`); README documents "usage-context blindness" (README.md:141–147) | SRC |
| pqc-audit @ b5ccaac | RSA keygen → "ML-KEM (key establishment) / ML-DSA (signatures)" (`knowledge/code.py:103`, `targets.py:15`); per-rule `Usage` constant | SRC |
| PostQuant @ 4dc61b7 | pyca RSA keygen → asymmetric-encryption, dual text; PyCryptodome `RSA.generate` → digital-signature → ML-DSA (`patterns/python.ts:14–39`): role by library | SRC |
| qsafe @ ff4f6dc | RSA keygen and `PKCS1_OAEP.new` → "RSA Key Exchange" → ML-KEM 768 (`ast_analyzer.py:26–33, 179–180`) | SRC |
| Quantum-Safe Auditor @ 4d69550 (`shaw2026auditing`) | RSA → "ML-KEM / ML-DSA" (paper Table 1, p. 5); LLM context labels; single labeller (p. 7) | FT (paper) |
| CBOMkit / sonar-cryptography 1.7.0 | Captures pyca sign/decrypt/exchange only on in-place generated keys; no verify or encrypt | (12 Nov) |
| Mehl scanner | Source public, not inspected | — |

## 4. Inventory and CBOM

| Work | Status | Use in the draft |
|---|---|---|
| ECMA-424 / CycloneDX 1.6 (`ecma2024ecma424`) | schema used and validated | standard |
| SARIF 2.1.0 (`oasis2023sarif`) | schema used and validated | standard |
| Bögli et al. 2026 (`bogli2026bfcbom`), Yamamuro et al. 2026 (`yamamuro2026sok`), Schmitt et al. 2024 (`schmitt2024inventories`), Lee et al. 2026 (`lee2026taxonomy`) | **NFT** | title-level citation only; content descriptions withdrawn |

## 5. Migration correctness

| Work | Verified content | Status |
|---|---|---|
| Pallarés de Bonrostro et al. 2026 (`pallares2026llm`) | 800 synthetic executable Python pairs; target fixed per category by dataset design; PyCA + liboqs-python (pp. 1, 3, 6–8) | FT |
| Shaw 2026 (`shaw2026auditing`) | Detection-level metrics; recall 100% by construction (p. 8) | FT |
| Mehl 2026 | Readiness detection; does not prescribe migration | FT |

## 6. Abstention

| Work | Verified content | Status |
|---|---|---|
| Rathnasuriya & Yang 2026 (`rathnasuriya2026defer`) | Calibration plus tool-based abstention for code models (p. 1) | FT |
| Chow 1970 (`chow1970reject`) | (title) reject-option trade-off | NFT (classical citation only) |

## 7. Where the contribution may lie (provisional)

1. **C1–C3** (taxonomy, analyser, role-conditioned policy with explicit non-migration classes) and **C4** (pre-registered, coverage-matched protocol) exist as verified artefacts.
2. Within the inspected set (audit Sec. 3), no work combines provenance-based role inference, role-conditioned targets with abstention, and per-site correctness measurement.
3. **C5**, the measurement, does not exist yet.
4. Unverified works (Yuan et al.; CryptoPyt; Cryptbara; Cryptolation; BF-CBOM) must be checked before any submission-time novelty claim.
