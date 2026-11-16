# Annotation guide for PyPQC-RoleBench (v1.1 — PROPOSED, revision 2; v1.0 remains in force until owner approval)

Use with `docs/specification/role_taxonomy.md` v1.0.1 and `docs/specification/data_dictionary.md`. The decision procedure in Sec. 3 is v1.0's Steps A–G, unchanged except for the scope rule. New in v1.1: the process (Sec. 1–2), per-role evidence (Sec. 4), the record envelope (Sec. 5) and the AI-review rules (Sec. 6).

## 1. Who does what

| Step | Who | What | Record (ledger committed and pushed after the step) |
|---|---|---|---|
| 1 | Claude (scripted) | issues a batch of location-only candidates (opaque ID, repository, commit, file, line) | ledger `issue` entry |
| 2 | **Owner** | labels every candidate from source at the pinned commit, tool outputs hidden, using Sec. 3–4. The file must pass strict validation before it is hashed | `primary_<repo>_B<n>.jsonl`; ledger `primary` entry (hash) |
| 3 | **ChatGPT** (run by the owner, Sec. 6) | separate blind review of the same candidates | `ai_review_<repo>_B<n>.jsonl` + exported conversation; ledger `ai_review` entry |
| 4 | Claude (scripted) | field-by-field comparison: `eligible`, `gt_role`, `assessability`, `possible_roles`, `hybrid_component`, `obvious_from_name`, `evidence_needed`, `key_provenance` | `disagreements_<repo>_B<n>.csv`; ledger `compare` entry |
| 5 | **Owner** | decides every disagreement: final value, reason, category (`kept`, `adopted_ai`, `third_value`, `unresolved`), plus a `context_difference` tag where the AI's excerpt caused it. Agreed fields keep the owner's value | `adjudication_<repo>_B<n>.csv`; `final_<repo>.jsonl` derived by script; ledger `adjudication` entry |
| 6 | Owner | records ambiguity and guide problems | the `meta.ambiguity` field and the adjudication notes |

The AI review is never ground truth. "Insufficient context" from the AI is recorded as `ai_status = insufficient_context` and is not counted as a role disagreement.

## 2. Rules for the owner

- Before the final labels of a repository exist, do not open pqscan or baseline outputs for it. That includes `runs/` and any judgment file. Never open the sealed test outputs before F2.
- Run the AI review only after the primary file's hash has been committed and pushed.
- Label every issued candidate. Never skip one, and never edit a submitted file. A correction is a new file with a reason.
- Budget about 1 minute for clearly ineligible candidates and 2–4 minutes for eligible ones (assumed). Flag `hard = true` above 10 minutes.
- A second site in the same statement, or elsewhere in the function, that is not in the list is added as `annotator_added`.
- **Unresolved:** if, after adjudication, a field still cannot be decided, mark it `unresolved` with a reason.
  - An unresolved `eligible` counts as not eligible for the quota.
  - Every unresolved case must be recorded before F2.
- **Intra-rater re-label:** a seeded sample of at least 50 candidates per phase (or 10%, if larger), at least 14 days after the first label, labelled without looking at the earlier label.

## 3. Decision procedure

v1.0 Steps A–G apply unchanged, with this replacement for the scope rule in Step F:

**Step F, scope (v1.1).**
- `test`: a directory named `test`, `tests` or `testing`, or a file named `test_*.py`, `*_test.py`, `test.py`, `tests.py`, `tests_*.py`, `tests-*.py` or `conftest.py`;
- `vendored`: under `vendor/`, `_vendor/` or `third_party/`;
- `example`: under `examples/` or `demo*/`;
- otherwise `app`.

## 4. Evidence required for each label

Every eligible label lists `evidence_lines` (file:line), including the line that **establishes the receiver's type**: key creation, loading, annotation, isinstance or attribute assignment.

