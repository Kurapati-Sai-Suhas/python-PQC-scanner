# Provisional IEEE manuscript draft (content only)

**Status: PROVISIONAL DRAFT, 17 Nov 2026. Not submittable.**
- This is the content of an *implementation, design and pre-registered evaluation-protocol* paper.
- It is **not** a completed empirical paper. The research question has not been answered. No labelled real-world evaluation has been run.
- Formatting is deliberately template-neutral until the owner supplies the reference IEEE paper (`author_decisions.md` D1).
- Citations are BibTeX keys from `references.bib`, written as [key].
- Every number is traceable to `evidence_register.md` (E-ids in brackets).
- Placeholders read **[NOT YET EVALUATED — requires owner annotation and F1/F2/E]**.

---

## Title (provisional; author decision D2)

*Role-Aware Post-Quantum Migration Guidance for Python: Bounded Key-Provenance Inference with Evidence-Gated Abstention*

Project title, unchanged: "Post-quantum crypto scanner for Python projects".

## Abstract (provisional; must be rewritten after evaluation)

**Problem.** Static scanners that support the migration to post-quantum cryptography (PQC) typically attach a target such as ML-KEM or ML-DSA to an RSA or elliptic-curve finding on the basis of the algorithm name. The correct target, however, depends on the *cryptographic role* of the call site:
- digital signatures migrate to ML-DSA;
- key establishment is redesigned around ML-KEM;
- public-key encryption has no drop-in replacement and requires a KEM-DEM redesign.

**System.** We present pqscan, a static analyser for Python projects that use pyca/cryptography and PyCryptodome. It:
- detects RSA, EC, Ed25519/Ed448 and X25519/X448 call sites;
- infers each site's role from the method, its arguments, receiver typing, and bounded key-provenance and consumer tracing;
- assigns an ordinal evidence tier;
- maps the role to NIST-aligned guidance, or abstains when the evidence is insufficient;
- emits CycloneDX 1.6 CBOM, SARIF 2.1.0 and JSON.

**Evaluation design.** We also describe a pre-registered evaluation protocol for the research question: does provenance-aware role inference improve recommendation correctness at comparable coverage, compared with algorithm-family and method/argument baselines? The protocol uses:
- 13 repositories frozen before analysis (4 development, 2 validation, 7 sealed test);
- coverage-matched comparisons with a re-matching bootstrap;
- a coverage-gap guard, a feasibility gate and Holm control.

**Present evidence.**
- 489 automated tests pass.
- The statistical procedure agrees exactly with an independent reference implementation.
- It holds its error rates in simulation under an assumed planning model.
- The outputs are schema-valid and reproducible from a clean environment.

**Not yet available.** Human-labelled results, and therefore any statement about recommendation correctness or superiority over baselines: [NOT YET EVALUATED — requires owner annotation and F1/F2/E].

## Index Terms (provisional)

Post-quantum cryptography, cryptographic migration, static analysis, Python, cryptographic bill of materials, ML-KEM, ML-DSA, abstention, pre-registration.

---

## I. Introduction

NIST has standardised ML-KEM [nist2024fips203] and ML-DSA [nist2024fips204]. NIST IR 8547 (final, October 2026) deprecates quantum-vulnerable signature and key-establishment schemes after 2030 and disallows them after 2035 [nist2026ir8547, Sec. 4.1.1 Table 2; Sec. 4.1.2 Table 4]. Organisations must therefore find and migrate their uses of RSA and elliptic-curve cryptography [joseph2022transitioning, nather2024slr]. Zhang's vision of Quantum-Safe Software Engineering identifies code-level semantics, including the "protocol roles" that cryptographic operations implement, as missing from current inventory-oriented approaches [zhang2026qsse].

The migration target of an RSA or EC call site depends on what the call *does*:
- a signature migrates to a signature scheme (ML-DSA, optionally SLH-DSA [nist2024fips205]);
- key agreement is redesigned around a key-encapsulation mechanism (ML-KEM), with PQ/T hybrids as a transitional option [nist2025sp800227, Sec. 4.6];
- RSA public-key encryption ("key transport") has no drop-in PQC replacement and must be redesigned as KEM + KDF + authenticated encryption [nist2025sp800227, Sec. 5.2.1; nist2024fips203, Sec. 3.3].

Several open-source Python PQC scanners, inspected at source for this project, map targets by algorithm family or hard-coded pattern, or emit an undecided dual target. Examples include "RSA → ML-KEM-768" and "ML-KEM / ML-DSA" (Sec. III; pinned-source evidence in `related_work_fulltext_audit.md`). A role-incorrect target can mislead a migration; an undecided one shifts the decision back to the developer.

We address this with **role-aware, evidence-gated migration guidance**:
- the role of each site is inferred from evidence available statically within a bounded scope;
- the strength of that evidence is recorded as an ordinal tier;
- guidance is issued only when the tier meets a pre-registered threshold, otherwise the tool abstains.

**Research question (adopted, verbatim):** *Does bounded key-provenance-aware cryptographic role inference improve the correctness of post-quantum migration recommendations at comparable coverage for Python cryptographic call sites, compared with algorithm-family and method/argument-based baselines?*

**This paper's status.** This draft reports:
- the design and implementation of the analyser;
- the frozen benchmark and the pre-registered evaluation protocol;
- verification evidence for the software and the statistics.

The empirical answer to the research question needs human-labelled sites from sealed test repositories, which do not yet exist (Sec. XIV).

## II. Background and Motivation

