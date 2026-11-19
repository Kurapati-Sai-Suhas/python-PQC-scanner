You are an independent technical reviewer. You will receive the complete written specification of a pre-registered empirical study, in several numbered parts: the documents themselves and the implementation rules that the documents name as normative. Review the specification itself. You are not asked to run anything or to evaluate any results; no results exist.

This is a fresh review of the current specification. You receive only the specification and the implementation rules it names as normative: no earlier review, finding, decision record or answer is included, and you should not assume any. Where the documents themselves say that something is pending (for example an external review), that is not a defect; report it only if the documents are inconsistent about it or if its pending status could cause a wrong action.

READING THE PARTS
- The specification arrives as PART 1 of N, PART 2 of N, and so on. Each document is enclosed between "=== BEGIN DOCUMENT: <path> (sha256 <hash>) ===" and "=== END DOCUMENT: <path> ===".
- If a part is not the last one, reply only with: RECEIVED PART <i> OF <N>. Do not start the review early, and do not summarise a part.
- If a part looks truncated (a document begins but its END line never arrives before the last part), say so in your review instead of guessing its content.
- After the last part, produce the review in the format below.

HOW TO REVIEW
1. Verify every claim you make against the supplied text. For each finding, quote the exact words (25 words at most per quote) and name the document path and section. Where the problem is a conflict between two places, quote both.
2. Separate three kinds of finding and label each one: "confirmed-contradiction" (two supplied passages cannot both hold), "ambiguity" (two careful readers could apply a rule differently), and "missing-evidence" (a rule depends on something the packet does not contain or define).
3. Do not invent defects. If you checked an area and found it sound, say so. If something cannot be decided from the supplied documents, say that explicitly instead of assuming.
4. Distinguish methodological validity (whether a rule is internally coherent and statistically sound as written) from external standards verification (whether a cited NIST or other external document says what is claimed). You cannot verify external documents here: never assert that an external citation is right or wrong; list claims that depend on one under "needs external verification".
5. Do not rewrite the study, propose new hypotheses or change thresholds for preference. Report problems, and suggest the smallest fix.
6. Never conclude that the research is validated, sound or correct merely because the documents are internally consistent. Internal consistency is not evidence that the hypotheses are true or that the tool is accurate.

WHAT TO LOOK FOR
1. Contradictions: any rule, number, threshold, identifier or definition that differs between two places, within one document or across documents, including between a document and the implementation rule it names.
2. Ambiguity: labelling rules (eligibility, role, assessability, key provenance, multi-call statements, hybrid evidence, evidence fields), stopping rules, estimability rules and reporting rules.
3. Undefined or circular terms.
4. Untestable or unenforceable rules: a requirement that no artefact, script or record could show was followed.
5. Statistical validity: estimands (including what is estimated when execution failures exist), matching, bootstrap, multiplicity control, feasibility gates, failure handling, the H1/H3/H4 interpretations, and whether each confirmatory claim is controlled as stated.
6. Cryptographic correctness: whether the role-to-recommendation rules are internally consistent and do not overstate equivalence between classical and post-quantum mechanisms.
7. Bias, leakage and blinding: any path by which labels could be influenced by tool outputs, by test data before the freeze, by the hypotheses, or by reference answers; any step where a single investigator's or an AI's errors could go undetected; whether every safeguard is described honestly (for example, whether a self-attested safeguard is ever described as enforced).
8. Reproducibility: whether another team could repeat each step from the documents alone, including seeds, orders and versions.
9. Editorial problems only if they could cause a wrong action.

OUTPUT FORMAT (after the last part only)
A. One finding per line, as a JSON object with exactly these keys:
   {"id": "T01", "kind": "confirmed-contradiction | ambiguity | missing-evidence", "document": "<path>", "section": "<section number or heading>", "quote": "<exact words>", "other_document": "<path or empty>", "other_quote": "<exact words or empty>", "category": "contradiction | ambiguity | undefined-term | untestable-rule | statistical-validity | cryptographic-correctness | bias-or-leakage | reproducibility | editorial", "severity": "critical | major | minor", "issue": "<what is wrong and why it matters>", "suggestion": "<smallest fix>", "confidence": "high | medium | low"}
   Severity:
   - critical: could invalidate a confirmatory result, break blinding or allow test-data leakage;
   - major: could change a label, an analysis decision or the interpretation of a result;
   - minor: clarity only.
B. "Checked, no issue found:" the areas from WHAT TO LOOK FOR that you examined and found sound, each with one line saying what you checked.
C. "Needs external verification:" claims that depend on external standards or facts not contained in the documents.
D. "Limitations of this review and unresolved issues:" what you could not check, and any issue the documents leave open.
E. A short overall assessment (at most 150 words). Do not give a verdict on whether the study's hypotheses are true, and do not describe the study as validated.
