# Role-to-migration recommendation policy (v1.1, pre-registered)

Project: Post-quantum crypto scanner for Python projects. Base paper: Zhang, ICSE-Companion '26, DOI 10.1145/3774748.3795653.

Status: **v1.1, 12 Nov 2026, frozen before any benchmark experiment**, after an independent cryptography review of v1.0 (Section 7). The policy may not change after final test results are viewed (Development rule 12).

## 1. Standards basis (verified directly from the NIST PDFs on 12 Nov 2026; line numbers refer to the plain-text extractions kept with the audit evidence)

| Source | Verified statement | Location |
|---|---|---|
| FIPS 203 (Aug 2024, final) | ML-KEM is a key-encapsulation mechanism with parameter sets ML-KEM-512 (security category 1), ML-KEM-768 (category 3), ML-KEM-1024 (category 5). The 256-bit shared secret "can be used directly as a shared secret key for symmetric cryptography"; if further keys are needed they "shall be derived … in an approved manner" (SP 800-108 / SP 800-56C). | Sec. 3.2 (category list), Sec. 8 prose; Sec. 3.3 "Approved usage of the shared secret key" |
| FIPS 204 (Aug 2024, final) | ML-DSA generates and verifies digital signatures; ML-DSA-44 is claimed in category 2 (reduced to category 1 if the RBG has < 192 bits of security), ML-DSA-65 category 3, ML-DSA-87 category 5. | abstract; Sec. 3.6.1 (RBG strength); Sec. 4 |
| FIPS 205 (Aug 2024, final) | SLH-DSA is a stateless hash-based digital-signature algorithm. | abstract |
| SP 800-227 (Sep 2025, final) | A KEM establishes a shared secret used with symmetric algorithms; the KEM/DEM paradigm combines a KEM with a symmetric data-encryption mechanism to build public-key encryption (Sec. 2.1); key transport with a KEM that "does not natively perform key transport (e.g., ML-KEM)" is achieved only via the KEM–DEM procedure (Sec. 5.2, Fig. 7); key derivation may be required (Sec. 4.3); key confirmation "should be used" and may be implicit, e.g. successful use of the key for authenticated encryption (Sec. 4.4); an encapsulating party using another party's static encapsulation key "must have assurance of the other party's ownership of the key" (Sec. 4.2); Sec. 4.6 describes PQ/T hybrids and composite KEMs (ML-KEM + a traditional scheme) with approved key combiners (Sec. 4.6.2). | Secs. 2.1, 4.2–4.6, 5.2 |
| NIST IR 8547 (Oct 2026, final) | Quantum-vulnerable signature algorithms ECDSA (≥ 112-bit), EdDSA (≥ 128-bit) and RSA (≥ 112-bit) and key-establishment schemes (finite-field DH/MQV, elliptic-curve DH/MQV, RSA-based, all ≥ 112-bit) are **deprecated after 2030** and **disallowed after 2035**. Sec. 4.1 defines *deprecated* (may be used with some security risk), *disallowed* (no longer allowed for the stated purpose) and *legacy use* (only to process already-protected information, e.g. verify a signature); the assignment of those statuses to specific algorithms lives in SP 800-131A, which NIST "will revise". "NIST recommends using ML-KEM-768 as the default parameter set." Hybrid solutions "are typically expected to be temporary measures that lead to a second transition" to PQC-only; a hybrid combination can be FIPS 140-validated if at least one input comes from an approved scheme, with combiner guidance in SP 800-227. | Sec. 4.1 (definitions, Tables 2–4), Sec. 4.1.2 (ML-KEM-768 default), Sec. 3 (hybrids) |

Not cited because not verified: specific IETF RFC numbers for hybrid key exchange in TLS/SSH/JOSE; CNSA 2.0 dates. These appear only as "protocol-specific review" pointers.

## 2. Target classes

