# Standards and library verification (Phase 2, 19 Nov 2026)

Purpose: confirm, before the third review and the paper, that every standard and library the project cites is still in the status the project claims. This is a status check, not a fresh section-by-section reading.

**Method.** Each publication's official CSRC page was opened in the app's built-in browser on 19 Nov 2026. The CycloneDX 1.6.1 schema enumerations were compared against the repository's pinned schema. Library APIs were imported from the project's virtual environment. No PDFs were downloaded: section-level content was **not** re-read today. Section citations still rest on the 17 Nov 2026 full-text check in `docs/final/technical_readiness_report.md` and `docs/paper/evidence_register.md`.

## Standards

| Publication | Status on CSRC (19 Nov 2026) | Project claim | Result |
|---|---|---|---|
| NIST IR 8547, *Transition to Post-Quantum Cryptography Standards* | Final, 27 Oct 2026 (initial public draft 12 Nov 2024); DOI 10.6028/NIST.IR.8547 | Final, Oct 2026 | Consistent |
| FIPS 203 (ML-KEM) | Final, 13 Aug 2024; errata planning note dated 17 Nov 2025 | Final, Aug 2024 | Consistent; errata note does not affect parameter sets the policy names |
| FIPS 204 (ML-DSA) | Final, 13 Aug 2024; errata note dated 31 Jul 2026 | Final, Aug 2024 | Consistent; errata contents not re-read |
| FIPS 205 (SLH-DSA) | Final, 13 Aug 2024 | Final, Aug 2024 | Consistent |
| SP 800-227, *Recommendations for Key-Encapsulation Mechanisms* | Final, 18 Sep 2025 | Final, Sep 2025 | Consistent |
| SP 800-131A Rev. 2 | Final, Mar 2019; Rev. 3 still an initial public draft (21 Oct 2024) | "to be revised" | Consistent: Rev. 3 is not final, so it must not be cited as final |
| FIPS 186-5 | Final, 3 Feb 2023 (errata note) | DSA no longer specified for signing | Consistent |

## Formats and libraries

| Item | Checked | Result |
|---|---|---|
| CycloneDX 1.6.1 schema | `cryptoFunctions` enumeration (no key-agree value); padding enumeration (no PSS); `primitive` includes signature, key-agree, pke, kem, combiner; `relatedCryptoMaterial` types include private-key, public-key, key | Consistent with `pqscan` CBOM output mapping |
| pyca/cryptography 47.0.0 | `hazmat.primitives.asymmetric.mlkem` (ML-KEM-768/1024) and `mldsa` (ML-DSA-44/65/87) present; no SLH-DSA module | Consistent with the policy's pyca prefixes |
| PyCryptodome 4.4.0 | `Crypto.PublicKey.MLKEM`, `Crypto.PublicKey.MLDSA`, `Crypto.PublicKey.Hybrid`, `Crypto.Signature.mldsa` present | **New finding N1** (below) |

## N1 (owner decision required; nothing changed)

PyCryptodome 4.4.0 provides ML-KEM, ML-DSA and a hybrid module. The scanner's approved-hybrid encoding recognises only the pyca ML-KEM/ML-DSA prefixes. The annotation guide's list of PQ components names pyca, `oqs` and `pqcrypto`, not PyCryptodome. A PyCryptodome-based PQ/T hybrid would be neither recognised by the scanner nor explicitly covered by the labelling rule.

Changing the scanner or the guide before F1 alters labelling scope or scanner behaviour, so that is the owner's decision. Until then it is disclosed as a limitation (`owner_decisions_g02_g03_g08_g10.md`; paper limitations).

## Not verified today

- Section numbers and table numbers inside the PDFs; the 17 Nov check stands.
- The contents of the FIPS 203/204 errata.
- W6 (SP 800-227 citation precision in the frozen policy text) is still open and owner-gated.
