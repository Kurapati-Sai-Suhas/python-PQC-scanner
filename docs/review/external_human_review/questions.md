# Questions for the external specification reviewer

Please answer each question with "no issue", or name the document, section and passage and say what is wrong. Where a question touches an issue the AI reviews already raised (see `third_ai_review_report.md`), say whether you agree and what you would decide.

## A. Research question and hypotheses
1. Is the research question (protocol Sec. 1) answerable by the planned comparisons? In particular, "comparable coverage" holds by construction only in family F-B; family F-A compares at natural coverage. Is that acceptable as stated?
2. Are H1a, H1b, H2a, H2b, H3 and H4 each defined precisely enough to compute without further choices? The AI review flagged the H1a numerator (TA08), the H3 harmful-rate definition (TA03), and the H4 quantifier and synthetic split (TA04, TA05).
3. Is it acceptable that only F-B and F-A are under family-wise error control, while H1, H3 and H4 are threshold rules or secondary analyses?

## B. Sampling and labelling
4. Are the repository qualification, the 4/2/7 split and the candidate-pool construction free of bias that would favour the scanner?
5. Are the annotation guide's eligibility and role rules unambiguous? Please look at protocol-configuration calls (TA06), escaped keys of single-purpose algorithms (TA07), the PyCryptodome split idiom `cipher = PKCS1_OAEP.new(key)` followed by `cipher.encrypt(m)` (TA11), and hybrid components (TA19).
6. Single-investigator labelling with an isolated AI-assisted review and a ≥ 14-day intra-rater re-label: is this adequate for the claims the protocol allows? Which κ statistic should trigger the reliability rule (TA09)?

## C. Statistics
7. Is the matched, tie-averaged estimand (analysis plan Secs. 2–5) appropriate, and is its behaviour under execution failures described correctly?
8. Are the re-matching bootstrap, the signed coverage-gap guard (g < 1/10 → p doubled), the feasibility gate and Holm control appropriate for seven fixed repositories?
9. Calibration: scenario S16 (random repositories) exceeds the criterion and is treated as outside inference, but the plan does not exempt it in writing (TA01). Is the conditional-on-fixed-repositories scope acceptable, and should the exemption be recorded?
10. Is power adequate? With seven repositories, calibration power at δ = +0.04 was 0.16–0.22. What should be reported if H2a is not supported?

## D. Cryptographic correctness
11. Is the role-to-guidance policy (recommendation policy Sec. 3; `policy_v1_1.yaml`) correct against FIPS 203/204/205, SP 800-227 and IR 8547? In particular, KEM-DEM for public-key encryption, hybrids as transitional, and DSA.
12. Is the hybrid-recognition rule (one function, explicit combination, data combination only) conservative enough?

## E. Leakage, blinding, reproducibility
13. Are the safeguards against test-data leakage adequate? Note that several are self-attested, not enforced: test-output blinding, tool-attribution isolation, AI-review isolation (TA23) and no manual scanner runs (TA24).
14. Could another team reproduce the candidate orders, bootstrap and calibration from the documents (TA25)?

## F. Overall
15. Is there anything that must change before the pre-test freeze F1? Please separate what must change from what you suggest.
