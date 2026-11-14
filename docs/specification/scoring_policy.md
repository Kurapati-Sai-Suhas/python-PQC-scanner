# Recommendation scoring policy (v1.0, FROZEN 2026-11-14, before any held-out evaluation)

Project: Post-quantum crypto scanner for Python projects. Base paper DOI 10.1145/3774748.3795653.

This document freezes how every method (external tools, simple baselines, pqscan arms) is judged at each benchmark site. It consolidates `recommendation_policy.md` v1.1 Section 5, the review-round decisions of Phase 2, and the open strict-scoring decision. Implementation: `pqscan/bench/judge.py` (`judge`, `strict_judgment`, `dropin_wording`, `classify_text`) and `pqscan/bench/run.py`. Changing anything here after test-split results have been viewed is not allowed. A change before that requires a new version and a dated changelog entry.

## 1. Separate dimensions per site and method

| Dimension | Values | Source |
|---|---|---|
| Ground-truth role | SIGN, VERIFY, KEY_ESTABLISHMENT, PK_ENCRYPT, PK_DECRYPT, KEY_MATERIAL_ONLY, PROTOCOL_CONFIG, UNKNOWN, NONE (ineligible) | adjudicated human labels |
| Assessability | DETERMINATE, INDETERMINATE | adjudicated human labels |
| Expected class | SIG, KEM (KEM and KEM_DEM are one family), NONE (inventory, approved hybrid, protocol review), ABSTAIN (indeterminate), N/A (ineligible) | derived from the two rows above by the frozen role → class table |
| Method action | RECOMMEND, FLAG_NO_TARGET, ABSTAIN, NO_FINDING, EXECUTION_FAILURE | method output via adapters |
| Recommended class | SIG, KEM, DUAL, PQC_ALREADY, NONE | `classify_text` on the method's text (negated mentions removed token by token) |
| Judgment (primary) | see Section 2 | `judge` |
| Harm category | ROLE_INCOMPATIBLE, FALSE_ASSURANCE, OVER_RECOMMENDATION, UNSUPPORTED_DROP_IN (strict only), OTHER (unused so far) | `judge`, `strict_judgment` |
| Drop-in wording flag | true / false | `dropin_wording` on the method's text; negated phrases do not count |

## 2. Primary judgment (policy v1.1 Section 5)

| Condition | Judgment | Harm |
|---|---|---|
| Method failed on the file (missing report, file the tool is measured to drop, file in the tool's own error log) | EXECUTION_FAILURE | — |
| Ineligible site, nothing reported | N/A | — |
| Ineligible site, anything reported (an abstention included) | FALSE_POSITIVE_SITE (detection level) | — |
| Eligible site, nothing reported | MISSED | — |
| ABSTAIN on an INDETERMINATE site | CORRECT | — |
| ABSTAIN on a DETERMINATE site | UNASSESSABLE (not correct, not harmful; lowers coverage) | — |
| FLAG_NO_TARGET where expected NONE | CORRECT | — |
| FLAG_NO_TARGET elsewhere | DETECTED_ONLY | — |
| RECOMMEND of the expected family | CORRECT | — |
| RECOMMEND of the other family (KEM for SIGN/VERIFY; SIG for KE/PK_*) | INCORRECT | ROLE_INCOMPATIBLE |
| RECOMMEND "already PQC" on a quantum-vulnerable non-hybrid site | INCORRECT | FALSE_ASSURANCE |
| RECOMMEND SIG/KEM where expected NONE (inventory, approved hybrid) | INCORRECT | OVER_RECOMMENDATION |
| RECOMMEND DUAL on a DETERMINATE site, or on an INDETERMINATE site | UNDECIDED | — |
| RECOMMEND a single target on an INDETERMINATE site | UNJUSTIFIED | — |

"Harmful" always means INCORRECT with a harm category. UNDECIDED, UNJUSTIFIED and UNASSESSABLE are reported separately and never folded into "harmful".

## 3. Strict sensitivity analysis (resolves open decision C2)

Pre-registered and reported in every results table next to the primary score, never instead of it:

- A primary CORRECT on a site whose expected family is KEM (key establishment or public-key encryption/decryption), where the method's text implies a direct substitution ("replace RSA with ML-KEM", "drop-in", "swap", "replaces … entirely/directly"), becomes **INCORRECT with harm UNSUPPORTED_DROP_IN**.
- Negated phrases ("no drop-in replacement", "not a drop-in") never trigger it.
- All other judgments are identical to the primary scoring.

Rationale: ML-KEM is a KEM, not a public-key encryption scheme. SP 800-227 describes key transport with a KEM only through the KEM/DEM construction, so "replace RSA encryption with ML-KEM" is unsafe advice even though the family is right. The primary scoring keeps the pre-registered v1.1 definition of harm (family incompatibility). The strict scoring tests whether conclusions change when unsafe wording also counts as harm.

## 4. Indeterminate and unassessable examples

- A site is INDETERMINATE when its role depends on a runtime value, dynamic dispatch or code outside the repository (annotation guide, Step D). The only CORRECT outcome is an abstention (or, for ineligible handling, nothing). A dual target is UNDECIDED, and a single target is UNJUSTIFIED.
- Annotators who cannot decide between DETERMINATE and INDETERMINATE after adjudication record INDETERMINATE.
- UNASSESSABLE marks a method's abstention on a determinate site. It counts against coverage, never against harm.
- Sites whose ground truth cannot be adjudicated at all (annotators and adjudicator disagree on eligibility after discussion) are excluded from scoring and listed with the reason. They are never silently dropped.

## 5. Denominators and fairness

- Every rate (correct, harmful, undecided, coverage) uses n_exec: eligible sites where the method ran. Execution failures are reported in their own column per method.
- Paired comparisons (McNemar) use only sites where both methods ran.
- Detection precision counts FALSE_POSITIVE_SITE for every method, including pqscan abstentions.
- Each external tool's file-failure behaviour is the measured profile in `benchmark/baselines_manifest.json`. A tool's silence on a file of a condition it is known to drop is EXECUTION_FAILURE, never MISSED.

## Changelog

- v1.0 (2026-11-14): frozen. Strict sensitivity scoring adopted (decision C2); execution-failure handling for external tools; abstention on ineligible sites counts as a false positive.
