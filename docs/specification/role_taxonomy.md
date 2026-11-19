# Role taxonomy and key-provenance taxonomy (frozen, v1.1)

Project: Post-quantum crypto scanner for Python projects. Base paper: Lei Zhang, "Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography Migration", ICSE-Companion '26, pp. 402–403, DOI 10.1145/3774748.3795653 (Pillar P1: PQC-aware detection with "protocol roles" and enriched inventories).

Status: **FROZEN v1.0 on 12 Nov 2026** after the H1 pilot (`docs/pilot/h1_pilot_analysis.md`). Any change requires a new version number, a dated changelog entry at the end of this file, and re-annotation of affected benchmark items.

## 1. Unit of analysis: the cryptographic call site

A *call site* is one Python call expression (or attribute-chained call) in a source file that invokes an API of a supported library (`docs/specification/api_coverage.md`) and either (a) performs a public-key cryptographic operation, (b) creates, loads, derives or reconstructs public-key material, or (c) configures a protocol object of that supported library with public-key algorithm choices (v1.1-r2, G01: protocol configuration in a library outside `api_coverage.md`, such as `ssl` or paramiko, is out of scope; the pinned supported libraries expose no protocol objects, so kind (c) is reserved and not expected in the current frame). A site is identified by `(repository, commit, file, line_start, line_end, api_call)`.

A site is **eligible** for recommendation scoring when it is (a), (b) or (c) above (v1.1) and involves RSA, EC (ECDSA/ECDH, NIST curves), X25519/X448, Ed25519/Ed448, finite-field DH or DSA. Parameter-object constructions (e.g. `padding.PKCS1v15()`, `ec.SECP256R1()`), type references in `isinstance`, docstrings and comments are **ineligible** negatives: a tool that reports them is scored at detection level (false positive), never at recommendation level.

## 2. Cryptographic roles (ground truth, one primary role per site)

| Role | Definition | Typical evidence |
|---|---|---|
| `SIGN` | The site produces a digital signature with a private key. | method `sign`/`sign_ssh_data`, `DSS.new(...).sign`, `pkcs1_15.new(...).sign`, `pss.new(...).sign` |
| `VERIFY` | The site verifies a digital signature with a public key. | method `verify`, `pkcs1_15.new(...).verify` |
| `KEY_ESTABLISHMENT` | The site derives a shared secret with a peer public key (ECDH, X25519, DH) or participates in a protocol key exchange. | `exchange(ec.ECDH(), peer)`, `X25519PrivateKey.exchange`, `DHPrivateKey.exchange` |
| `PK_ENCRYPT` | The site encrypts data (typically a symmetric key, "key transport") with a public key. | `public_key.encrypt(data, padding)`, `PKCS1_OAEP.new(key).encrypt` |
| `PK_DECRYPT` | The site decrypts public-key-encrypted data with a private key. | `private_key.decrypt(ct, padding)`, `PKCS1_OAEP.new(key).decrypt` |
| `KEY_MATERIAL_ONLY` | The site generates, loads, derives or reconstructs a key and the key is **not** consumed by any operation reachable from the site within the analysed scope (export, fingerprinting, type dispatch and storage within the analysed scope only; a key that escapes the scope is `UNKNOWN`, annotation guide Step D). | `generate_private_key`, `load_pem_private_key`, `RSA.import_key` with no reachable `sign`/`verify`/`exchange`/`encrypt`/`decrypt` |
| `PROTOCOL_CONFIG` | The site configures a protocol library object (TLS/SSH contexts, cipher-suite or key-exchange lists, JOSE `alg` registries) rather than calling a primitive. | `ssl.SSLContext.set_ciphers`, `ssl.SSLContext.set_ecdh_curve`, transport KEX preference lists |
| `UNKNOWN` | The role cannot be fixed from the code because it depends on a runtime value (e.g. an `algorithm` string), on dynamic dispatch, or on code outside the analysed scope. Always paired with `assessability = INDETERMINATE` and a `possible_roles` list. | python-jose `CryptographyRSAKey` loaders (sites J06–J09 in the pilot) |

Rules:

