# Annotation guide for PyPQC-RoleBench (v1.2)

Adopted 2026-11-16 with evaluation protocol v1.0.4 (owner decisions V1, V5, V8, V9, V16; `docs/specification/phase3_decisions.md`). The superseded v1.0 is kept in `docs/benchmark/annotation_guide_v1.0.md`. v1.2 (18 Nov 2026, before any labelling and any test-split access) applies the owner-approved pre-F1 decision register with protocol v1.0.5 (`docs/audit/owner_decision_register_v1.0.5.md`); the v1.1 text is kept in `docs/specification/archive/v1.0.4/annotation_guide.md`.

**Changes from v1.0:**
- a single investigator with a separately conducted AI-assisted review;
- the Step F scope rule;
- evidence requirements;
- the record envelope with `context_used`;
- packet-first labelling;
- the re-label procedure;
- reporting language.

**Changes in v1.2:** the multi-call candidate rule (Step A, F03); Step D consumer inheritance as in taxonomy rule 1 (F02) and escape before KEY_MATERIAL_ONLY (F21); the hybrid rule requires a matching PQ family and actual combination (Step F, F08); the unresolved-field convention (Sec. 2, F10); owner and AI example records (Sec. 5, F15); the packet-first rule as implemented (Sec. 5, F11); the forbidden-token gate (Sec. 6, F07).

**Revision r3 (19 Nov 2026; owner decisions G02 and G03; `docs/audit/owner_decisions_g02_g03_g08_g10.md`):** `obvious_from_name` is `null` on ineligible records; the four units of the multi-call rule and the `notes` format for additional same-family calls.

**Editorial revision r2 (19 Nov 2026; second review G01, G04, G11; `docs/audit/second_review_closure.md`):** the protocol-configuration branch of Step C and of the multi-call rule (kind (c) of a supported library; reserved in the current frame); the permitted frozen batch run versus manual scanner use; the tool-attribution files. No eligibility outcome changes: out-of-scope protocol configuration was already ineligible under Step A.

The decision procedure (Steps A–E and G) and the worked examples are unchanged from v1.0, except for the v1.2 changes listed above.

Use with `docs/specification/role_taxonomy.md` (definitions) and `docs/specification/data_dictionary.md` (fields). Labels are made from **source code only**; tool outputs are hidden during labelling.

## 1. Who does what

| Step | Who | What | Record (ledger committed and pushed after the step) |
|---|---|---|---|
| 1 | script | issues a location-only batch (opaque candidate ID, repository, commit, file, line). B0 = 10 S2 candidates, once; B1+ = S1 batches of 10 | ledger `issue` |
| 2 | **owner** | labels every candidate from the full repository at the pinned commit, tool outputs hidden, using Sec. 3–5; records `context_used`; the file must pass strict validation | `primary_<repo>_B<n>.jsonl`; ledger `primary` (hash) |
| 3 | **AI review** (run by the owner; Sec. 6) | blind review of the same candidates in a fresh isolated session, from the packet only | `ai_review_<repo>_B<n>.jsonl` plus export; ledger `ai_review` |
| 4 | script | compares `eligible`, `gt_role`, `assessability`, `possible_roles`, `hybrid_component`, `obvious_from_name`, `evidence_needed`, `key_provenance` | `disagreements_<repo>_B<n>.csv`; ledger `compare` |
| 5 | **owner** | decides each disagreement: final value, reason, category (`kept`, `adopted_ai`, `third_value`, `unresolved`), `context_difference` tag. Agreed fields keep the owner's value. | `adjudication_<repo>_B<n>.csv`; `final_<repo>.jsonl` (script); ledger `adjudication` |
| 6 | owner | records ambiguity and guide problems | `meta.ambiguity`; adjudication notes |

**The AI review is never ground truth.** An AI "insufficient context" answer is `ai_status = insufficient_context`, not a disagreement.

## 2. Rules for the owner