| Class | Meaning | Standard |
|---|---|---|
| `SIG` | Migrate to a PQC digital-signature scheme: ML-DSA (FIPS 204), or SLH-DSA (FIPS 205) where its size/speed trade-offs are acceptable. Parameter set by required category: ML-DSA-65 (category 3) as the default; ML-DSA-44 only with an RBG of ≥ 192-bit strength if category 2 is required; ML-DSA-87 for category 5. | FIPS 204 / 205; IR 8547 Table 3 |
| `KEM` | Redesign key establishment around ML-KEM (FIPS 203) following SP 800-227: encapsulate/decapsulate roles (not a Diffie–Hellman-style symmetric `exchange(peer)` interface), ephemeral keys used once, key derivation (Sec. 4.3) where more keys are needed, key confirmation (Sec. 4.4, possibly implicit via AEAD). A PQ/T hybrid with the existing ECDH/X25519 through an approved combiner (Sec. 4.6) is an acceptable *transitional* design. Default parameter set ML-KEM-768 (IR 8547 recommendation). | FIPS 203, SP 800-227, IR 8547 |
| `KEM_DEM` | Public-key encryption / key transport must be redesigned as KEM + KDF + symmetric AEAD (KEM/DEM, SP 800-227 Sec. 2.1 and Sec. 5.2 key-transport procedure). **ML-KEM is not a drop-in replacement for `encrypt(message)` / `decrypt(ciphertext)`**: the sender cannot choose the plaintext of an encapsulation; the KEM outputs the shared secret, and the content key is derived from it. The recipient's static encapsulation key must be authenticated (SP 800-227 Sec. 4.2), as the RSA public key had to be. Scored in the same family as `KEM`; the recommendation text must say "redesign", never "replace". | SP 800-227, FIPS 203 Sec. 3.3 |
| `INVENTORY` | No migration target is justified at this site: report the asset, algorithm, parameters, provenance and that no consumer was found; the developer must determine the downstream role. | — |
| `PROTOCOL_REVIEW` | Migration is decided at the protocol library (TLS, SSH, JOSE): enable the library's ML-KEM hybrid key exchange / ML-DSA certificate options; never patch primitives inside configuration code. | IR 8547 Sec. 4.2 (application-specific guidance) |
| `NO_ACTION_HYBRID` | The site is the traditional component of a PQ/T hybrid whose PQ component is a NIST-approved scheme (ML-KEM; ML-DSA/SLH-DSA for signatures). No migration of the traditional component is required *now*; the hybrid is transitional (IR 8547 Sec. 3), so a follow-up to PQC-only is recorded, and the combiner is reviewed against SP 800-227 Sec. 4.6. A hybrid whose PQ component is not NIST-approved (e.g. `sntrup761x25519`) does **not** receive this class; it is treated as `KEY_ESTABLISHMENT` → `KEM`. | SP 800-227 Sec. 4.6; IR 8547 Sec. 3 |
| `ABSTAIN` | Evidence is insufficient for any class; the output names the missing evidence (role, provenance, consumer) and lists the possible roles. | — |

## 3. Policy table (role → class)

| Ground-truth / inferred role | Class | Rationale text template (emitted by Module D) |
|---|---|---|
| `SIGN` | `SIG` | "RSA/ECDSA/EdDSA signing is deprecated after 2030 and disallowed after 2035 (IR 8547 Table 2). Migrate signing to ML-DSA (FIPS 204); dual/hybrid signatures are a transitional option; verifiers and certificate chains must be able to accept ML-DSA before signers switch." For finite-field DSA: "DSA is no longer specified in FIPS 186-5 and is not listed in IR 8547 Table 2; migrate to ML-DSA (FIPS 204)." |
| `VERIFY` | `SIG` | "Add ML-DSA (FIPS 204) verification so that migrated signers can be accepted. IR 8547 defines 'legacy use' as processing already-protected data such as verifying an existing signature; whether RSA/ECDSA verification of already-issued signatures keeps that status after 2035 is set by SP 800-131A (to be revised). Retain legacy verification only for already-issued signatures; do not accept new RSA/ECDSA signatures after the transition." |
| `KEY_ESTABLISHMENT` | `KEM` | "ECDH/DH/X25519 key establishment is deprecated after 2030 and disallowed after 2035 (IR 8547 Table 4) and is exposed to harvest-now-decrypt-later. Redesign around ML-KEM (FIPS 203; ML-KEM-768 recommended by IR 8547) per SP 800-227; a PQ/T hybrid with the existing scheme via an approved combiner (SP 800-227 Sec. 4.6) is an acceptable transitional design. ML-KEM uses encapsulate/decapsulate, not a symmetric exchange(peer) call." |
| `PK_ENCRYPT` | `KEM_DEM` | "RSA public-key encryption / key transport (PKCS#1 v1.5, OAEP) has no drop-in PQC replacement. Redesign as KEM + KDF + AEAD (SP 800-227 Secs. 2.1, 5.2): the sender encapsulates to the recipient's authenticated ML-KEM key, derives the content key from the shared secret (FIPS 203 Sec. 3.3), and encrypts with an AEAD. The existing encrypt(data) call shape cannot be preserved." |
| `PK_DECRYPT` | `KEM_DEM` | As above, decapsulation side. |
| `KEY_MATERIAL_ONLY` | `INVENTORY` | "RSA/EC key material with no consumer found in the analysed scope. No target is recommended; determine the downstream role first." |
| `PROTOCOL_CONFIG` | `PROTOCOL_REVIEW` | "Protocol configuration site. Migrate by enabling the library's PQC/hybrid options; do not replace primitives here." |
| `KEY_ESTABLISHMENT`, `SIGN` or `VERIFY` with `hybrid_component = yes` (approved PQ component of the matching family; the only roles for which the flag is permitted, owner decision TA19, 19 Nov 2026) | `NO_ACTION_HYBRID` | "Traditional component of a PQ/T hybrid with an approved PQ algorithm; no migration of this component is required now; hybrids are transitional (IR 8547) — plan a PQC-only follow-up; review the combiner per SP 800-227 Sec. 4.6." |
| `UNKNOWN` (INDETERMINATE) | `ABSTAIN` | "Role cannot be determined: <missing evidence>. Possible roles: <list>. No single target is justified." |

## 4. Evidence-tier gate (Module D parameter, pre-registered)

