# Annotation guide for PyPQC-RoleBench (v1.1 — PROPOSED, revision 3; v1.0 remains in force until owner approval)

Use with `docs/specification/role_taxonomy.md` v1.0.1 and `docs/specification/data_dictionary.md`. The decision procedure (Sec. 3) is v1.0's Steps A–G, except the scope rule. Revision 3 changes from revision 2: scope precedence; `context_used`; phase definitions; the isolated-session rule; S2 and analysis-set notes.

## 1. Who does what

| Step | Who | What | Record (ledger committed and pushed after the step) |
|---|---|---|---|
| 1 | Claude (scripted) | issues a location-only batch (opaque ID, repository, commit, file, line). B0 = 10 S2 candidates, once; B1+ = S1 batches of 10 | ledger `issue` |
| 2 | **Owner** | labels every candidate from the full repository at the pinned commit, tool outputs hidden, using Sec. 3–4; records `context_used`; the file must pass strict validation | `primary_<repo>_B<n>.jsonl`; ledger `primary` (hash) |
| 3 | **ChatGPT** (run by the owner; Sec. 6) | blind review of the same candidates in a fresh isolated session | `ai_review_<repo>_B<n>.jsonl` + export; ledger `ai_review` |
| 4 | Claude (scripted) | compares `eligible`, `gt_role`, `assessability`, `possible_roles`, `hybrid_component`, `obvious_from_name`, `evidence_needed`, `key_provenance` | `disagreements_<repo>_B<n>.csv`; ledger `compare` |
| 5 | **Owner** | decides each disagreement: final value, reason, category (`kept`, `adopted_ai`, `third_value`, `unresolved`), `context_difference` tag; agreed fields keep the owner's value | `adjudication_<repo>_B<n>.csv`; `final_<repo>.jsonl` (script); ledger `adjudication` |
| 6 | Owner | records ambiguity and guide problems | `meta.ambiguity`; adjudication notes |

The AI review is never ground truth. An AI "insufficient context" answer is `ai_status = insufficient_context`, not a disagreement.

## 2. Rules for the owner

- Never open pqscan or baseline outputs for a repository before its final labels exist. That includes `runs/` and judgment files. Never open the sealed test outputs before F2.
- Run the AI review only after the primary file's hash has been pushed.
- Label every issued candidate. Never skip or edit a submitted file; a correction is a new file with a reason.
- S2 (B0) candidates are labelled exactly like the others. They are reported separately and do not count toward quotas.
- Add any other eligible site you notice that is not in the list as `annotator_added`. It is reported separately.
- **Unresolved:** mark a field `unresolved` with a reason when it cannot be decided. An unresolved `eligible` counts as not eligible. Every unresolved case is recorded before F2.
- **Phases:** DV = development and validation together; T = test (after F1).
- **Intra-rater re-label:** per phase, n = max(50, ⌈0.10·N⌉), selected by script, at least 14 days after the latest primary label in the sample, earlier labels hidden.

## 3. Decision procedure

v1.0 Steps A–G apply unchanged, except for Step F.

**Step F, scope (v1.1, revision 3).** Classify the path relative to the repository root, applying the first class that matches in this order:

1. `vendored`: a directory `vendor`, `_vendor` or `third_party`.
2. `test`: a directory `test`, `tests` or `testing`; or a file `test_*.py`, `*_test.py`, `test.py`, `tests.py`, `tests_*.py`, `tests-*.py`, `conftest.py`.
3. `example`: a directory `example`, `examples`, `demo`, `demos` or `demo*`.
4. `app`: otherwise.

## 4. Evidence required for each label

Unchanged from revision 2 (`04_annotation_guide_v1.1_PROPOSED.md` Sec. 4): the receiver-type line is always required, plus the role-specific evidence for SIGN, VERIFY, KEY_ESTABLISHMENT, PK_ENCRYPT, PK_DECRYPT, KEY_MATERIAL_ONLY, PROTOCOL_CONFIG, UNKNOWN and NONE. Evidence is also required for `hybrid_component`, `obvious_from_name` and `evidence_needed`.

## 5. Record envelope

As in revision 2 Sec. 5, plus `meta.context_used` (`packet_sufficient` or `extended`) and `meta.context_extra` (a list of file:line ranges, when extended). The boolean fields must be JSON booleans.

## 6. AI-review rules (run by the owner)

- **Isolation:** never use the existing project conversation, or any session that has seen this project. One fresh ChatGPT Temporary Chat per batch, with custom instructions, memory and history reference, Projects, connectors, file library and browsing/search all off. Or the API with a pinned model identifier and the owner's own key.
- **Inputs:** the fixed prompt template (hash recorded), guide v1.1 Steps A–G with the field definitions, and the packet. Nothing else.
- **Identification:** the interface, the model as displayed or the API model ID, the app version if shown, and the date and time in UTC.
- **Export:** the verbatim response plus the conversation export or the API JSON.
- **Repeat-run sample:** per phase, max(30, ⌈0.10·N_AI⌉), in new sessions.

## 7. What reports may say

"Single-investigator labels with a separately conducted AI-assisted review and investigator adjudication". Never "double-annotated", "independent annotators", "inter-annotator agreement" or "independent human validation".
