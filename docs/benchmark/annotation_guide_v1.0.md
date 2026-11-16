# Annotation guide for PyPQC-RoleBench (v1.0) — SUPERSEDED by v1.1 on 2026-11-16; kept unchanged as the historical record

Use with `docs/specification/role_taxonomy.md` (definitions) and `docs/specification/data_dictionary.md` (fields). Annotators label from **source code only**; tool outputs are hidden during labelling.

## 1. Setup

1. Open the repository at the frozen commit from `benchmark/real/manifest.json`.
2. Open the candidate list for your assignment (`labels/<you>/todo.jsonl`): each candidate has `file`, `line_start`, `line_end`, `api_call`.
3. Budget ≈ 2–4 minutes per site; record `time_seconds`.

## 2. Decision procedure (follow in order)

**Step A — Is it a site at all?** If the matched text is a comment, docstring, string literal, parameter-object construction (`padding.PKCS1v15()`, `ec.SECP256R1()`, `ec.ECDSA(...)` on its own), type reference (`isinstance(k, RSAPrivateKey)`), or an out-of-scope library → `eligible = false`, `gt_role = NONE`, stop.

**Step B — Identify the API.** Resolve the import chain to the fully qualified API (follow `import x as y`, `from a.b import c`). Record `library`, `algorithm`, `api_call`, `method`, `arguments`. If the receiver's library cannot be determined (e.g. `key.sign(...)` on an untyped parameter), record `library = unknown` and continue; eligibility stays true only if the file imports a supported library and no other candidate library.

**Step C — Operation or key material?**
- Operation (`sign`, `verify`, `exchange`, `encrypt`, `decrypt`, PyCryptodome `pkcs1_15/pss/DSS/eddsa/PKCS1_OAEP/PKCS1_v1_5 .new(...).sign/verify/encrypt/decrypt`) → the role follows the method: `SIGN`, `VERIFY`, `KEY_ESTABLISHMENT`, `PK_ENCRYPT`, `PK_DECRYPT`. Check the receiver is a public-key object (not an AEAD cipher, HMAC or JOSE wrapper object). For pyca `encrypt/decrypt` on an RSA key object → `PK_ENCRYPT/PK_DECRYPT`; on a `Cipher`/`AESGCM` object → `eligible = false`.
- Key material (generate / load / derive / construct) → go to Step D.

**Step D — Follow the key (bounded).** Trace the produced key object through: assignments in the same function; return value to the direct caller (one level); attribute assignments (`self.key = ...`) and uses of that attribute in the same class; arguments passed to one callee. Collect the set of operation consumers.
- All consumers in one family → that family's role (`SIGN` when consumers are sign and/or verify; `KEY_ESTABLISHMENT`; `PK_ENCRYPT`/`PK_DECRYPT`). Record the other members in `secondary_roles`.
- Consumers in two families, selected by a static constant in the same class/module → label the role that constant selects, and note it.
- Consumers in two families, selected by a runtime value (an `algorithm` argument, config, dispatch dict keyed by user input) → `gt_role = UNKNOWN`, `assessability = INDETERMINATE`, fill `possible_roles`.
- No consumer within the bounded scope → `KEY_MATERIAL_ONLY` (`DETERMINATE`).
- Key leaves the scope (returned two levels up, stored in a global registry, pickled) → `UNKNOWN`/`INDETERMINATE` with `possible_roles = [all]` and a note.

**Step E — Provenance.** For the receiver of an operation, record the proximate provenance (`attribute`, `parameter`, a local from a loader/generator) and, if resolvable within the bounded scope, the `ultimate_provenance` set.

**Step F — Flags.** `hybrid_component = true` only if the same class/function combines the site with an ML-KEM/ML-DSA call (pyca `mlkem`/`mldsa`, `oqs`, `pqcrypto`). `scope`: `test` if the path contains a test directory or filename pattern `test_*.py`/`*_test.py`; `vendored` if under `vendor/`, `_vendor/`, `third_party/`; `example` if under `examples/`/`demo*/`; else `app`.

**Step G — Difficulty fields.** `obvious_from_name`: `yes` only if Step C decided the role without Step D, or the algorithm is single-purpose (X25519/X448 → key establishment; Ed25519/Ed448 → signature). `evidence_needed` and `evidence_scope` per the taxonomy.

## 3. Worked examples (from the pilot, `docs/pilot/h1_pilot_sites.csv`)

- paramiko `kex_ecdh_nist.py:59` `self.P = ec.generate_private_key(self.curve)`: consumer `self.P.exchange(ec.ECDH(), …)` in two other methods of the same class → `KEY_ESTABLISHMENT`, provenance `generated`, `obvious_from_name = no`, scope `cross-function`.
- paramiko `pkey.py:195` `serialization.load_ssh_private_key(...)`: the loaded object is only used in `isinstance` checks; the signing key is re-loaded elsewhere → `KEY_MATERIAL_ONLY`.
- python-jose `cryptography_backend.py:252` `load_pem_private_key` inside `CryptographyRSAKey`: consumers `sign` (RS*) and `decrypt` (RSA-OAEP unwrap) selected by the runtime `algorithm` argument → `UNKNOWN`, `INDETERMINATE`, `possible_roles = [SIGN, VERIFY, PK_DECRYPT]`.
- python-jose `cryptography_backend.py:208` `RSA1_5 = padding.PKCS1v15()` → `eligible = false`.
- paramiko `kex_mlkem.py:112` X25519 `exchange` next to `MLKEM768PrivateKey` → `KEY_ESTABLISHMENT`, `hybrid_component = true`.

## 4. Quality control

- Two annotators per site; labels compared on `gt_role`, `assessability`, `key_provenance`, `eligible`; κ computed per field.
- Disagreements go to an adjudicator with both justifications; the adjudicated label is final and the reason is stored.
- Annotators must not run any scanner on the repository before labelling.
- A site whose label took > 10 minutes is flagged `hard = true` for the difficulty analysis.