- **No tool outputs.** Never open pqscan or baseline outputs for a repository before its final labels exist. That includes `runs/` and judgment files. Never open the sealed test outputs before F2.
- **Order.** Run the AI review only after the primary file's hash has been pushed.
- **Completeness.** Label every issued candidate. Never skip or edit a submitted file; a correction is a new file with a reason.
- **S2.** S2 (B0) candidates are labelled exactly like the others. They are reported separately and do not count toward quotas.
- **Annotator-added sites.** Add any other eligible RSA/EC site you notice in the same function that is not in the list as `annotator_added`. It is reported separately.
- **Unresolved (convention stated in v1.2).** When a field cannot be decided, put its name in `meta.unresolved` and the reason in `meta.unresolved_reason` (required: the meta schema rejects an unresolved field without a reason). The site field itself keeps your provisional, schema-valid value; it is never treated as settled. An unresolved `eligible` counts as not eligible. Unresolved fields are excluded, listed and bounded as in protocol Sec. 5.6. Every unresolved case is recorded before F2.
- **Phases.** DV = development and validation together; T = test (only after F1).
- **Re-label (intra-rater).**
  - **Sample:** per phase, n = max(50, ⌈0.10·N⌉), selected by the script (seed `20261113:intra:<phase>`).
  - **Timing:** presented in a new order, no earlier than 14 days after the latest primary label in the sample. The script refuses earlier.
  - **Blinding:** earlier labels must not be consulted.
- **What the labels feed.**
  - Owner-final labels define eligibility, the expected class (`eligible`, `gt_role`, `assessability`, `hybrid_component`) and H1a (`obvious_from_name`, `evidence_needed`).
  - Tool outputs, tiers and coverage matching are never consulted while labelling.
- **No scanners (clarified in r2, G04).** Do not run, open or inspect any scanner or baseline yourself on a repository before its final labels exist (for the test split: before F2). The only permitted execution is the prescribed one: the frozen batch run (protocol Sec. 6) executes every method once and writes to a sealed directory that you do not open; its outputs are first read at the stage the protocol names (Phase DV: after the DV labels are final; test split: after F2).
- **Tool-attribution files (r2, G11).** `pool_sources_<repo>.json` records which tool found each candidate. It is kept in `benchmark/restricted/pool_sources/<split>/`, outside the candidate and annotation folders, and the annotation tool refuses to issue a batch while such a file sits in a candidate or annotation folder. Never open it before the repository's final labels exist (test split: before F2). With a single investigator this separation is **procedural and self-attested, not technically enforced**: record the access attestation (`docs/audit/source_attribution_access_attestation_TEMPLATE.md`) for each phase.
- **Hard sites.** A site whose label took > 10 minutes is flagged `hard = true`.

## 3. Decision procedure (follow in order)

**Step A — Is it a site at all?** If the matched text is any of the following, set `eligible = false`, `gt_role = NONE`, `obvious_from_name = null`, and stop:
- a comment, docstring or string literal;
- a parameter-object construction on its own (`padding.PKCS1v15()`, `ec.SECP256R1()`, `ec.ECDSA(...)`);
- a type reference (`isinstance(k, RSAPrivateKey)`);
- an out-of-scope library.

**Multi-call candidate statement (v1.2).** A candidate is one statement. When the candidate statement contains more than one call to a supported library API, the candidate's site is exactly one call expression, chosen in this order:
1. a public-key **operation** call (`sign`, `verify`, `exchange`, `encrypt`, `decrypt`) on a quantum-vulnerable key (taxonomy rule 4); otherwise
2. a **key-material** call (generate, load, derive, construct, extract) on a quantum-vulnerable algorithm; otherwise
3. a **protocol-configuration** call on a supported library's protocol object (Step C, `PROTOCOL_CONFIG`; r2, G01); otherwise the candidate has no eligible site (label it ineligible as above);
4. if several calls qualify at the same level, the first in source order (line, then column of the called name).

Calls on post-quantum algorithms (ML-KEM, ML-DSA, SLH-DSA) never become the site; they may be evidence for `hybrid_component`. Record the chosen call in `api_call`; `line_start` and `line_end` stay the statement's lines. Every other eligible call in the statement whose role family differs from the site's is added as an annotator-added site; same-family calls are listed in `notes`. Issued candidates of this kind are marked `multi_call: true`, with their calls listed by name.