1. **Key material inherits the role of its type-valid consumer.** A key-generation or key-loading site whose result flows (by def-use within the function, by attribute assignment inside the same class, by passing through a constructor into such an attribute, or by one level of call) to exactly one operation family receives that family's role, considering only consumers that can succeed for the loaded key type (a public key cannot `sign` or `decrypt`; a private key can do both halves): private key with `sign`/`verify` consumers → `SIGN` (secondary `VERIFY`); public key with `verify` consumer → `VERIFY`; `exchange` → `KEY_ESTABLISHMENT`; `encrypt`/`decrypt` → `PK_ENCRYPT`/`PK_DECRYPT`. `secondary_roles` records the other members of the same family. Consumers reached through methods of the same class count even when those methods are invoked from other modules.
2. **Mixed families mean `UNKNOWN`.** If the key reaches consumers of two different target families (e.g. `verify` and `encrypt`, as in a JOSE key object that serves both JWS and JWE), the site is `UNKNOWN`/`INDETERMINATE` unless a static argument (not a runtime value) selects the family.
3. **No reachable consumer means `KEY_MATERIAL_ONLY`.** This is a determinate role: the correct output is an inventory entry, not a migration target.
4. **Operations fix their own role.** `sign`, `verify`, `exchange`, `encrypt`, `decrypt` method calls on public-key objects are determinate from the method name once the receiver type is known to be a public-key object (for pyca) or the module is known (for PyCryptodome `pkcs1_15`, `pss`, `DSS`, `PKCS1_OAEP`, `PKCS1_v1_5`). The padding object alone (`PKCS1v15` is shared by RSA sign and RSA encrypt in pyca) never fixes the role.
5. **Hybrid flag.** `hybrid_component = yes` marks a quantum-vulnerable component that is combined with an approved PQC algorithm in a PQ/T hybrid construction (SP 800-227 Sec. 4.6, e.g. paramiko `mlkem768x25519-sha256`). The role is still recorded (e.g. `KEY_ESTABLISHMENT`); the policy treats the site as "no migration required, review the combiner".
6. **Scope attribution** (`app` / `test` / `vendored` / `example`) is recorded separately and never changes the role.
7. **One call expression per site.** (v1.1-r3, owner decision G03: in a sampled candidate statement only the call selected by annotation guide Step A is the site; additional same-family calls are recorded in `notes` and are not sites.) A `try: load_a() except: load_b()` fallback pair, or two loaders feeding the same variable, are two sites with the same consumers and labels; provenance is never a composite value. When one candidate statement contains several supported calls, annotation guide v1.2 Step A fixes which call is the site.
8. **Ineligible negatives** carry `gt_role = NONE`, `assessability = DETERMINATE`, `key_provenance = n/a`, `obvious_from_name = null` (JSON null: not applicable; v1.1-r3, owner decision G02), `evidence_needed = none`; they are scored at detection level only.
9. **`possible_roles` vs `secondary_roles`.** `secondary_roles` lists same-family alternatives of a determinate role (e.g. `VERIFY` next to `SIGN`). `possible_roles` is required for `UNKNOWN` and lists the cross-family candidates. The two are never mixed.

## 3. Assessability

| Value | Meaning |
|---|---|
| `DETERMINATE` | A careful human reader can fix one primary role from the repository at the frozen commit using the evidence scopes below. |
| `INDETERMINATE` | The role depends on a runtime value, dynamic dispatch, reflection or code outside the repository. The justified scanner action is to **abstain** (or to emit a dual/undecided target with an explicit reason). |

Assessability is a property of the site, independent of any tool's ability to resolve it.

## 4. Evidence scopes (what a reader needed to fix the role)

`call` (the call expression alone) → `function` (def-use inside the enclosing function) → `cross-function` (same module or class: attribute assignments, helper calls, one call level) → `cross-module` (another module in the repository) → `runtime-value` (cannot be fixed statically). The pilot records this per site in `evidence_scope`.

`obvious_from_name` is `yes` only when the role follows from the method name, given that the receiver is a public-key object of a supported library (its *type*, not its *origin*), or from a single-purpose algorithm name (X25519/X448 are key-agreement-only; Ed25519/Ed448 are signature-only), without inspecting the receiver's origin or consumers. The receiver-type condition matters because `encrypt`/`decrypt`/`sign`/`verify` also exist on AEAD cipher, HMAC and JOSE wrapper objects; "obvious" therefore means "obvious once the receiver is known to be an RSA/EC key", which is the T1→T2 step for an analyzer.

## 5. Key-provenance taxonomy (frozen)

