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

Several open-source Python PQC scanners, inspected at source for this project, map targets by algorithm family or hard-coded pattern, or emit an undecided dual target. Examples include "RSA → ML-KEM" and "ML-KEM / ML-DSA" (Sec. III; `related_work_matrix.md`). A role-incorrect target can mislead a migration; an undecided one shifts the decision back to the developer.

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

Full matrix: `related_work_matrix.md`. Content claims marked ◐ there must be re-checked against full text before submission.

**PQC migration and readiness.**
- Systematic reviews and frameworks describe migration as an organisational and software-engineering process [nather2024slr, hasan2024framework, vonnethen2024pmmp, nather2026agility, ott2019challenges], with industrial evidence [zhang2023db2, zhang2021y2k], library surveys [ahmed2025survey] and binary-level tooling [rattanavipanon2025toolchain].
- Empirical readiness studies measure detection or repository-level readiness:
  - Mehl scans 14,508 repositories and labels them vulnerable, quantum-safe or PQC-ready, and states that it does not prescribe migration [mehl2026esem]; its released artefact contains results only [mehl2026zenodo];
  - Yuan et al. assess PQC support at package and repository level [yuan2026pqcwild];
  - Ye et al. detect quantum-vulnerable usage in Python by keywords [ye2024quantumthreats];
  - Mallick et al. classify implementations from runtime telemetry [mallick2026classifying].
- None of these attaches role-specific guidance to individual call sites.

**Cryptographic API detection and misuse.** Python misuse detectors resolve cryptographic objects across functions: Cryptolation [frantz2024cryptolation], CryptoPyt [guo2024cryptopyt], Cryptbara [cho2025cryptbara], with a prevalence study in [wickert2021licma]. Java analyses use typestate and slicing [kruger2021crysl, moffie2025cryptoscope]. Ami et al. showed that detectors fail under semantics-preserving mutations [ami2022masc, ami2026mutation], and Chen et al. warned about benchmark gaming [chen2024precise]. Reviews and LLM-based studies cover the wider field [mousavi2025misuse, xia2025beyond], and general Python call-graph construction is studied in [salis2021pycg]. We reuse these ideas (bounded inter-procedural resolution, mutation operators, a frozen held-out split) for role inference rather than misuse. We do **not** claim the analysis technique as new.

**Crypto inventory and CBOM.** CycloneDX 1.6 (ECMA-424) provides `cryptoProperties` [ecma2024ecma424]. Several tools generate CBOMs, and they disagree [bogli2026bfcbom, yamamuro2026sok, schmitt2024inventories, nather2026hiddenciphers]; taxonomy-driven inventories add role-like categories without automation [lee2026taxonomy]. CBOM output is a requirement here, not a contribution.

**Role and provenance in existing PQC scanners.** Source inspection on 12 Nov 2026 of the pinned baseline tools [tool_pqcheck, tool_pqcaudit, tool_postquant, tool_qsafe, tool_qsaregex, tool_pqblocks] and CBOMkit found:
- roles hard-coded per pattern;
- roles assigned by library rather than by use;
- dual "ML-KEM / ML-DSA" targets;
- no abstention outcome.

These statements describe the inspected versions only.

**Migration correctness and abstention.**
- Pallarés de Bonrostro et al. evaluate LLM migration of code fragments whose migration category was labelled by hand [pallares2026llm].
- Shaw combines static analysis with LLM-assisted risk scoring [shaw2026auditing].
- Abstention and selective prediction are classical [chow1970reject] and used in SE tooling [rathnasuriya2026defer].

To our knowledge, *pending the final novelty audit*, the inspected literature reports no call-site-level measurement of whether PQC recommendations are correct for the site's role. That measurement is what our protocol is designed to produce.

## IV. Research Gap and Contributions

**Gap (provisional).** Existing Python PQC tools detect quantum-vulnerable usage. In the inspected set, none infers a site-level role from receiver provenance, method, arguments and consumers, and none abstains. Recommendation correctness per site has not been measured.

**Contributions of this paper as it stands** (implemented and verified; not claimed novel until the novelty audit):
1. **C1 – Operational role and provenance taxonomy.** Eight roles, eleven key-provenance kinds, and rules for consumer-based role inheritance, mixed-family indeterminacy and key-material-only sites (Sec. VI). Frozen before the benchmark was labelled.
2. **C2 – Analyser.** Bounded key-provenance and consumer tracing with an ordinal evidence tier T0–T3, and four evidence-restricted ablation arms (Sec. V–VI).
3. **C3 – Role-conditioned guidance policy.** Explicit non-migration classes (inventory, protocol review, approved hybrid, abstain) and a KEM-DEM redesign class for public-key encryption, each tied to NIST sections (Sec. VII).
4. **C4 – Pre-registered, coverage-matched evaluation protocol.** Frozen repository split, tool-independent sampling, single-investigator labelling with an isolated AI-assisted review, and confirmatory families F-B and F-A. The statistics are differentially verified and simulation-calibrated (Sec. VIII–IX).

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

[Figure 1 placeholder: architecture diagram. Source available in `docs/demo/architecture.md`; final figure per the IEEE template.]

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
- **Family F-A:** the proposed system (`full` at T2) against each baseline that ran, using a one-sided exact McNemar test on both-ran sites [mcnemar1947note], with Holm correction [holm1979simple].
- **Algorithm-family baselines** (B1-algorithm, B1-dual) are evaluated on the same candidate sites.

**Estimand and matching** (analysis plan Secs. 2–5). For repository r with common evaluable set C_r of size n_r, let R_F,r and R_M,r be the recommendation counts of the two arms. Matching sets

  k_r = min(R_F,r, R_M,r).  (1)

The arm with the excess withdraws its lowest-tier recommendations first, breaking ties by SHA-256 keys; withdrawn recommendations are judged as abstentions. The primary estimate is the exact tie-averaged repository-balanced difference

  δ̃ = (1/K_e) Σ_{r estimable} δ̃_r,  (2)

where δ̃_r is the expected difference in complete-policy correctness per site over all permitted tie orders.

**Inference** (Sec. 7).
- **Bootstrap.** A re-matching percentile bootstrap [efron1979bootstrap] resamples sites within repositories and draws fresh random tie keys per resample; B = 10,000, seed 20261113. The p-value is

  p = (1 + #{δ*_b ≤ d0}) / (B + 1),  (3)

  with B = 100,000 when |p − t| < 3√(p(1−p)/B).
- **Coverage-gap guard.**

  g = (1/K_e) Σ_r (R_F,r − R_M,r)/n_r.  (4)

  When g < 1/10, the guarded p-value is p* = min(1, 2p), applied before Holm and also to H2b.
- **Feasibility gate.** It passes iff Σ_r k_r / Σ_r n_r ≥ 1/5 and at least 5 of the 7 repositories have k_r ≥ 5.
- **Assessability.** K = 7 is always reported. If K_e < 7, the confirmatory result is "not assessable as pre-registered".
- **Execution failures.** Handled by a common evaluable set, with S-F1/S-F2 sensitivity analyses.

**Population statement.** Results are limited to RSA/EC/Ed/X public-key call sites in files importing pyca or PyCryptodome, within the candidate frame of the 13 frozen repositories. Inference is conditional on the seven test repositories.

**Freeze sequence.**
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

**B. Statistical calibration under the planning model** [E30–E33].

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
- Two clean environments built from a source archive reproduced the seven committed demonstration outputs byte-for-byte.
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
- CBOMkit and Mehl's scanner are not run, and are reported as such.

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