**A. NIST transition timeline.**
- IR 8547 Table 2: ECDSA (≥ 112-bit), EdDSA (≥ 128-bit) and RSA (≥ 112-bit) signatures are deprecated after 2030 and disallowed after 2035.
- Table 4: finite-field DH/MQV, EC DH/MQV and RSA key establishment follow the same timeline.
- Harvest-now-decrypt-later risk may require earlier migration of key establishment [nist2026ir8547, Sec. 4.1.2].
- ML-KEM is currently the only approved PQ key-establishment scheme, and NIST recommends ML-KEM-768 as the default parameter set [nist2026ir8547, Sec. 4.1.2].
- ML-DSA-44 provides category 2 only with a random bit generator of at least 192-bit strength, otherwise category 1 [nist2026ir8547, Table 3 note; nist2024fips204, Sec. 3.6.1].

**B. KEMs are not public-key encryption.**
- A KEM produces a shared secret and a ciphertext. FIPS 203 permits the 256-bit shared secret to be used directly as a symmetric key, or as input to an approved key derivation [nist2024fips203, Sec. 3.3]. The same section states that the internal K-PKE component is not approved as a stand-alone public-key encryption scheme.
- SP 800-227 describes public-key encryption from a KEM only through the KEM-DEM construction: encapsulate, then encrypt the message under the derived key [nist2025sp800227, Sec. 5.2.1], with key post-processing in Sec. 4.3.
- An `encrypt(data)` call on an RSA key therefore cannot be replaced by an ML-KEM call with the same shape.

**C. Hybrids and legacy use.**
- Hybrid solutions are "typically expected to be temporary" [nist2026ir8547, Sec. 3.2].
- SP 800-227 Sec. 4.6 specifies multi-algorithm KEMs and approved key combiners.
- Legacy use (e.g. verifying an existing signature) is defined in SP 800-131A, which NIST will revise [nist2026ir8547, Sec. 4].

**D. Why role inference is non-trivial in Python.** Key objects are often generated or loaded in one place and used elsewhere: in a class attribute, passed as a parameter, returned to a caller, or behind a JOSE key abstraction that serves both signatures and encryption. A call such as `RSA.import_key(pem)` does not reveal whether the key will sign, verify, encrypt or decrypt. The role is decided by its consumers.

## III. Related Work (provisional; final novelty audit pending)

**Evidence basis.**
- Content statements below are verified in full text (page numbers in `related_work_fulltext_audit.md`) or, for tools, in the pinned source (file:line).
- Works whose full text could not be accessed are cited only for their title-level scope and marked †.
- Bibliographic metadata of every entry is verified separately (`references.bib`).

**PQC migration and readiness.**
- Migration has been studied as a process for IP networks [nather2024slr] and enterprises [hasan2024framework], and through industrial experience [zhang2023db2]. Other work covers library support [ahmed2025survey], binary-level detection of quantum-vulnerable executables [rattanavipanon2025toolchain], crypto-agility definitions [nather2026agility], and process and organisational guidance [vonnethen2024pmmp†, joseph2022transitioning†, ott2019challenges†, zhang2021y2k†].
- **Mehl** [mehl2026esem] statically scans 14,508 GitHub repositories (Python patterns for 11 libraries and 14 calls) and labels them vulnerable, quantum-safe or PQC-ready. It explicitly "measures where source code still relies on quantum-vulnerable public-key primitives rather than prescribing how to migrate" (p. 3). Its accuracy check is repository-level: 19 repositories labelled from project documentation, not line by line (pp. 7–8). Custom wrappers are not captured (p. 7). Its results dataset is [mehl2026zenodo].
- **Mallick et al.** distinguish classical from PQ key exchange and signatures from runtime workload [mallick2026classifying].
- **Yuan et al.** study PQC readiness of open-source ecosystems [yuan2026pqcwild†]. Their full text was not accessible to us, so we make no claim about their method.
- Ye et al. address quantum-threat discovery in Python applications [ye2024quantumthreats†].

**Cryptographic API analysis and misuse detection.**
- Wickert et al. found misuses in 52.26% of 895 Python projects [wickert2021licma].
- Python misuse detectors with inter-procedural reasoning exist [frantz2024cryptolation†, guo2024cryptopyt†, cho2025cryptbara†], as does typestate-based specification for Java [kruger2021crysl†]. We could not inspect their full texts. They are the closest prior analyses to our bounded provenance tracing, so we do **not** claim the tracing technique as new.
- Cryptoscope builds inventories by slicing from cryptographic calls to their parameters and objects. Its design covers Python, but it is evaluated on seven Java applications [moffie2025cryptoscope].
- MASC evaluates misuse detectors with usage-based mutation operators and finds undocumented flaws [ami2026mutation; earlier version ami2022masc]. Our Dataset A operators follow this idea.
- Chen et al. show that misuse detectors produce false positives on real application code that hand-crafted benchmarks did not reveal [chen2024precise]. This motivates pairing synthetic data with frozen real repositories.
- Reviews and LLM-based studies cover the wider field [mousavi2025misuse, xia2025beyond]. General Python call-graph construction is studied in [salis2021pycg]; pqscan does not use it.

**Crypto inventory and CBOM.**
- CycloneDX 1.6 (ECMA-424) defines `cryptoProperties` [ecma2024ecma424].
- Crypsy discovers cryptographic assets in Ruby and Go sources and in TLS/SSH configuration files, and emits CycloneDX 1.7 [nather2026hiddenciphers]. It reports its 52 PQ migration candidates collectively as requiring "ML-KEM, ML-DSA, or SLH-DSA" (p. 16), not per site by role.
- Further inventory and CBOM work exists [bogli2026bfcbom†, yamamuro2026sok†, schmitt2024inventories†, lee2026taxonomy†].
- CBOM output is a requirement of this project, not a contribution.

