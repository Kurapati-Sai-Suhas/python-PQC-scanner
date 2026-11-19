# Owner decisions needed before annotation and before F1 (from the third AI review, 19 Nov 2026)

Source: `docs/review/spec_review_v1.0.5-r3/review_outputs/third_ai_review_report.md` (verbatim findings in `package_A_specification_review.md` and `package_B_closure_audit.md`).

**Nothing here has been decided.** Each item needs an explicit owner decision, then a recorded revision: new adoption record, pre-change text archived, tests. No threshold changes are proposed. The options below are the reviewers' suggestions plus the obvious alternatives; the owner chooses.

## A. Before any annotation (labelling rules; deciding later would mix two rules in the labels)

| ID | Question | Options |
|---|---|---|
| TA06 | The taxonomy's PROTOCOL_CONFIG examples (`ssl.SSLContext.set_ciphers`, KEX lists) are calls the guide declares out of scope | (a) Restrict the examples to protocol objects of supported libraries and mark the row reserved (reviewer's suggestion); (b) keep and add an explicit "out of scope" note |
| TA07 | Escaped key of a single-purpose algorithm (X25519/X448/DH; Ed25519/Ed448/DSA): the guide says UNKNOWN with all roles; the scanner gives the algorithm's role at T2 | (a) Label the algorithm's role family; (b) keep UNKNOWN but limit possible roles to that family plus KEY_MATERIAL_ONLY |
| TA11 | PyCryptodome split idiom: `cipher = PKCS1_OAEP.new(key)`; `cipher.encrypt(m)` | (a) The operation statement is the site, `.new(key)` is ineligible, and the receiver check accepts cipher or signer objects built from a key; (b) the reverse |
| TA19 | Can `hybrid_component` be true for roles other than KEY_ESTABLISHMENT, SIGN, VERIFY? | (a) No: add the rule to guide Step F and the schema; (b) allow it and define scoring |

## B. Before F1 (how hypotheses are computed, and records F1 needs)

| ID | Question |
|---|---|
| TA01 | Record in plan Sec. 11.2 that S16 (random repositories) is outside the criterion because inference is conditional on the fixed repositories; or record it as a failed cell |
| TA03 | Which harmful-rate definition does H3 use (per eligible site, or per recommendation)? Add a reporting rule for the coverage-confounded always-recommend comparison |
| TA04 | H4 Part 1 quantifier: per tool (the adopted reading) and also report whether one operator meets the threshold for all eight baselines? |
| TA05 | H4 population: synthetic holdout only, all base cases, or both reported? |
| TA08 | H1a numerator: `obvious_from_name = false`, `evidence_needed ≠ none`, or either; how indeterminate sites count |
| TA09 | Name the κ that triggers the reliability rule (the code uses intra-rater κ(gt_role)) |
| TA10 | Add `docs/specification/api_coverage.md` to the F1 hash list |
| TA22 | Apply unresolved-site bounding to F-A and H1 as well, or state why not |
| TA28 | H3 bootstrap procedure details |
| TA17 | `h2.py` takes K from its input length: assert K = 7 in the future E driver (keeps the calibration closure intact), or change `h2.py` (breaks the E30 closure trace) |
| W6 | Policy text cites SP 800-227 "Secs. 2.1, 5.2"; precise: 5.2.1 and 4.3 |
| N1 | PyCryptodome PQ modules (ML-KEM, ML-DSA, Hybrid): extend hybrid recognition, or keep as a disclosed limitation |
| D14 | Mehl scanner exclusion reason |

## C. Wording-only revisions (no decision on substance; can be bundled into one revision)

TA14, TA15, TA16, TA18, TA20, TA21, TA23, TA24/TB04, TA25, TA27, TB05, TB06, TB07, TB10, TB11, TB12. See the combined report, Section 3.