| Provenance | Definition | Examples |
|---|---|---|
| `generated` | Key created in process by a key-generation API. | `rsa.generate_private_key`, `ec.generate_private_key`, `X25519PrivateKey.generate`, `RSA.generate`, `ECC.generate` |
| `loaded-PEM` | Parsed from PEM text. | `load_pem_private_key`, `load_pem_public_key`, `RSA.import_key(pem)` |
| `loaded-DER` | Parsed from DER bytes. | `load_der_private_key`, `load_der_public_key` |
| `loaded-SSH` | Parsed from OpenSSH formats. | `load_ssh_private_key`, `load_ssh_public_key` |
| `loaded-JWK` | Reconstructed from JWK/JWT parameters (`n`,`e`,`d`,`x`,`y`,`crv`). | `RSAPrivateNumbers(...).private_key()`, `EllipticCurvePublicNumbers(...).public_key()` fed from a JWK dict, `RSA.construct` |
| `loaded-certificate` | Public key taken from an X.509 certificate. | `load_pem_x509_certificate(...).public_key()` |
| `constructed-from-parsed-blob` | Reconstructed from numbers parsed from a non-JWK wire/file format. | paramiko OpenSSH blob → `RSAPrivateNumbers` |
| `parameter` | Received as a function/method parameter whose origin is outside the function. | `def sign(self, key, msg): key.sign(...)` when `key` is not resolvable |
| `attribute` | Read from an object attribute (`self.key`, `self.prepared_key`) whose assignment is elsewhere in the class. | pilot sites P01, P06, J04 |
| `env-or-KMS` | Obtained from environment variables, secret managers or KMS/HSM interfaces. | `boto3.client("kms")`, `os.environ["PRIVATE_KEY"]` |
| `unknown` | Cannot be determined. | dynamic attribute, reflection |

`attribute` and `parameter` are *proximate* provenances; the annotator additionally records the *ultimate* provenance set when it can be resolved (e.g. P01: attribute ← {generated, loaded-DER, constructed-from-parsed-blob, wire message}).

## 6. Mapping to CycloneDX 1.6 (verified 2026-11-14 against the official bom-1.6 schema, tag 1.6.1)

The 1.6 `cryptoFunctions` enum is: generate, keygen, encrypt, decrypt, digest, tag, keyderive, sign, verify, encapsulate, decapsulate, other, unknown. It has no key-agreement value, and the `padding` enum (pkcs5, pkcs7, pkcs1v15, oaep, raw, other, unknown) has no PSS. The exporter (`pqscan/export/cbom.py`) therefore uses:

| Role | Component | primitive | cryptoFunctions | Extra |
|---|---|---|---|---|
| SIGN / VERIFY | `algorithm` asset | signature | sign / verify | padding pkcs1v15, or `other` + `pqscan:padding=PSS` |
| KEY_ESTABLISHMENT | `algorithm` asset | key-agree | other | `pqscan:role=KEY_ESTABLISHMENT` |
| PK_ENCRYPT / PK_DECRYPT | `algorithm` asset | pke | encrypt / decrypt | padding oaep / pkcs1v15 |
| key-material sites (any role) | `related-crypto-material` | — | — | type private-key / public-key / key; size when known |
| UNKNOWN | as above by site kind | unknown when no role family applies | unknown | `pqscan:possibleRole` entries |

Every component carries role, tier, action, target class, rationale, policy version, provenance and evidence as `pqscan:*` properties; operation components depend on the key-material components their receiver was traced to.

## Changelog

- v1.1-r3 (2026-11-19; owner decisions G02 and G03; `docs/audit/owner_decisions_g02_g03_g08_g10.md`): ineligible negatives carry `obvious_from_name = null`; rule 7 states that additional same-family calls in a sampled statement are notes, not sites. No role, eligibility outcome or label value other than this representation changed.
- v1.1-r2 (2026-11-19, editorial; second review G01; `docs/audit/second_review_closure.md`): kind (c) requires a protocol object of a supported library; out-of-scope protocol configuration stays ineligible (Step A of the guide). No role, value or eligibility outcome changed.
- v1.1 (2026-11-18, before any labelling and any test-split access; owner-approved pre-F1 decision register `docs/audit/owner_decision_register_v1.0.5.md`): kind (c) protocol-configuration sites are eligible when they occur (F01), aligning the taxonomy with recommendation policy Sec. 5, the annotation guide, the schema and the scoring table; the scanner's lack of PROTOCOL_CONFIG output stays a stated limitation (D10). KEY_MATERIAL_ONLY storage means storage within the analysed scope, and an observed escape is UNKNOWN (F21). Rule 7 points to the multi-call rule (F03). No role, assessability value or provenance value was added or removed. The v1.0.1 text is kept in `docs/specification/archive/v1.0.4/role_taxonomy.md`.
- v1.0.1 (2026-11-14): Sec. 6 replaced by the schema-verified mapping (no change to roles or rules).
- v1.0 (2026-11-12): frozen after the H1 pilot and after an independent re-derivation of 12 pilot labels (12/12 role, 12/12 assessability, 11/12 provenance agreement). Added `hybrid_component`, the "type-valid consumer" wording of rule 1, rules 7–9 (one call per site; ineligible-negative fields; `possible_roles` vs `secondary_roles`) and the receiver-type condition on `obvious_from_name`, all in response to that review. The pilot showed 15 of 30 eligible sites (50%) require consumer evidence and one hybrid site (P16).