**PQC scanners: what the pinned versions implement.** Source inspection of the pinned baselines (read-only, 18 Nov 2026) shows the targets are fixed by pattern, library or name, not inferred from use:
- pqcheck maps RSA to "migrate to ML-KEM-768" in its bundled policies, and its README documents "usage-context blindness" [tool_pqcheck];
- pqc-audit maps RSA key generation to "ML-KEM (key establishment) / ML-DSA (signatures)" [tool_pqcaudit];
- PostQuant classifies pyca RSA key generation as asymmetric encryption and PyCryptodome RSA key generation as a signature, i.e. by library [tool_postquant];
- qsafe labels RSA key generation and `PKCS1_OAEP` "RSA Key Exchange" with target ML-KEM 768 [tool_qsafe];
- the Quantum-Safe Auditor maps RSA to "ML-KEM / ML-DSA" (Table 1 of [shaw2026auditing]; [tool_qsaregex]).

The sixth pinned baseline, pqblocks-scan [tool_pqblocks], was checked only for its PQC algorithm tables; its role handling was not re-inspected. These statements describe the pinned versions only. **Our own comparison of these tools against labelled sites has not been run.**

**Migration correctness and abstention.**
- Pallarés de Bonrostro et al. evaluate LLM migration of 800 synthetic Python fragments. The target of each fragment is fixed by its category in the dataset design [pallares2026llm].
- Shaw reports detection-level precision on 602 findings labelled by one author, with recall 100% by construction [shaw2026auditing].
- Abstention is classical [chow1970reject†] and used for code models [rathnasuriya2026defer].

**Scoped gap statement.** Among the 20 papers whose full text we inspected and the six pinned baseline tools whose source we inspected, none:
1. infers a site-level cryptographic role from key provenance and consumers;
2. conditions the PQC target on that role with an explicit abstain outcome; or
3. measures per-site recommendation correctness.

This statement does not cover the works marked †. In particular, Yuan et al., CryptoPyt, Cryptbara and Cryptolation must be checked before submission.

## IV. Research Gap and Contributions

**Gap (scoped; see the statement at the end of Sec. III).** Within the inspected set:
- PQC tools attach targets by algorithm, pattern or library;
- PQC studies measure detection or readiness;
- no inspected work evaluates per-site recommendation correctness.

**Contributions of this paper as it stands** (implemented and verified; novelty provisional until the final novelty audit):
1. **C1 – Operational role and provenance taxonomy.** Eight roles, eleven key-provenance kinds, and rules for consumer-based role inheritance, mixed-family indeterminacy and key-material-only sites (Sec. VI). Frozen before benchmark labelling.
2. **C2 – Analyser.** Bounded key-provenance and consumer tracing with an ordinal evidence tier T0–T3, and four evidence-restricted ablation arms (Secs. V–VI). The tracing technique itself builds on established inter-procedural analysis and is not claimed as new.
3. **C3 – Role-conditioned guidance policy.** Explicit non-migration classes (inventory, protocol review, approved hybrid, abstain) and a KEM-DEM redesign class for public-key encryption, each tied to NIST sections (Sec. VII).
4. **C4 – Pre-registered, coverage-matched evaluation protocol.** Frozen repository split; strata that do not depend on any tool; single-investigator labelling with an isolated AI-assisted review; confirmatory families F-B and F-A. The statistics are differentially verified and simulation-calibrated (Secs. VIII–IX).

**Contributions that require the pending evaluation:**
- **C5:** a role-labelled real-world benchmark and the measurements RQ1–RQ4.
  **[NOT YET EVALUATED — requires owner annotation and F1/F2/E]**

## V. Proposed System Architecture

pqscan is a command-line tool (`pqscan scan <path>`). It never imports or executes the scanned code.

| Module | Package | Function |
|---|---|---|
| A | `pqscan/detect` | Semgrep CE 1.185.0 rules [tool_semgrep] for pyca and PyCryptodome; candidate detection and rule ids |
| B | `pqscan/semantic` | `ast`-based import and alias resolution, receiver typing, argument resolution, bounded key-provenance and consumer tracing, hybrid-context detection |
| C | `pqscan/roles` | Role decision table and evidence tier |
| D | `pqscan/policy` | Frozen policy v1.1: role → target class, tier threshold (default T2), NIST-referenced rationale |
| E | `pqscan/export` | JSON; CycloneDX 1.6 CBOM [ecma2024ecma424], schema-validated before writing (exit code 3 if invalid); SARIF 2.1.0 [oasis2023sarif] |
| F–G | `pqscan/bench`, `pqscan/baselines` | Evaluation tooling: sampler, ledger, packets, judge, matching, H2/F-A statistics, baseline adapters |

Module B finds sites independently of Semgrep, and Semgrep rule ids are joined by location. A scan without Semgrep lists the same sites [E54; lecturer-demo outputs 01 vs 07]. Every finding carries:
- evidence (location, API, receiver description, provenance, consumers);
- the decision (role, tier, reason, possible and secondary roles);
- the recommendation (action, target class, target text, parameter set, rationale, NIST references, policy version, threshold, abstention reason).

[Fig. 1: `docs/paper/figures/fig1_architecture.svg` (content-first; restyle to the template). Fig. 2, the role, tier and policy decision flow, is `fig2_role_tier_flow.svg`.]

## VI. Cryptographic Role and Key-Provenance Inference

**A. Unit and roles.** A *call site* is one call expression that performs a public-key operation, creates or loads public-key material, or configures a protocol object (taxonomy v1.0.1).

| Role | Meaning | Typical evidence |
|---|---|---|
| SIGN | produce a signature | `sign`, `pkcs1_15.new(k).sign` |
| VERIFY | verify a signature | `verify` |
| KEY_ESTABLISHMENT | derive a shared secret with a peer key | `exchange(ec.ECDH(), peer)`, X25519 |
| PK_ENCRYPT | encrypt with a public key (key transport) | `public_key.encrypt`, `PKCS1_OAEP.new(k).encrypt` |
| PK_DECRYPT | decrypt with a private key | `decrypt` |
| KEY_MATERIAL_ONLY | key generated or loaded, with no consumer in scope | `generate_private_key` used only for export |
| PROTOCOL_CONFIG | configures a protocol object | TLS/SSH algorithm lists |
| UNKNOWN | role depends on runtime values or out-of-scope code | JOSE key object used for JWS and JWE |