Module C emits an ordinal evidence tier T0–T3 (`data_dictionary.md`). Module D recommends only when `tier ≥ τ`; below τ it abstains with the tier and the missing evidence. **τ = T2 is the pre-registered primary threshold**; T1 and T3 are sensitivity arms. Tiers are ordinal labels, never converted to probabilities.

## 5. Scoring a tool's recommendation (Module F and the pilot)

Given a site with expected class E (Section 3) and a tool output mapped by the published adapters to R ∈ {`SIG`, `KEM`, `DUAL`, `PQC_ALREADY`, `NONE`}:

| Condition | Judgment | Harm category |
|---|---|---|
| no output at the site | `MISSED` | — |
| flagged with no target (R = NONE) on a site with E ∈ {SIG, KEM, KEM_DEM} | `DETECTED_ONLY` | — |
| E ∈ {SIG, KEM, KEM_DEM} and R is E's family (KEM_DEM ≡ KEM family) | `CORRECT` | — |
| E = SIG and R = KEM, or E ∈ {KEM, KEM_DEM} and R = SIG | `INCORRECT` | `ROLE_INCOMPATIBLE` |
| R = `PQC_ALREADY` on a quantum-vulnerable, non-hybrid site | `INCORRECT` | `FALSE_ASSURANCE` |
| E ∈ {INVENTORY, NO_ACTION_HYBRID, PROTOCOL_REVIEW} and R ∈ {SIG, KEM} | `INCORRECT` | `OVER_RECOMMENDATION` |
| E ∈ {INVENTORY, PROTOCOL_REVIEW} and R = NONE (flag only) | `CORRECT` | — |
| E = NO_ACTION_HYBRID and R ∈ {NONE, PQC_ALREADY} | `CORRECT` | — |
| R = `DUAL` ("ML-KEM / ML-DSA") on a DETERMINATE site | `UNDECIDED` | — |
| site INDETERMINATE and R single target | `UNJUSTIFIED` | — |
| site INDETERMINATE and R = DUAL | `UNDECIDED` | — |
| site INDETERMINATE and the tool abstains with a reason | `CORRECT` | — |
| ineligible site reported | `FALSE_POSITIVE_SITE` (detection level) | — |

"Harmful" in every report = `INCORRECT` with any harm category. `UNDECIDED` and `UNJUSTIFIED` are reported separately and never folded into "harmful".

`PROTOCOL_CONFIG` sites are eligible for this scoring (they are kind (c) in the taxonomy); detection-level metrics treat them as true sites.

**Drop-in wording flag.** For E ∈ {KEM, KEM_DEM}, if the tool's text implies a direct substitution ("replace X with ML-KEM", "replaces … entirely", "drop-in", "swap"), `dropin_wording = true` is recorded. The judgment stays `CORRECT` (family) under the pre-registered definition of harm, but **drop-in counts are reported beside harmful counts in every table** so the distinction cannot be dropped later.

Scoring is consolidated and frozen in `scoring_policy.md` v1.0 (2026-11-14). That file adds the pre-registered strict sensitivity analysis (drop-in wording on KEM-family sites counts as UNSUPPORTED_DROP_IN), execution-failure handling for external tools, and false-positive counting of abstentions on ineligible sites. The role → class table above is unchanged.

## 6. Explicit non-claims

- ML-KEM is never recommended as a replacement for a signature; ML-DSA is never recommended for key establishment or encryption.
- No specific protocol RFC is cited for hybrid TLS/SSH/JOSE until verified.
- Parameter-set defaults follow IR 8547 (ML-KEM-768) and a category-3 default for signatures (ML-DSA-65); they are not a security assessment of the scanned system.
- The policy does not cover symmetric algorithms, hashes, or key sizes.

## 7. Independent review record

| Date | Reviewer | Scope | Outcome |
|---|---|---|---|
| 2026-11-12 | Independent AI reviewer (separate context, cryptography/PQC persona) with access to the NIST text extractions | v1.0 Sections 1–6 | APPROVE WITH CHANGES: 3 MAJOR (legacy-use attribution, hybrid permanence and approved-PQ condition, PROTOCOL_CONFIG scoring inconsistency), 8 MINOR (EdDSA 128-bit row, definitions location, FIPS 203 citation location, key confirmation "should", drop-in flag for KEM, drop-in reporting, missing scoring rows, DSA sentence, additional source statements). All eleven incorporated in v1.1; every cited line re-checked by the author against the source text. |
| pending | Human reviewer outside the build team (lecturer or external) | full document | **required before the Phase 3 freeze** |

## Changelog

- v1.1, text clarification r5 (2026-11-19; owner decision TA19): the `NO_ACTION_HYBRID` row names the only roles for which `hybrid_component` is permitted (`KEY_ESTABLISHMENT`, `SIGN`, `VERIFY`), as the policy engine already enforces (`pqscan/policy/engine.py`). No mapping, template, threshold or policy-version change. Pre-change text: `docs/specification/archive/v1.0.5-r4/recommendation_policy.md`.
- v1.1 (2026-11-12): incorporated independent review (Section 7).
- v1.0 (2026-11-12): initial pre-registered policy.