| Label | Required evidence | Not sufficient on its own |
|---|---|---|
| **SIGN** | **Operation:** a signing call — pyca `.sign(...)` on an RSA/EC/Ed25519/Ed448 private key, or PyCryptodome `pkcs1_15/pss/DSS/eddsa.new(key).sign(...)`.<br>**Key site:** the creation or load line, plus every consumer within the bounded scope (Step D). All consumers are sign or verify, and at least one is sign. | the `.sign(` name alone (HMAC, JOSE and token objects have it); the algorithm name alone |
| **VERIFY** | **Operation:** verification on a public key (pyca `.verify(...)`; PyCryptodome `...new(pubkey).verify(...)`).<br>**Key site:** a public key whose only consumers are verify. | `verify` on a non-key object |
| **KEY_ESTABLISHMENT** | **Operation:** an `exchange(...)` call (ECDH with `ec.ECDH()`, X25519, X448, DH), with the peer argument identified.<br>**Key site:** every consumer is exchange. | the curve name or a "kex" substring |
| **PK_ENCRYPT** | encryption with an RSA public key (pyca `.encrypt(data, padding)`; PyCryptodome `PKCS1_OAEP` / `PKCS1_v1_5` cipher `.encrypt`); the receiver shown to be a key, not an AEAD or Fernet object | `encrypt` on any object; the padding constant alone |
| **PK_DECRYPT** | decryption with an RSA private key; the receiver shown to be a key | as for PK_ENCRYPT |
| **KEY_MATERIAL_ONLY** | the creation or load line, plus the list of every use examined within the bounded scope (export, fingerprint, storage, isinstance, return with no consumer at the direct caller) and the boundary reached | "no consumer found" without the list |
| **PROTOCOL_CONFIG** | a configuration call on a protocol library object (TLS/SSH context, KEX or cipher list, JOSE `alg` registry) | a protocol-library import alone |
| **UNKNOWN** | the runtime value, dynamic dispatch, reflection or out-of-scope flow that prevents fixing the role (with its line), plus `possible_roles` with at least one evidence line per family; `assessability = INDETERMINATE` | the annotator's own uncertainty (use `meta.ambiguity`) |
| **NONE** (ineligible) | the Step A category (comment, docstring, string, parameter or padding object alone, type reference, out-of-scope library, symmetric or hash primitive, unrelated method on a non-key object), with the line that shows it | — |

**Fields beyond the role, with their evidence:**
- `hybrid_component = true` only with the line(s) showing the matching-family PQ result combined with this site's secret or signature.
- `obvious_from_name` per taxonomy Sec. 4.
- `evidence_needed` naming the evidence kind actually used.

## 5. Record envelope

One JSON object per line:

```json
{"site": { ...fields of docs/benchmark/benchmark_schema.json, validated unchanged... },
 "meta": {"candidate_id": "C-…", "annotator": "owner | ai_review", "submitted_utc": "…",
          "evidence_lines": ["file:line", …], "rationale": "…", "confidence": 1, "ambiguity": "none | guide_unclear | context_insufficient | unresolved",
          "hard": false, "time_seconds": 0,
          "ai": {"interface_or_api": "…", "model": "…", "datetime_utc": "…", "prompt_sha256": "…", "packet_sha256": "…", "status": "ok | insufficient_context"}}}
```

`site.eligible`, `site.hybrid_component` and `site.obvious_from_name` must be JSON booleans; anything else is rejected, never coerced. `meta.ai` is present only for AI-review records.

## 6. AI-review rules (run by the owner)

- **Session:** ChatGPT Temporary Chat, with custom instructions, chat-history reference, Projects, connectors and web browsing/search off. Or the API with a pinned model identifier, using the owner's own credentials.
- **Batching:** one new session per batch.
- **Content:** the fixed prompt template and the packet only. Never the project's name, pqscan, tool names, hypotheses, results or the owner's labels.
- **Saving:** the verbatim response and the exported conversation, with timestamps.
- **Self-consistency:** a seeded 10% (at least 30) per phase is reviewed again in new sessions.

## 7. Worked examples

Unchanged from v1.0, with the evidence lines v1.1 requires.

## 8. What reports may say

"Single-investigator labels with a blind AI-assisted review and investigator adjudication". Never "double-annotated", "independent annotators" or "inter-annotator agreement".