**Inference rules:**
- **Rule 1.** Key material inherits the role of its *type-valid* consumers.
- **Rule 2.** Consumers from two families make the site UNKNOWN, with its possible roles listed.
- **Rule 3.** No consumer means KEY_MATERIAL_ONLY.
- **Rule 4.** Operations take their role from the method once the receiver is a public-key object.

**B. Bounded provenance and consumer tracing.** Starting from the key-producing call, Module B follows the value:
- through local def-use within the function;
- through aliases, cycle-protected;
- through `self.attr` assignments to every method of the class;
- through tuple-packed key pairs;
- through PyCryptodome signer and cipher constructors;
- through peer arguments of `exchange`;
- across **at most two call levels** that leave the class, within the same module, in both directions (parameter binding and `return`) (`pqscan/semantic/consumers.py`, `MAX_CALL_DEPTH = 2`).

Escapes are recorded and never guessed through: a public return, a call to an unresolved callee, storage outside the class. Cross-module flows are not traced; this is a stated limitation. Provenance kinds: generated, loaded-PEM, loaded-DER, loaded-SSH, loaded-JWK, loaded-certificate, constructed-from-parsed-blob, parameter, attribute, env-or-KMS, unknown.

**C. Evidence tiers** (`pqscan/roles/classifier.py`).
- **Operations:**
  - T0: receiver unresolved and no algorithm-specific argument;
  - T1: one of {receiver typed as a key object, algorithm-specific argument};
  - T2: both;
  - T3: T2 plus a resolved, non-conflicting key origin.
  - Any conflict caps the tier at T1.
- **Key material:**
  - one consumer family with no escape → that role, T3;
  - one family with an escape → T2;
  - two or more families → UNKNOWN, T2;
  - no consumer and no escape → KEY_MATERIAL_ONLY, T2;
  - single-purpose algorithms decide when consumers escape: X25519/X448/DH → key establishment; Ed25519/Ed448/DSA → signature.

**D. Ablation arms.** The four arms below restrict the evidence available to the *same* decision table, so that only the evidence differs between compared arms:
- `method-only`;
- `method+args`;
- `method+args+recv`;
- `full` (adds provenance and consumers).

**E. Hybrids.** A classical component combined with a matching-family approved PQ API in the same class or function is marked as a hybrid component. ML-KEM qualifies for key establishment; ML-DSA for signatures.

**F. Worked example** (original synthetic code; `docs/paper/example/`). Listing 1 is abridged; the full file is `token_service.py`. Every outcome below is pqscan's actual output (`output_summary.txt`, `output_scan.json`), not a hand-derived expectation.

```python
from cryptography.hazmat.primitives.asymmetric import rsa as rsa_alias          # import alias

def _load_signing_key(pem):                                    # private wrapper
    return serialization.load_pem_private_key(pem, None)      # K1  key material, loaded-PEM

class TokenSigner:
    def __init__(self, pem):
        self._key = _load_signing_key(pem)                    # wrapper result -> attribute
    def sign(self, payload):
        return self._key.sign(payload, PSS(...), SHA256())    # O1  operation

def sign_with(key, payload):                                  # key is an untyped parameter
    return key.sign(payload, PKCS1v15(), SHA256())            # O2

def make_key():                                               # public: callers unknown
    return rsa_alias.generate_private_key(65537, 3072)        # K2

class Envelope:
    def __init__(self):  self._k = rsa_alias.generate_private_key(65537, 3072)    # K3
    def seal_signature(self, m):  return self._k.sign(m, PSS(...), SHA256())      # O3
    def open(self, c):            return self._k.decrypt(c, OAEP(...))            # O4
```

*Listing 1: Worked example (abridged).*

```
K1 load_pem_private_key ──return (in-module caller)──► TokenSigner.__init__ ──► self._key ──► self._key.sign  (O1)
   provenance: loaded-PEM            consumer families = {SIG}, no escape  ⇒ K1: SIGN, T3 ; O1: SIGN, T3
K2 generate_private_key ──return from public make_key──► (outside analysed scope)   ⇒ escape, no consumer, RSA multi-purpose
                                                                                     ⇒ UNKNOWN, T1 → ABSTAIN
K3 generate_private_key ──► self._k ──► sign (SIG)  and  ──► decrypt (PKE)          ⇒ two families ⇒ UNKNOWN, T2 → ABSTAIN
O2 key.sign(…, PKCS1v15, …) with `key` an untyped parameter                         ⇒ argument evidence only ⇒ SIGN, T1 → ABSTAIN (τ = T2)
```

*Figure E1 (text form; final rendering per the template): Provenance and consumer flow in Listing 1.*

| Site | Role, tier (pqscan) | Action at τ = T2 | Why |
|---|---|---|---|
| K1 | SIGN, T3 | RECOMMEND SIG | The key is traced through the private wrapper's return and the attribute to its only consumer (`sign`), so the key inherits that role (rule 1). The algorithm stays `ANY` because a PEM loader does not reveal it; the role does not depend on it. |
| O1 | SIGN, T3 | RECOMMEND SIG | The method fixes the role; the receiver is resolved to K1's concrete origin |
| O2 | SIGN, T1 | **ABSTAIN** | Only the RSA-specific padding is visible; the receiver is a parameter |
| K2 | UNKNOWN, T1 | **ABSTAIN** | Escapes the analysed scope before any consumer is seen |
| K3 | UNKNOWN, T2 | **ABSTAIN** | Consumers from two families (rule 2); possible roles listed |
| O3, O4 | SIGN T2; PK_DECRYPT T2 | RECOMMEND SIG; KEM_DEM | Receiver resolved, but the origin also feeds another family, so the tier is capped at T2 |

