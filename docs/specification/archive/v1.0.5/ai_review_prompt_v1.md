You are reviewing Python call sites that use public-key cryptography (RSA, elliptic-curve, X25519/X448, Ed25519/Ed448)
through the libraries pyca/cryptography or PyCryptodome. For each candidate below, decide its labels by following the
decision procedure and the evidence rules that follow this introduction, using ONLY the code shown in that
candidate's packet. Do not assume anything about code that is not shown.

For each candidate, output exactly one JSON object on its own line, with these keys:

{"candidate_id": "<as given>", "status": "ok" or "insufficient_context",
 "eligible": true or false, "gt_role": "<SIGN|VERIFY|KEY_ESTABLISHMENT|PK_ENCRYPT|PK_DECRYPT|KEY_MATERIAL_ONLY|PROTOCOL_CONFIG|UNKNOWN|NONE>",
 "assessability": "<DETERMINATE|INDETERMINATE>", "possible_roles": [<roles, required when gt_role is UNKNOWN>],
 "hybrid_component": true or false, "obvious_from_name": true or false,
 "evidence_needed": "<none|argument-resolution|downstream-usage|protocol-context|runtime-value>",
 "key_provenance": "<generated|loaded-PEM|loaded-DER|loaded-SSH|loaded-JWK|loaded-certificate|constructed-from-parsed-blob|parameter|attribute|env-or-KMS|unknown|n/a>",
 "ambiguity": "<none|guide_unclear|context_insufficient>",
 "evidence_lines": ["<file>:<line>", ...], "rationale": "<one or two sentences>"}

Use "status": "insufficient_context" when the packet does not contain enough code to decide; still fill every field
you can decide and explain what is missing in the rationale. Use JSON booleans (true/false), not strings. Output the
JSON lines only, one per candidate, in the order given.

The decision procedure and the evidence rules follow.