**Units (r3, owner decision G03; the F03 rule is retained).** The *candidate-discovery unit* is a statement location (the pool's union, deduplicated by enclosing statement). The *sampling unit* is that candidate statement (seeded order; quotas count eligible candidates). The *primary annotated site* is exactly one call expression per candidate, selected by steps 1–4 above. The *analysis unit* is that primary site: one per eligible candidate, so every denominator and estimand is unchanged. Additional same-family supported calls in the statement are not sites: list each in `notes` as `also-call: <api_call> @<line>:<column>` (name and position only, no label). Additional eligible calls of a different role family are annotator-added sites (reported separately, never in the primary set). Impact bound: at most 8 of the 3,503 development/validation pool candidates contain more than one supported call (`docs/audit/evidence/f03_multicall_pool.json`); the primary sample is never expanded retrospectively.

**Step B — Identify the API.**
- Resolve the import chain to the fully qualified API (follow `import x as y`, `from a.b import c`).
- Record `library`, `algorithm`, `api_call`, `method` and `arguments`.
- If the receiver's library cannot be determined (for example `key.sign(...)` on an untyped parameter), record `library = unknown` and continue. Eligibility stays true only if the file imports a supported library and no other candidate library.

**Step C — Operation or key material?**
- **Operation.** `sign`, `verify`, `exchange`, `encrypt`, `decrypt`, and PyCryptodome `pkcs1_15/pss/DSS/eddsa/PKCS1_OAEP/PKCS1_v1_5 .new(...).sign/verify/encrypt/decrypt`.
  - The role follows the method: `SIGN`, `VERIFY`, `KEY_ESTABLISHMENT`, `PK_ENCRYPT` or `PK_DECRYPT`.
  - Check that the receiver is a public-key object, not an AEAD cipher, HMAC or JOSE wrapper object.
  - For pyca `encrypt`/`decrypt` on an RSA key object → `PK_ENCRYPT`/`PK_DECRYPT`; on a `Cipher`/`AESGCM` object → `eligible = false`.
- **Key material** (generate / load / derive / construct): go to Step D.
- **Protocol configuration (r2, G01).** A call that configures a protocol object *of a supported library* with public-key algorithm choices (taxonomy kind (c)) → `PROTOCOL_CONFIG`, `eligible = true`. Evidence: the configuration call, the line that shows the object belongs to a supported library, and the algorithm list or option it sets. The supported libraries in their pinned versions (pyca/cryptography 47.0.0, PyCryptodome) expose no such protocol objects, so this branch is reserved and not expected to occur in the current frame. Protocol configuration in a library outside the supported list (for example `ssl.SSLContext.set_ciphers`, paramiko `Transport(disabled_algorithms=...)` or `get_security_options()`, a JOSE library's own algorithm registry) is an out-of-scope library (Step A): `eligible = false`.

**Step D — Follow the key (bounded).** Trace the produced key object through:
- assignments in the same function;
- the return value to the direct caller (one level);
- attribute assignments (`self.key = ...`) and uses of that attribute in the same class;
- arguments passed to one callee.

Collect the set of operation consumers, then decide:
- **All consumers in one family** → that family's role, as in taxonomy rule 1 (v1.2): a **private** key whose consumers are sign and/or verify, at least one of them sign → `SIGN` (secondary `VERIFY`); a **public** key whose consumers are all verify → `VERIFY`; exchange → `KEY_ESTABLISHMENT`; encrypt → `PK_ENCRYPT`; decrypt → `PK_DECRYPT`. Only consumers that can succeed for the key's type count (a public key cannot sign or decrypt). Record the other members in `secondary_roles`.
- **Two families, selected by a static constant in the same class or module** → label the role that constant selects, and note it.
- **Two families, selected by a runtime value** (an `algorithm` argument, configuration, a dispatch dict keyed by user input) → `gt_role = UNKNOWN`, `assessability = INDETERMINATE`, and fill `possible_roles`.
- **The key escapes the bounded scope** (returned beyond the direct caller, stored in a module-level or global variable or registry, serialized or pickled, or passed to code outside the analysed scope) → `UNKNOWN` / `INDETERMINATE`, with `possible_roles = [all]` and a note. **An observed escape takes precedence over `KEY_MATERIAL_ONLY` (v1.2).**
- **No consumer within the bounded scope, and no escape** → `KEY_MATERIAL_ONLY` (`DETERMINATE`). Every use inside the scope must be a non-operation (export, fingerprint, `isinstance`, storage in a local or in an attribute of the same class), and nothing may leave the scope.

**Step E — Provenance.** For the receiver of an operation, record the proximate provenance (`attribute`, `parameter`, or a local from a loader/generator). If it is resolvable within the bounded scope, also record the `ultimate_provenance` set.

**Step F — Flags (v1.1).**
- **`hybrid_component = true`** only if both hold (v1.2), with the lines as evidence: (1) an approved post-quantum component **of the matching family** is present — ML-KEM for `KEY_ESTABLISHMENT`; ML-DSA or SLH-DSA for `SIGN` and `VERIFY` (pyca `mlkem`/`mldsa`, `oqs`, `pqcrypto`); and (2) the site's output is **actually combined** with it within the bounded scope of Step D: both shared secrets enter one key derivation or combiner (for example a hash of their concatenation), or both signatures are produced over, or verified against, the same message and used together. Being in the same class or function alone is not enough: then `hybrid_component = false`, with a note.
- **`scope`:** classify the path relative to the repository root, applying the first class that matches in this order:
  1. `vendored`: a directory `vendor`, `_vendor` or `third_party`;
  2. `test`: a directory `test`, `tests` or `testing`; or a file `test_*.py`, `*_test.py`, `test.py`, `tests.py`, `tests_*.py`, `tests-*.py`, `conftest.py`;
  3. `example`: a directory `example`, `examples`, `demo`, `demos` or `demo*`;
  4. `app`: otherwise.

**Step G — Difficulty fields.**
- `obvious_from_name`: `true` only if Step C decided the role without Step D, or the algorithm is single-purpose (X25519/X448 → key establishment; Ed25519/Ed448 → signature).
- `evidence_needed` and `evidence_scope`: per the taxonomy.

## 4. Evidence required for each label

Every eligible label lists `evidence_lines` (file:line), including the line that **establishes the receiver's type**: key creation, loading, annotation, isinstance or attribute assignment.

| Label | Required evidence | Not sufficient on its own |
|---|---|---|
| **SIGN** | **Operation:** a signing call: pyca `.sign(...)` on an RSA/EC/Ed25519/Ed448 private key, or PyCryptodome `pkcs1_15/pss/DSS/eddsa.new(key).sign(...)`.<br>**Key site:** the creation or load line, plus every consumer within the bounded scope (Step D). All consumers are sign or verify, and at least one is sign. | the `.sign(` name alone (HMAC, JOSE and token objects have it); the algorithm name alone |
| **VERIFY** | **Operation:** verification on a public key (pyca `.verify(...)`; PyCryptodome `...new(pubkey).verify(...)`).<br>**Key site:** a public key whose only consumers are verify. | `verify` on a non-key object |
| **KEY_ESTABLISHMENT** | **Operation:** an `exchange(...)` call (ECDH with `ec.ECDH()`, X25519, X448, DH), with the peer argument identified.<br>**Key site:** every consumer is exchange. | the curve name or a "kex" substring |
| **PK_ENCRYPT** | encryption with an RSA public key (pyca `.encrypt(data, padding)`; PyCryptodome `PKCS1_OAEP` / `PKCS1_v1_5` cipher `.encrypt`); the receiver shown to be a key, not an AEAD or Fernet object | `encrypt` on any object; the padding constant alone |
| **PK_DECRYPT** | decryption with an RSA private key; the receiver shown to be a key | as for PK_ENCRYPT |
| **KEY_MATERIAL_ONLY** | the creation or load line, plus the list of every use examined within the bounded scope (export, fingerprint, storage, isinstance, return with no consumer at the direct caller) and the boundary reached | "no consumer found" without the list |
| **PROTOCOL_CONFIG** | a configuration call on a protocol library object (TLS/SSH context, KEX or cipher list, JOSE `alg` registry) | a protocol-library import alone |
| **UNKNOWN** | the runtime value, dynamic dispatch, reflection or out-of-scope flow that prevents fixing the role (with its line), plus `possible_roles` with at least one evidence line per family; `assessability = INDETERMINATE` | the annotator's own uncertainty (use `meta.ambiguity`) |
| **NONE** (ineligible) | the Step A category (comment, docstring, string, parameter or padding object alone, type reference, out-of-scope library, symmetric or hash primitive, unrelated method on a non-key object), with the line that shows it | — |

## 5. Record envelope and context

One JSON object per line. An **owner primary** record (v1.2: separate examples, each with `label_kind`):

```json
{"site": { ...fields of docs/benchmark/benchmark_schema.json, validated unchanged... },
 "meta": {"candidate_id": "C-…", "annotator": "owner", "label_kind": "primary", "submitted_utc": "…",
          "evidence_lines": ["file:line", …], "rationale": "…", "confidence": 1,
          "ambiguity": "none | guide_unclear | context_insufficient | unresolved",
          "hard": false, "time_seconds": 0,
          "context_used": "packet_sufficient | extended", "context_extra": ["file:start-end", …]}}
```

An **AI-review** record, written by the script from the verbatim response (`site` holds only `site_id` and the 8 compared fields):

```json
{"site": {"site_id": "C-…", ...the 8 compared fields... },
 "meta": {"candidate_id": "C-…", "annotator": "ai_review", "label_kind": "ai_review", "submitted_utc": "…",
          "evidence_lines": ["file:line", …], "rationale": "…", "ambiguity": "…",
          "ai": {"interface_or_api": "…", "model": "…", "datetime_utc": "…", "prompt_sha256": "…",
                 "packet_sha256": "…", "status": "ok | insufficient_context"}}}
```

Other `label_kind` values: `packet_first` and `relabel` (owner), `final` (written by the script after adjudication).

**Type rules:**
- `site.eligible` and `site.hybrid_component` must be JSON booleans. `site.obvious_from_name` is a JSON boolean on an eligible record and `null` (not applicable) on an ineligible record (r3, owner decision G02; schema v1.1). Anything else is rejected, never coerced.
- `meta.ai` is present only for AI-review records.

**`context_used`.** It is set while labelling and cannot be changed after the primary file is hashed:
- `packet_sufficient`: every one of the 8 compared fields was decided from lines inside the packet the packet builder generated for this candidate. Open the packet file, not only the repository.
- `extended`: anything else. Every extra file:line range goes in `context_extra`.

**Packet-first subset.** For candidates the script flags `packet_first = true` (seeded; rate max(10%, 60 / planned candidates) per phase: 12.8% for DV, 10% for T; ≥ 50 is an expected count, and the realised count is reported):
1. First record a P-label from the packet only, in `primary_packet_<repo>_B<n>.jsonl`. It is validated, hashed and pushed.
2. Then record the normal primary label (the F-label), which may use more context.

Never edit the P-label afterwards.

## 6. AI-review rules (run by the owner)

- **Identification first.** Before the first review, the owner records the interface and the model identity as displayed (or the API model identifier) in `docs/benchmark/ai_review_identity.json`, which the tool validates; each AI-review ledger entry records its SHA-256.
- **Isolation.** Never use the existing project conversation, or any session that has seen this project. Use one fresh ChatGPT Temporary Chat per batch, with these all off: custom instructions, memory and chat-history reference, Projects, connectors, file library, and browsing/search. Alternatively, use the API with a pinned model identifier and the owner's own key; Claude never handles it.
- **Inputs.** The fixed prompt template (hash recorded), guide v1.2 Steps A–G with the field definitions, and the packet. Nothing else: no owner label, tool output, project name or hypotheses.
- **Per-review identification:** the interface; the model as displayed or the API model ID; the app version if shown; the date and time in UTC.
- **Export:** the verbatim response plus the conversation export or the API JSON.
- **Forbidden tokens (v1.2).** If a packet contains a forbidden token (a tool name, the project's name or a hypothesis label; `packets.FORBIDDEN`), the prompt step refuses the batch until you record, for every (candidate, token), a decision in a CSV with columns `candidate_id,token,verdict,evidence`: `genuine` → the candidate is **excluded** from the AI review (it is still labelled by you and reported as not AI-reviewed), and no reason can override this; `false_positive` → allowed only with evidence (file:line, and why the match does not refer to an evaluated tool, this project or its hypotheses). The decision file's SHA-256 is recorded in the ledger. Nothing is redacted.
- **Repeat-run sample:** per phase, max(30, ⌈0.10·N_AI⌉) (seed `20261113:airepeat:<phase>`), in new sessions.

## 7. Worked examples (from the pilot, `docs/pilot/h1_pilot_sites.csv`)

- **paramiko `kex_ecdh_nist.py:59`** `self.P = ec.generate_private_key(self.curve)`. The consumer is `self.P.exchange(ec.ECDH(), …)` in two other methods of the same class → `KEY_ESTABLISHMENT`, provenance `generated`, `obvious_from_name = false`, scope `cross-function`.
- **paramiko `pkey.py:195`** `serialization.load_ssh_private_key(...)`. The loaded object is only used in `isinstance` checks, and the signing key is re-loaded elsewhere → `KEY_MATERIAL_ONLY`.
- **python-jose `cryptography_backend.py:252`** `load_pem_private_key` inside `CryptographyRSAKey`. The consumers `sign` (RS*) and `decrypt` (RSA-OAEP unwrap) are selected by the runtime `algorithm` argument → `UNKNOWN`, `INDETERMINATE`, `possible_roles = [SIGN, VERIFY, PK_DECRYPT]`.
- **python-jose `cryptography_backend.py:208`** `RSA1_5 = padding.PKCS1v15()` → `eligible = false`.
- **paramiko `kex_mlkem.py:112`** X25519 `exchange`; the secret is returned to its caller in the same class and combined with the ML-KEM secret as SHA-256(K_PQ ‖ K_CL) (lines 139–141 and 193–194) → `KEY_ESTABLISHMENT`, `hybrid_component = true`.

These five worked examples are pilot sites. In the pilot loop they form a separately reported subset, and their agreement is never counted as blind evidence (owner decision, 18 Nov 2026).

## 8. What reports may say

"Single-investigator labels with a separately conducted AI-assisted review and investigator adjudication".

Never:
- "double-annotated";
- "independent annotators";
- "inter-annotator agreement";
- "independent human validation".