**Matching illustration.** Under the H2-1 comparison at T0, `full` recommends 5 sites (K1, O1, O2, O3, O4). `method+args` recommends 4 (O1–O4), because without provenance K1 is UNKNOWN. Matching gives k = 4 (equation 1). `full` withdraws one recommendation from its lowest tier, T1, which holds only O2 (j = m = 1, so w = 1 in equation (2a)). This shows the mechanics only; without labels it implies nothing about correctness.

**Scope of the example.**
- The wrapper and its caller are in the same module, which is within the tracing bound.
- A loader in another module, a key passed through more than two call levels outside the class, or dynamic dispatch would not be traced. Such sites would be classified at a lower tier or as UNKNOWN.

## VII. Post-Quantum Migration Recommendation Policy

Policy v1.1 (`pqscan/policy/policy_v1_1.yaml`, frozen 2026-11-12) is a fixed table [E40]. The threshold τ = T2 is pre-registered.

| Role | Class | Guidance (abridged) | Primary sources |
|---|---|---|---|
| SIGN | SIG | Migrate to ML-DSA (ML-DSA-65 by default, a project choice); SLH-DSA where its trade-offs fit; verifiers must accept ML-DSA before signers switch | [nist2024fips204]; [nist2024fips205]; [nist2026ir8547] Table 2 |
| VERIFY | SIG | Add ML-DSA verification; keep legacy verification only for already-issued signatures | [nist2026ir8547] Sec. 4 (legacy use), Table 2 |
| KEY_ESTABLISHMENT | KEM | Redesign around ML-KEM (ML-KEM-768); PQ/T hybrid via an approved combiner as a transitional design; encapsulate/decapsulate, not `exchange(peer)` | [nist2024fips203]; [nist2025sp800227] Sec. 4.6; [nist2026ir8547] Sec. 4.1.2, Table 4 |
| PK_ENCRYPT, PK_DECRYPT | KEM_DEM | **Not a drop-in replacement.** Redesign as KEM + KDF + AEAD; the `encrypt(data)` / `decrypt(ct)` call shape cannot be preserved | [nist2025sp800227] Secs. 5.2.1, 4.3; [nist2024fips203] Sec. 3.3 |
| KEY_MATERIAL_ONLY | INVENTORY | No target; inventory the key and determine its downstream role | — |
| PROTOCOL_CONFIG | PROTOCOL_REVIEW | Enable the protocol library's PQC or hybrid options | [nist2026ir8547] |
| approved hybrid component | NO_ACTION_HYBRID | No migration of this component now; plan a PQC-only follow-up; review the combiner | [nist2025sp800227] Sec. 4.6; [nist2026ir8547] Sec. 3.2 |
| UNKNOWN, or tier < τ | ABSTAIN | No recommendation; missing evidence and possible roles are stated | — |

**Correctness notes:**
- The policy never states that ML-KEM replaces RSA in general.
- It never asserts security equivalence.
- It introduces no non-NIST algorithms.
- DSA signing receives a dedicated sentence, because DSA is not in IR 8547 Table 2.

Every statement above was checked against the PDFs [E42]. One citation-precision issue is recorded for the owner (W6): the policy text cites SP 800-227 "Secs. 2.1, 5.2"; the precise sections are 5.2.1 and 4.3.

**Known gap.** Module C never emits PROTOCOL_CONFIG [E41], so the PROTOCOL_REVIEW class is reachable only through ground-truth labels and is never produced by pqscan.

## VIII. Dataset and Benchmark Design

**A. Dataset B (real repositories)** [E10–E12].
- 13 public repositories, frozen on 2026-11-13 by a mechanical qualification. Criteria: public GitHub, an OSI licence, ≥ 100 stars or a security purpose, pyca and/or PyCryptodome RSA/EC use, and ≥ 10 regex candidates.
- Split: **4 development, 2 validation, 7 sealed test.**
- Repositories in a baseline tool's tuning corpus are excluded from the test split. All four development repositories are such repositories; no validation or test repository is [E10b].
- The test split has not been fetched for analysis; only its manifest metadata is used here.
- PyCryptodome public-key use is concentrated in two test repositories. The six development/validation repositories contain 2 PyCryptodome imports in total [E10c].

**B. Sampling (protocol v1.0.4).**
- **Pool:** the union of a regex over-approximation, every baseline's findings and pqscan Module A, deduplicated by enclosing statement. pqscan is never the sole source.
- **Scope classes:** vendored > test > example > app.
- **Strata:** S1-app and S1-nonapp (files importing pyca or PyCryptodome), and S2 (all other candidates).
- **Order:** seeded and uniformly random within each stratum. Issuance uses batches of 10 (7 app + up to 3 non-app), with a one-third non-app cap.
- **Quotas:** 30 (test), 25 (development) and 25 (validation) eligible sites per repository, for **360 planned primary-set eligible sites** [E11].
- **Current DV frames:** **3,503 candidate locations** in the six development/validation repositories (S1-app 920, S1-nonapp 1,080, S2 1,503) [E12]. These are candidates, not eligible sites; eligibility exists only after labelling.

**C. Labelling (annotation guide v1.1).**
- **Annotator.** The single investigator labels each candidate from source with all tool outputs hidden, recording `context_used`.
- **AI review.** A separately conducted, isolated, blind AI-assisted review works from a fixed packet only. It is never ground truth.
- **Adjudication.** The investigator adjudicates every disagreement.
- **Integrity.** A hash-chained ledger records every step; labels themselves are never committed.
- **Intra-rater reliability.** A re-label sample (n = max(50, ⌈0.10 N⌉)) is presented no earlier than 14 days after the last primary label.
- **Reporting language.** "Single-investigator labels with a separately conducted AI-assisted review and investigator adjudication". Never "independent annotators".

