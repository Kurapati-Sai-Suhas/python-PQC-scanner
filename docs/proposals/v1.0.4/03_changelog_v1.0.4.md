# Change log: protocol v1.0.3 → v1.0.4 (PROPOSED, revision 2)

"Approval" refers to `06_open_decisions.md`. "Consequential" means the change follows from another approved item.

| Section | v1.0.3 | Proposed v1.0.4 | Why | Approval |
|---|---|---|---|---|
| 1 H2 decision rule | "Paired McNemar … Holm-corrected across arms; report difference with bootstrap CI"; the role of "≥ 10 pp" was undefined | three pre-registered outcomes: supported (significant and observed ≥ 10 pp), partially supported (significant, < 10 pp), not supported. The hypothesis wording is unchanged | audit: with "≥ 10 pp observed" required, a true 10 pp effect is supported only about 50% of the time at any n, while the power analysis assumed a test of > 0 | V10a |
| 1 Comparison families | "within each family", families not listed | F-B (m = 3: full vs. method+args, vs. method+args+recv, vs. method-only); F-A (full vs. each baseline that ran) | the audit found the Holm family was undefined; the earlier "m = 3" was an assumption | V10b |
| 1 Wording rule | — | "supported", "partially supported", "not supported"; "robust" only if the category holds in the secondary analyses and the bounding range | over-claiming risk with single-annotator labels | V4 |
| 2 Dataset B description | "double-annotated" | owner-annotated, blind AI-assisted review, owner adjudication | no second human | V1 |
| 2 Targets and quotas | 300 / 150; quotas 30 / 25 | numbers unchanged; quotas tabulated in the protocol as the single source; the sampler constant is tested against it | the audit found the manifest has no quota field and the CLI accepted any value | V2, V6 |
| 2 Scope classes | test directory, `test_*.py`, `*_test.py` | adds `test.py`, `tests.py`, `tests_*.py`, `tests-*.py`, `conftest.py`; adds example and vendored classes | verified on 683 development/validation files: newly test = `authlib/docs/conftest.py` and jwcrypto `tests.py`, `tests-cookbook.py`, `tests_mldsa.py` (all genuine). jwcrypto's `tests.py` holds 143 of its 379 "app" candidates | V5 |
| 2 Strata | S1-app, S1-test, S2 | S1-app, S1-nonapp (test, example, vendored), S2 | the sampler counted example and vendored code as app | V11 |
| 2 Candidate IDs | `C-<repo>-<stratum>-<rank>` | opaque hash | old IDs reveal stratum and rank | V6 |
| 2 S2 issuance | inside the first batch | batch B0 | first batch was 20; missing S2 labels caused re-issue | V6 |
| 2 Non-app issuance | 3 per batch until the cap | at most (cap − eligible non-app so far) | with 7 eligible and a cap of 8, 3 more were issued (reproduced) | V6 |
| 2 Overshoot | unstated | every annotated site is kept | prevents post-hoc discarding | V6 |
| 2 Unresolved eligibility | unstated | counts as not eligible for stopping; reported | the stopping rule needed a defined input | V9 |
| 2 Ledger | eligibility inferred from the labels file | hash-chained ledger with hashes only, committed and pushed after each step; strict validation | audit: `"false"` read as true; unknown IDs accepted; duplicates overwritten; a chain without an external anchor can be regenerated | V6 |
| 2 Frame audit | none | seeded files added until ≥ 60 eligible sites (≥ 6 files); Wilson CI; scope stated | six files alone give no defined precision (zero misses in n sites → 95% upper bound about 3/n) | V7 |
| 3 Annotation | two humans, a third adjudicates, κ ≥ 0.70 | owner → blind ChatGPT review → owner adjudication | sole human owner | V1 |
| 3 Fields compared | — | eligible, gt_role, assessability, possible_roles, hybrid_component, obvious_from_name, evidence_needed, key_provenance | audit: `hybrid_component` decides the expected class and `obvious_from_name` / `evidence_needed` decide H1a, but they were not compared | V4 |
| 3 AI settings | — | Temporary Chat or API with a pinned identifier; memory, custom instructions, history, Projects, connectors and browsing off; prompt contents restricted; exported conversations; self-consistency check; context-difference tag; correlation disclosure | "memory off" alone does not prevent leakage; the repository is public | V8 |
| 3 Record format | frozen schema | envelope `{site, meta}`; frozen schema unchanged | the frozen schema forbids extra fields (`additionalProperties: false`) | V6 |
| 3 Intra-rater | — | ≥ 50 candidates per phase (or 10% if larger), at least 14 days later; rule on the κ point estimate, CI always shown | at n of about 21 the 95% range of κ is about ±0.2 | V3 |
| 5 Statistics | κ for human agreement | owner–AI, intra-rater and AI self-consistency κ; consensus and AI-label secondary analyses; unresolved bounding; exact power statement | reliability evidence for one human; V9 bias control | V3, V4, V9 |
| 6 Freeze | two annotators; supervisor-held IDs | owner and AI records, ledger heads, quotas table, V10 decision, attestation | consequential | consequential |
| 7 Threats | — | single annotator, builder overlap (development/validation less blind), correlated AI errors, context asymmetry, self-disciplined blinding, power assumptions, no external validation | honesty | V1 |
| Guide | v1.0 | v1.1 (`04_…`) | — | V1, V5, V6, V8, V11 |

## Corrections to earlier statements

1. **Pool counts:** 2,302 development candidates (statement-level), not 2,802 (line-level). 154 of them are regex-only *candidate lines*, not "sites missed by every tool". Development plus validation: 3,503.
2. **Pilot coverage:** "regex covers 30 of 30 eligible pilot sites" is a count, not an unbiased recall estimate. The pilot sites came from hand-picked files and AI labels; the frame audit (V7) replaces it.
3. **Quotas 25 and 30:** these are not inconsistent; they are the approved quotas. The defect was the hand-typed CLI value.
4. **Power figures (revision 1):** normal-approximation values overstated exact McNemar power by about 0.02–0.04, and they answered "difference > 0", not the H2 rule. They are replaced by the exact and simulated figures in `01` Sec. 4.
5. **Noise approximation:** (1 − 2e) is a binary-flip bound. For errors spread over many classes and unrelated to the arms, the simulated factor is about (1 − e). Neither covers systematic bias.
6. **Revision 1's sampler audit file name:** jwcrypto's other test files are `tests-cookbook.py` and `tests_mldsa.py` (corrected in revision 1).

## Unchanged and explicitly preserved

Hypotheses H1–H4 and their wording; the H1, H3 and H4 decision rules; metric definitions in `scoring_policy.md` v1.0; τ = T2; the statistical methods; Dataset A; the repository and baseline manifests; D4 = A; every Phase 1 and Phase 2 record and result; protocol v1.0.3 and guide v1.0 in history.
