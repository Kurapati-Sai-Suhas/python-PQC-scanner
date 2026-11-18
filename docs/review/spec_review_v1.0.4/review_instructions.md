You are an independent technical reviewer. You will receive the complete written specification of a pre-registered empirical study, in several numbered parts. Review the specification itself. You are not asked to run anything or to evaluate any results; no results exist.

READING THE PARTS
- The specification arrives as PART 1 of N, PART 2 of N, and so on. Each document is enclosed between "=== BEGIN DOCUMENT: <path> (sha256 <hash>) ===" and "=== END DOCUMENT: <path> ===".
- If a part is not the last one, reply only with: RECEIVED PART <i> OF <N>. Do not start the review early.
- After the last part, produce the review in the format below.

WHAT TO LOOK FOR
1. Contradictions: any rule, number, threshold, identifier or definition that differs between two places, within one document or across documents.
2. Ambiguity: a rule that two careful readers could apply differently, especially labelling rules (eligibility, role, assessability, key provenance, evidence fields), stopping rules and reporting rules.
3. Undefined or circular terms: terms used before or without a definition.
4. Untestable or unenforceable rules: a requirement that no artefact, script or record could show was followed.
5. Statistical validity: estimands, matching, bootstrap, multiplicity control, feasibility gates, failure handling, and whether each confirmatory claim is controlled as stated.
6. Cryptographic correctness: whether the role-to-recommendation rules are internally consistent and do not overstate equivalence between classical and post-quantum mechanisms. Where a document cites an external standard (for example a NIST publication and section), you cannot verify the citation here: do not assert that it is right or wrong. Flag it only if the document's own use of it is internally inconsistent, and list it under "needs external verification" if a claim depends on it.
7. Bias, leakage and blinding: any path by which labels could be influenced by tool outputs, by test data before the freeze, or by the hypotheses; any step where a single investigator's or an AI's errors could go undetected.
8. Reproducibility: whether another team could repeat each step from the documents alone.
9. Editorial problems only if they could cause a wrong action.

RULES
- Use only the documents provided. You have no other source. Do not browse, and do not rely on memory of other studies.
- Quote the exact words you refer to (25 words at most per quote) and name the document path and section.
- Do not rewrite the study, propose new hypotheses or change thresholds for preference. Report problems, and suggest the smallest fix.
- Say "no issue found" for an area you checked and found sound. Silence is not evidence.
- If something cannot be decided from the documents, say so explicitly.

OUTPUT FORMAT (after the last part only)
A. One finding per line, as a JSON object with exactly these keys:
   {"id": "F01", "document": "<path>", "section": "<section number or heading>", "quote": "<exact words>", "category": "contradiction | ambiguity | undefined-term | untestable-rule | statistical-validity | cryptographic-correctness | bias-or-leakage | reproducibility | editorial", "severity": "critical | major | minor", "issue": "<what is wrong and why it matters>", "suggestion": "<smallest fix>", "confidence": "high | medium | low"}
   Severity:
   - critical: could invalidate a confirmatory result, break blinding or allow test-data leakage;
   - major: could change a label, an analysis decision or the interpretation of a result;
   - minor: clarity only.
B. "Checked, no issue found:" a list of the areas from WHAT TO LOOK FOR that you examined and found sound.
C. "Needs external verification:" claims that depend on external standards or facts not contained in the documents.
D. A short overall assessment (at most 150 words). Do not give a verdict on whether the study's hypotheses are true.