**D. Dataset A (synthetic)** [E13].
- 61 base cases (key 26, operation 22, negative 13) × invariance operators = **388 instances**: key 182, op 154, negative 52; 336 eligible.
- Operators: identity, alias-import, wrapper-function, class-method, cross-function, dict-dispatch, and `loaded-key` (an evidence change, analysed separately).
- Labels are **by construction**; a 78-instance subset awaits blind validation.
- Split by base case: 31 development / 30 holdout. The holdout is sealed until F1.
- All statistics cluster on the base case. Synthetic and real results are never pooled.

**E. Pilot.** 31 sites from two development repositories (30 eligible) [E14]. The pilot fixed the taxonomy. Module B was debugged on these sites, so pilot outcomes are circular and are **not** used as evidence.

## IX. Experimental Methodology (pre-registered, protocol v1.0.4)

**RQ mapping.** The adopted research question corresponds to protocol **RQ2** (H2, "at equal coverage"), with the coverage condition of **RQ3**. The protocol also pre-registers:
- **RQ1:** H1a/H1b, prevalence and baseline harm;
- **RQ4:** H4, robustness on Dataset A.

**Judging** (scoring policy v1.0). For each site and method, the judgment is one of: CORRECT, INCORRECT (with a harm category: role-incompatible, false assurance, over-recommendation), UNDECIDED, UNJUSTIFIED, UNASSESSABLE, DETECTED_ONLY, MISSED or EXECUTION_FAILURE.
- An abstention is CORRECT only on an indeterminate site.
- A strict sensitivity score treats "drop-in" wording for KEM-family sites as harmful.

**Comparisons.**
- **Family F-B (confirmatory; Holm, m = 3, one-sided α = 0.025):**
  - H2-1: `full` (T0) vs `method+args` (T0) — **H2a**;
  - H2-3: vs `method+args+recv`;
  - H2-4: vs `method-only`.
- **H2b** (≥ 10 points) is exploratory and outside error control.
- **Family F-A:** the proposed system (`full` at T2) against each baseline that ran (at most 8), using a one-sided exact McNemar test on both-ran sites **at natural coverage** (no matching, no guard) [mcnemar1947note], with Holm correction [holm1979simple].
- **Experiment A baselines** (protocol Sec. 4):
  - the six runnable external tools;
  - a simple algorithm-name mapping and a method/argument-only mapping, both computed on pqscan's own candidate sites so that only the decision rule differs. The code provides two algorithm-name variants: `B1-algorithm` (RSA → KEM, EC → SIG, …) and `B1-dual` (dual target for multi-purpose algorithms). Which of them enters F-A must be named before F1 (owner decision D15).
- **Coverage note (for the adopted RQ; presentation pending owner decision D7, `d7_rq_alignment.md`).**
  - The coverage-matched ("comparable coverage") comparisons are family F-B (H2-1, H2-3, H2-4), whose comparators are the method-only, method+arguments and method+arguments+receiver arms.
  - Family F-A, against the algorithm-name mapping, the method/argument-only mapping and the external tools, is at natural coverage. Coverage is reported alongside each result.
  - Abstention at matched coverage is addressed by RQ3, which compares the system's own policies with random withholding.

**Estimand and matching** (analysis plan Secs. 2–5). For repository r with common evaluable set C_r of size n_r, let R_F,r and R_M,r be the recommendation counts of the two arms. Matching sets

  k_r = min(R_F,r, R_M,r).  (1)

The arm with the excess withdraws its lowest-tier recommendations first, breaking ties by SHA-256 keys; withdrawn recommendations are judged as abstentions. The primary estimate is the exact tie-averaged repository-balanced difference

  δ̃ = (1/K_e) Σ_{r estimable} δ̃_r,  (2)

where δ̃_r is the exact expectation, over all permitted tie orders, of the difference in complete-policy correctness per common evaluable site (analysis plan Sec. 5; `pqscan/bench/matching.py`).

*Tie-average closed form.* Let:
- A ∈ {F, M} be the withdrawing arm, with excess e_r = R_A,r − k_r > 0;
- G_0, G_1, G_2, G_3 be its RECOMMEND sites in tiers T0 < T1 < T2 < T3;
- b be the boundary tier: the smallest t with Σ_{s≤t} |G_s| ≥ e_r;
- j = e_r − Σ_{s<b} |G_s| be the number withdrawn inside the boundary tier, and m = |G_b|.

Each RECOMMEND site i of arm A then has withdrawal probability

  w_i = 1 if tier(i) < b;  w_i = j/m if tier(i) = b;  w_i = 0 if tier(i) > b.  (2a)

The non-withdrawing arm and all non-RECOMMEND actions have w_i = 0. With c(·) the frozen judge's complete-policy correctness indicator, a withdrawn recommendation is scored as ABSTAIN:

  E[X_i] = (1 − w_i^F) c(o_i^F) + w_i^F c(ABSTAIN_i),  E[Y_i] = (1 − w_i^M) c(o_i^M) + w_i^M c(ABSTAIN_i),  (2b)

  δ̃_r = (1/n_r) Σ_{i ∈ C_r} (E[X_i] − E[Y_i]).  (2c)

Equation (2a) is the exact average over the m!/(j!(m − j)!) equally likely choices of which j boundary-tier recommendations are withdrawn, so δ̃_r has no tie-breaking randomness. The ranking-free sensitivity variant ignores tiers and uses w_i = e_r / R_A,r for every RECOMMEND of arm A.

