# Supported API inventory and coverage status (v1.0)

Project: Post-quantum crypto scanner for Python projects.

Scope rule (frozen): two libraries, **PyCA `cryptography`** (tested against 47.0.0) and **PyCryptodome** (tested against 4.4.0, import roots `Crypto` and `Cryptodome`). Core algorithms RSA and EC (ECDSA/ECDH on NIST curves). Bounded extensions: X25519/X448, Ed25519/Ed448, finite-field DH, DSA — included only as far as they fall out of the same detection machinery; they must not delay RSA/EC.

Status legend (tracker vocabulary): `NOT_STARTED` → `IN_PROGRESS` → `IMPLEMENTED` (code exists) → `TESTED` (positive and negative fixtures pass) → `VALIDATED` (independently reviewed on real code). A row may be claimed as supported in any report only when its status is at least `TESTED`.

**Status update 2026-11-14 (Phase 2).** Rows marked TESTED have a Semgrep positive fixture line (`tests/fixtures/semgrep/*_positive.py`, matched by `tests/test_detect_rules.py`) and are typed by Module B in `tests/test_semantic_typing.py` / `tests/test_semantic_evidence.py`. Negative fixtures (`pyca_negative.py`, `no_crypto_import.py`) cover parameter objects, comments, docstrings, symmetric receivers and the import gate. The operation rows C3–C6, C10–C12, C14 and D5–D10 are exercised end to end by `tests/test_roles.py` and `tests/test_pipeline_export.py`. None is VALIDATED: that needs the independent annotation of real sites (Phase 3).

## 1. PyCA `cryptography`

| # | API (fully qualified) | Kind | Role evidence | Provenance | Module A (Semgrep) | Module B/C | Status |
|---|---|---|---|---|---|---|---|
| C1 | `hazmat.primitives.asymmetric.rsa.generate_private_key(public_exponent, key_size)` | keygen | none (consumer needed) | generated | yes | yes | TESTED |
| C2 | `rsa.RSAPrivateNumbers(...).private_key()` / `rsa.RSAPublicNumbers(...).public_key()` | key construct | none | loaded-JWK / constructed-from-parsed-blob | yes | yes | TESTED |
| C3 | `RSAPrivateKey.sign(data, padding, algorithm)` | operation | SIGN | receiver | yes | yes | TESTED |
| C4 | `RSAPublicKey.verify(signature, data, padding, algorithm)` | operation | VERIFY | receiver | yes | yes | TESTED |
| C5 | `RSAPublicKey.encrypt(plaintext, padding)` | operation | PK_ENCRYPT | receiver | yes | yes | TESTED |
| C6 | `RSAPrivateKey.decrypt(ciphertext, padding)` | operation | PK_DECRYPT | receiver | yes | yes | TESTED |
| C7 | `ec.generate_private_key(curve)` | keygen | none | generated | yes | yes | TESTED |
| C8 | `ec.derive_private_key(private_value, curve)` | key construct | none | constructed-from-parsed-blob | yes | yes | TESTED |
| C9 | `ec.EllipticCurvePublicKey.from_encoded_point(curve, data)`; `EllipticCurvePublicNumbers(...).public_key()`; `EllipticCurvePrivateNumbers(...).private_key()` | key construct | none | loaded-JWK / parsed-blob | yes | yes | TESTED |
| C10 | `EllipticCurvePrivateKey.sign(data, ec.ECDSA(hash))` | operation | SIGN | receiver | yes | yes | TESTED |
| C11 | `EllipticCurvePublicKey.verify(signature, data, ec.ECDSA(hash))` | operation | VERIFY | receiver | yes | yes | TESTED |
| C12 | `EllipticCurvePrivateKey.exchange(ec.ECDH(), peer_public_key)` | operation | KEY_ESTABLISHMENT | receiver | yes | yes | TESTED |
| C13 | `x25519.X25519PrivateKey.generate()` / `from_private_bytes()`; `X25519PublicKey.from_public_bytes()` | keygen/construct | KEY_ESTABLISHMENT (single-purpose algorithm) | generated / parsed | yes | yes | TESTED |
| C14 | `X25519PrivateKey.exchange(peer_public_key)` (and X448) | operation | KEY_ESTABLISHMENT | receiver | yes | yes | TESTED |
| C15 | `ed25519.Ed25519PrivateKey.generate()/sign()`, `Ed25519PublicKey.verify()` (and Ed448) | keygen/operation | SIGN/VERIFY (single-purpose) | generated/receiver | yes | yes | TESTED (extension) |
| C16 | `dh.generate_parameters()`, `DHParameters.generate_private_key()`, `DHPrivateKey.exchange(peer)` | keygen/operation | KEY_ESTABLISHMENT | generated/receiver | yes | yes | TESTED at detection level only (Module A); `DHParameters.generate_private_key` and `DHPrivateKey.exchange` role inference not typed (gap) |
| C17 | `serialization.load_pem_private_key(data, password)` / `load_pem_public_key(data)` | loader | none | loaded-PEM | yes | yes | TESTED |
| C18 | `serialization.load_der_private_key()` / `load_der_public_key()` | loader | none | loaded-DER | yes | yes | TESTED |
| C19 | `serialization.load_ssh_private_key()` / `load_ssh_public_key()` / `load_ssh_public_identity()` | loader | none | loaded-SSH | yes | yes | TESTED |
| C20 | `serialization.pkcs12.load_key_and_certificates()` | loader | none | loaded-PKCS12 (recorded as loaded-DER) | yes | partial | TESTED at detection level only (Module A); PKCS#12 loader not typed by Module B (gap) |
| C21 | `x509.load_pem_x509_certificate(data).public_key()` / `load_der_x509_certificate` | loader | none | loaded-certificate | yes | yes | TESTED |
| C22 | `padding.PKCS1v15()`, `padding.PSS(mgf, salt_length)`, `padding.OAEP(mgf, algorithm, label)` | parameter object | disambiguates SIG vs PK_ENCRYPT only together with the method (PSS → signature family; OAEP → encryption family; PKCS1v15 → ambiguous) | — | yes (as argument pattern) | yes (argument resolver) | TESTED |
| C23 | `ec.ECDSA(hash)`, `ec.ECDH()` | parameter object | ECDSA → signature family; ECDH → key establishment | — | yes | yes | TESTED |
| C24 | `mlkem.MLKEM768PrivateKey.generate()` / `.encapsulate()` / `.decapsulate()`, `mldsa.*` (pyca ≥ 46 PQC APIs) | PQC presence | marks hybrid context | generated | yes | yes (hybrid flag) | TESTED (hybrid flag; policy NO_ACTION_HYBRID) |

