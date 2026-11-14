# Specification review form

Reviewer ID: ______  Date: ______  Background (one line): ______
Conflict of interest (relationship to the build team, if any): ______

Answer every question. For each issue give the document, the section and a concrete suggestion.

## A. Role taxonomy v1.0.1 (`docs/specification/role_taxonomy.md`)

1. Are the nine roles (SIGN, VERIFY, KEY_ESTABLISHMENT, PK_ENCRYPT, PK_DECRYPT, KEY_MATERIAL_ONLY, PROTOCOL_CONFIG, UNKNOWN, NONE) complete and mutually exclusive for RSA/EC/X25519/Ed25519 call sites in Python?
2. Is the type-valid consumer rule (rule 1) correct, so that a key's role follows only from operations its algorithm and key half can perform?
3. Is it acceptable that a key with consumers in two role families, selected at runtime, is UNKNOWN / INDETERMINATE?
4. Is KEY_MATERIAL_ONLY right for a key with no consumer in the bounded scope, for example a capability probe whose result is discarded?
5. Are the evidence tiers T0–T3 (`data_dictionary.md` Sec. 3) clear enough to apply consistently?

Issues: ______
Verdict: APPROVED / APPROVED WITH CHANGES / CHANGES REQUIRED

## B. Recommendation policy v1.1 (`docs/specification/recommendation_policy.md`, `pqscan/policy/policy_v1_1.yaml`)

1. SIGN/VERIFY → ML-DSA (FIPS 204): correct direction?
2. KEY_ESTABLISHMENT → ML-KEM (FIPS 203) as a key-establishment redesign (SP 800-227), not a drop-in: correct?
3. PK_ENCRYPT/PK_DECRYPT → KEM + KDF + AEAD redesign, never a drop-in: correct?
4. Is the approved-hybrid exception (no action when the classical secret is demonstrably combined with a matching-family PQ result) acceptable? Is the restriction to data combination, not combiner security, stated clearly enough?
5. Is abstention below τ = T2 a reasonable default?
6. Is any recommendation text misleading or overconfident?

Issues: ______
Verdict: APPROVED / APPROVED WITH CHANGES / CHANGES REQUIRED

## C. Scoring policy v1.0 (`docs/specification/scoring_policy.md`)

1. Are the judgment categories (CORRECT, INCORRECT with harm types, UNDECIDED, UNJUSTIFIED, UNASSESSABLE, MISSED, DETECTED_ONLY, FALSE_POSITIVE_SITE, N/A, EXECUTION_FAILURE) well defined and mutually exclusive?
2. Are the harm types (ROLE_INCOMPATIBLE, FALSE_ASSURANCE, OVER_RECOMMENDATION; strict: UNSUPPORTED_DROP_IN) appropriate?
3. Is the handling of indeterminate sites (abstention counts as correct) and unassessable outcomes fair to all methods?
4. Is excluding execution failures from rate denominators (and reporting them separately) fair?

Issues: ______
Verdict: APPROVED / APPROVED WITH CHANGES / CHANGES REQUIRED

## Response by the build team (one entry per issue)

| Issue | Response | Changed document and version |
|---|---|---|

## Reviewer sign-off of the responses

Accepted / not accepted: ______  Date: ______