**Inference** (Sec. 7).
- **Bootstrap.** A re-matching percentile bootstrap [efron1979bootstrap] resamples sites within repositories and draws fresh random tie keys per resample; B = 10,000, seed 20261113. The p-value is

  p = (1 + #{δ*_b ≤ d0}) / (B + 1),  (3)

  with B = 100,000 when |p − t| < 3√(p(1−p)/B). Bootstrapping δ̃_r itself, with exact tie-averaging inside each resample, is not used: it was found liberal in the planning calibration (R4-13).
- **Resample count in calibration versus analysis (B).** The pre-F1 calibration (Sec. X-B) used a fixed B = 1,000 with the Monte Carlo rule switched off. It consumed random numbers in the same way as the archived planning calibration (R4-13), so that every cell could be compared with it (`scripts/phase3_acceptance.py`, header). The confirmatory analysis uses B = 10,000 plus the Monte Carlo rule, which reduces the Monte Carlo error of each individual p-value.
  - The only recorded check of sensitivity to B is in the superseded planning report R4-03c, for an earlier version of the bootstrap without the coverage-gap guard. There, B = 5,000 (4,000 data sets) gave rejection rates matching the B = 1,000 figures for four scenarios (R4-03c Sec. 3).
  - No B-sensitivity run was made for the final guarded procedure.
  - We therefore report the calibration as evidence for the procedure at B = 1,000. We do not claim that it bounds the error rates at B = 10,000 exactly.
- **Coverage-gap guard.**

  g = (1/K_e) Σ_r (R_F,r − R_M,r)/n_r.  (4)

  When g < 1/10, the guarded p-value is p* = min(1, 2p), applied before Holm and also to H2b.
- **Feasibility gate.** It passes iff Σ_r k_r / Σ_r n_r ≥ 1/5 and at least 5 of the 7 repositories have k_r ≥ 5.
- **Assessability.** K = 7 is always reported. If K_e < 7, the confirmatory result is "not assessable as pre-registered".
- **Execution failures.** Handled by a common evaluable set, with S-F1/S-F2 sensitivity analyses.

**Population statement.** Results are limited to RSA/EC/Ed/X public-key call sites in files importing pyca or PyCryptodome, within the candidate frame of the 13 frozen repositories. Inference is conditional on the seven test repositories.

**Freeze sequence** (Fig. 3: `docs/paper/figures/fig3_protocol_timeline.svg`).
1. Specification review.
2. DV annotation and reliability.
3. **F1:** pre-test methodological and code freeze, with a committed freeze record and a git tag.
4. Test-split fetch, then T annotation.
5. **F2:** label freeze.
6. **E:** a single evaluation run.

## X. Implementation and System Evaluation

**A. Software verification** [T1–T3].
- The production suite has **489 tests passing and 1 skipped** (a symlink test the Windows host does not permit). It covers rule fixtures, semantic evidence, roles, policy (including NIST-alignment checks), exports, the benchmark tooling and the statistics.
- **Differential verification:** production matching, guard, gate, Holm and bootstrap agree *exactly* with an independently written reference implementation on:
  - 1,000 random matching cases;
  - 1,000 guard/gate/Holm cases;
  - bootstrap distributions at three seeds;
  - a worked example.
- The reference implementation's own 82 tests pass.

**B. Statistical calibration under the planning model** [E30–E33]. Fig. 4: `docs/paper/figures/fig4_calibration.svg`.

| Check | Data sets per cell | Worst observed (α/3, α/2, α) | Criterion |
|---|---|---|---|
| Type I error, 17 fixed-repository scenarios | 20,000 | 0.0061 / 0.0093 / 0.0191 | ≤ nominal + 3 MC-SE: met |
| Near-equal-coverage cells (8) | 10,000 | 0.0092 / 0.0125 / 0.0213 | met |
| Family-wise error, Holm m = 3 (8 configurations) | 10,000 | 0.0125 | ≤ 0.025 + 3 MC-SE: met |
| Two-stratum, unstratified bootstrap (3 configurations) | 10,000 | 0.0025 / 0.0040 / 0.0114 | met; unstratified variant kept |
| Random repositories (S16) | 20,000 | α: 0.0415 | **not calibrated for generalisation** (expected; not used) |

Calibration ran with B = 1,000 on commit aa9d6b0, and pqscan is unchanged since [E30]. These results show that the *procedure* controls error under an *assumed* data-generating model. **They say nothing about scanner accuracy.**

**C. Outputs, determinism and reproducibility** [E53–E55].
- Three CBOMs validate against strict CycloneDX 1.6 and three SARIF files against SARIF 2.1.0.
- Two clean environments built from a source archive reproduced the seven committed demonstration outputs byte-for-byte. Both ran on Windows 11 with Python 3.12.10; other platforms have not been verified.
- Real-library outputs were byte-identical across both runs, and the CBOM is byte-identical across repeated runs.
- On the development and validation repositories, all 60 tool runs (6 baselines and 4 pqscan arms × 6 repositories) completed with 0 timeouts and 6,830 file-runs processed [E20].
- Normalised findings were identical across repeated runs [E55].

**D. Demonstration (not an evaluation)** [E50–E52]. We ran pqscan on its demonstration fixture and on the installed source of two cryptographic libraries. Neither library is a benchmark repository.

| Input | Files | Sites | RECOMMEND | FLAG (inventory) | ABSTAIN | Failures |
|---|---|---|---|---|---|---|
| Demo fixture (synthetic) | 7 | 23 | 20 | 1 | 2 | 0 |
| pyca cryptography 47.0.0 (library code) | 77 | 13 | 2 (SIG) | 0 | 11 | 0 |
| PyCryptodome 4.4.0 (library code, mostly self-tests) | 228 | 1,214 | 210 (SIG 124, KEM_DEM 86) | 431 | 573 | 0 |

On all 1,227 real-code sites:
- every non-abstaining site received exactly its role's policy class;
- every abstention had role UNKNOWN or tier below T2;
- no recommendation was issued at T0 or T1 [E52].

This shows that the policy is applied *consistently*, not that the roles are *correct*. The code is library-internal, and most PyCryptodome sites are in self-test files. **The counts are detection volume, not accuracy**, and are not representative of application code.

## XI. Results and Discussion

All results below depend on completed annotation and the F1 → T → F2 → E sequence. Table and figure shells are in `results_placeholders.md`.

- **RQ1 / H1a** (share of eligible sites needing evidence beyond the name): **[NOT YET EVALUATED — requires owner annotation and F1/F2/E]**
- **RQ1 / H1b** (harmful + undecided + unjustified rate per baseline): **[NOT YET EVALUATED — requires owner annotation and F1/F2/E]**
- **RQ2 / H2a** (H2-1, confirmatory): **[NOT YET EVALUATED — requires owner annotation and F1/F2/E]**. Reported strictly with the template "H2a (confirmatory): supported / not supported / not assessable …". The phrase "H2 supported" is never used.
- **RQ2 / H2b** (≥ 10 points, exploratory): **[NOT YET EVALUATED — requires owner annotation and F1/F2/E]**
- **H2-3, H2-4** (ablations): **[NOT YET EVALUATED — requires owner annotation and F1/F2/E]**
- **F-A** (proposed system vs each baseline): **[NOT YET EVALUATED — requires owner annotation and F1/F2/E]**
- **RQ3 / H3** (risk–coverage, AURC): **[NOT YET EVALUATED — requires owner annotation and F1/F2/E]**
- **RQ4 / H4** (invariance on Dataset A): **[NOT YET EVALUATED — requires Dataset A validation (D2) and, for the holdout, F1]**
- **Reliability** (intra-rater κ; owner–AI agreement): **[NOT YET EVALUATED — requires annotation and the 14-day gap]**

**Discussion (allowed now).** The present evidence supports statements about engineering properties only: implementation, verification, reproducibility and calibration. Whether role-aware, provenance-aware guidance is more often correct at equal coverage is the open empirical question this protocol is designed to answer. A negative result on any hypothesis will be reported as such (protocol Sec. 1).

## XII. Threats to Validity

**Construct validity.**
- Correctness is defined by a frozen role → class table derived from NIST documents; another policy could judge differently.
- The judge's text classification of baseline outputs, and the "drop-in" sensitivity rule, are heuristics. Both are fixed before evaluation.

**Internal validity.**
- **Single annotator.** There is one investigator plus an isolated AI-assisted review; no independent human annotator exists. Mitigations: blinding to tool outputs, the packet-first subset, the intra-rater re-label after ≥ 14 days, and the hash-chained ledger.
- **AI reviewer is not an independent annotator.**
  - The isolated AI-assisted review is performed by a large language model, run by the investigator, on a fixed packet. It is not an independent human annotator.
  - It may share failure modes with the investigator, for instance through common training material, the same packet framing, or the same misreading of an API. It also has failure modes of its own (hallucinated API semantics; run-to-run variation, which is measured).
  - Owner–AI agreement therefore does **not** establish inter-annotator reliability. It is reported only as a review-consistency statistic, and the AI output is never used as ground truth (annotation guide v1.1 Sec. 1).
  - Reliability evidence for the labels is limited to the intra-rater re-label.
  - The investigator also built the analyser. Blinding to tool outputs mitigates this but does not remove it.
- **Circular pilot.** The pilot repositories are development repositories and were used to tune Module B.
- **Candidate pool.** The pool includes tool findings, which may favour sites some tool detects. Partial mitigation: the regex over-approximation and annotator-added sites.

**Statistical conclusion validity.**
- Calibration holds under an assumed model, with B = 1,000 in calibration against B = 10,000 in analysis.
- Seven repositories limit power. The feasibility gate may make H2 "not assessable".

**External validity.**
- Results are conditional on seven fixed repositories. S16 shows the procedure is not calibrated for new repositories.
- Two libraries only; Python 3 only.
- PyCryptodome real use is concentrated in two test repositories.
- Dataset A has no non-app strata and no hybrids.

**Baseline fairness.**
- Baselines were not designed to recommend per role.
- Dual targets are scored as undecided, not harmful.
- CBOMkit is not run (owner decision D4 = A). Mehl's scanner is reported separately under the protocol.
  - The protocol's stated basis was a results-only artefact. The Zenodo record does contain only results, but the paper links a public source repository (MIT licence).
  - Whether to run it is open owner decision D14. It emits no migration recommendation by design (p. 3), so it could contribute detection-level comparison only.

## XIII. Limitations and Future Work

**Limitations:**
- no PROTOCOL_CONFIG detection;
- no cross-module provenance (call depth ≤ 2 within a module);
- no finite-field DH or DSA in Dataset A;
- PQ/T hybrids detected only through matching-family APIs;
- unresolved symmetric-cipher calls displayed with a method-implied role (they always abstain);
- no runtime or dynamic analysis;
- no refactoring or verification (AQuA pillars P2 and P3 [zhang2026qsse]).

**Future work.** First, complete the pre-registered evaluation. Then:
- an external annotator;
- additional libraries;
- protocol-configuration detection;
- validated refactoring patterns for one role.

## XIV. Conclusion (provisional)

We designed and implemented pqscan, a role-aware, evidence-gated PQC migration-guidance analyser for Python, together with a pre-registered evaluation protocol. Its statistics are differentially verified and calibrated by simulation. The software and outputs are tested, schema-valid and reproducible. **Whether role-aware guidance improves recommendation correctness at comparable coverage remains to be established** by the pre-registered evaluation on sealed repositories: [NOT YET EVALUATED — requires owner annotation and F1/F2/E].

## References

See `references.bib` (verified entries only). Every [key] above resolves to an entry there.

## Appendix (material available for the camera-ready version)

- Taxonomy: `docs/specification/role_taxonomy.md`.
- Policy: `pqscan/policy/policy_v1_1.yaml`, `docs/specification/recommendation_policy.md`.
- Scoring: `docs/specification/scoring_policy.md`.
- Protocol: `docs/specification/evaluation_protocol.md` (v1.0.4).
- Analysis plan: `docs/specification/phase3_analysis_plan.md`.
- Annotation guide: `docs/benchmark/annotation_guide.md` (v1.1).
- Acceptance: `docs/implementation/acceptance/statistical_acceptance.md`.
- Demonstration: `docs/final/final_project_demo.md`.