## 2. PyCryptodome (`Crypto.*` / `Cryptodome.*`)

| # | API | Kind | Role evidence | Provenance | Status |
|---|---|---|---|---|---|
| D1 | `Crypto.PublicKey.RSA.generate(bits)` | keygen | none | generated | TESTED |
| D2 | `RSA.import_key(extern_key, passphrase)` / `RSA.importKey` | loader | none | loaded-PEM or loaded-DER (format resolved from the literal when possible, else `loaded-PEM-or-DER`) | TESTED |
| D3 | `RSA.construct((n, e, d, ...))` | key construct | none | loaded-JWK / parsed-blob | TESTED |
| D4 | `Crypto.PublicKey.ECC.generate(curve=)` / `ECC.import_key()` / `ECC.construct()` | keygen/loader/construct | none | generated / loaded-* | TESTED |
| D5 | `Crypto.Signature.pkcs1_15.new(key).sign(hash)` / `.verify(hash, sig)` | operation | SIGN / VERIFY | receiver (key argument of `new`) | TESTED |
| D6 | `Crypto.Signature.pss.new(key).sign()/.verify()` | operation | SIGN / VERIFY | receiver | TESTED |
| D7 | `Crypto.Signature.DSS.new(key, mode).sign()/.verify()` (ECDSA/DSA) | operation | SIGN / VERIFY | receiver | TESTED |
| D8 | `Crypto.Signature.eddsa.new(key, mode).sign()/.verify()` | operation | SIGN / VERIFY | receiver | TESTED (Semgrep fixture; signer object typed as PyCryptodome eddsa scheme) |
| D9 | `Crypto.Cipher.PKCS1_OAEP.new(key).encrypt()/.decrypt()` | operation | PK_ENCRYPT / PK_DECRYPT | receiver | TESTED |
| D10 | `Crypto.Cipher.PKCS1_v1_5.new(key).encrypt()/.decrypt()` | operation | PK_ENCRYPT / PK_DECRYPT | receiver | TESTED |
| D11 | `Crypto.Protocol.DH.key_agreement(static_priv=, static_pub=, kdf=)` | operation | KEY_ESTABLISHMENT | arguments | TESTED at detection level only (Module A); `DH.key_agreement` not modelled as an operation by Module B (gap) |
| D12 | `Crypto.PublicKey.DSA.generate()/import_key()` | keygen/loader | none | generated / loaded | TESTED (extension) |

## 3. Explicitly unsupported (reported as `unsupported` by the scanner, never silently ignored)

- Libraries: `rsa` (python-rsa), `ecdsa` (python-ecdsa), `pyOpenSSL`, `M2Crypto`, `nacl`/`PyNaCl`, `oqs`/`liboqs-python`, `pqcrypto`, `jwcrypto`, `authlib`'s own primitives, `ssl` module configuration. Occurrences of these roots are emitted as `library = out-of-scope:<name>` findings with no role or recommendation.
- Python constructs: dynamic attribute access (`getattr(key, "sign")`), `exec`/`eval`, reflection, monkey-patching, keys passed through more than one call level, cross-package flows, `*args/**kwargs` forwarding of keys, async generators.
- File types: anything that is not a `.py` file (key files, configs) are out of scope for role inference; PEM/DER key files are reported by Module A only as inventory evidence if at all (decision deferred to Phase 2; not a research claim).

## 4. Coverage evidence table (to be filled in Phase 2)

Each row above will reference its positive fixture(s), negative fixture(s) and the test IDs that exercise it; the Phase 2 gate requires a positive and a negative fixture per row with status ≥ TESTED. Rows that cannot be reached by the gate are downgraded to "unsupported" in all reports.
