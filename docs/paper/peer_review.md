# Strict IEEE-style peer review of the provisional manuscript (18 Nov 2026)

**Reviewed:** `ieee_manuscript_draft.md` at the commit after c9164c7, together with `evidence_register.md`, `references.bib` and `related_work_matrix.md`.

**Reviewer stance:** a critical program-analysis, security and statistics reviewer for an IEEE venue.

**Recommendation as an empirical research paper: REJECT** (not yet a study). **As a design / pre-registered protocol paper: MAJOR REVISION.**

## 1. Answers to the ten questions

| # | Question | Verdict | Reason |
|---|---|---|---|
| 1 | Is the research problem clear? | **Yes** | Role-incorrect or undecided PQC targets; KEM ≠ public-key encryption is grounded in FIPS 203 Sec. 3.3 and SP 800-227 Sec. 5.2.1 |
| 2 | Does the RQ match the implementation? | **Mostly; one alignment issue (R2)** | "At comparable coverage" is implemented as coverage matching only for the method/argument comparators (H2). The algorithm-family baselines are compared at natural coverage (F-A). The RQ text was not changed; the draft now states this explicitly (Sec. IX). |
| 3 | Are the contributions supported? | **C1–C4 as artefacts: yes. C5 (the measurement): no.** | C1–C3 are implemented and tested, but not shown to be *useful* or *correct* on real code. C4 is verified and calibrated. Novelty is provisional. |
| 4 | Is the methodology reproducible? | **Yes for software and calibration; not yet for results** | Pinned commits, seeds, hash-chained ledger, byte-identical rebuilds, verification script (81 checks). One OS only. |
| 5 | Is the dataset sufficient for the proposed claims? | **The design is sufficient; the data is not yet** | 0 labels; 360 planned primary-set sites; 7 test repositories; PyCryptodome thin before test |
| 6 | Are the evaluation limitations transparent? | **Yes** | Sec. XII–XIII and the placeholders are explicit. The single annotator and the seven fixed repositories are stated. |
| 7 | Are the PQC recommendations technically correct? | **Yes**, with one citation-precision note (W6) | Every policy statement was checked against IR 8547 (final), FIPS 203/204 and SP 800-227 (E42) |
| 8 | Are equations, tables, metrics and references traceable? | **Yes** | E-ids → `verify_evidence.py`. All 54 bib keys resolve and were verified. Equations (1)–(4) follow analysis plan Secs. 4, 5 and 7. |
| 9 | Does it overstate novelty or results? | **No in the current draft** | Novelty is hedged ("to our knowledge, pending the final novelty audit"); results are placeholders. Watch C1–C3 wording at submission. |
| 10 | Can it be submitted as a completed empirical paper? | **No** | The RQ is unanswered. There are no labelled results, no hypothesis outcomes and no baseline comparison. |

## 2. Section-by-section review

| Section | Assessment | Required change |
|---|---|---|
| Title | Describes a method whose benefit is unproven | Owner D2. Avoid implying improvement. |
| Abstract | Honest. It states that no labelled results exist. | After E, rewrite with the pre-registered statement templates only |
| I. Introduction | Clear motivation; RQ verbatim | Make the "status" paragraph the first thing reviewers read (done) |
| II. Background | Accurate, with section-level NIST citations | Add the exact FIPS 186-5 reference only if DSA is discussed further (FIPS 186-5 not re-read; currently not cited) |
| III. Related work | Good coverage. Several content claims are ◐ (abstract only); tool statements date from 12 Nov source inspections. | Re-check ◐ items in full text. Re-inspect baseline tool versions before submission, because tools evolve. |
| IV. Contributions | Correctly separates available (C1–C4) from pending (C5) | Reviewers will see C1–C3 as engineering without evaluation. D8 framing decision. |
| V. Architecture | Clear | Draw Fig. 1 to the template |
| VI. Role inference | Precise; bounds stated (depth ≤ 2, within a module) | **Done:** an original synthetic worked example (Sec. VI-F) whose outcomes are pqscan's actual output |
| VII. Policy | Correct and cited | Decide W6 (D9). The PROTOCOL_REVIEW class is unreachable by the tool (W4/D10); either keep it as ground-truth-only or implement detection before F1. |
| VIII. Dataset | Careful candidate/eligible distinction | State the expected eligible yield; it is unknown until labelling, so say so |
| IX. Methodology | Rigorous and pre-registered | **R2:** coverage alignment (now stated). **R6:** justify calibration at B = 1,000 against analysis at B = 10,000 (R4-13 rationale) in one sentence. |
| X. Implementation evaluation | Verified figures | Keep the "not scanner accuracy" sentences. Consider moving the demonstration table to an appendix (D13). |
| XI. Results | Placeholders only | Cannot be reviewed |
| XII. Threats | Thorough | Add: the AI reviewer may share failure modes with the owner's reasoning (it is not independent); baseline tool versions are a moving target |
| XIII–XIV | Honest | — |
| References | Verified metadata | Nothing invented; 8 relayed or abstract-level content claims flagged in the matrix |

## 3. Correction list

| # | Correction | Severity | Status |
|---|---|---|---|
| R1 | Do not present as a completed empirical paper; choose the scope (design/protocol vs wait for E) | Critical | **Owner decision D3**; the draft labels itself provisional and non-submittable |
| R2 | RQ "at comparable coverage" vs F-A at natural coverage | Major | **Analysed** (18 Nov): `d7_rq_alignment.md` (two options with consequences; Option A recommended). **Resolved 18 Nov: owner chose Option A**, applied in manuscript Secs. I and IX. Also found: the F-A membership names an algorithm-name mapping without a code variant (D15; **resolved 18 Nov: B1-algorithm**, recorded in the pre-F1 run specification). |
| R3 | Single-annotator ground truth | Major | Disclosed (Secs. VIII-C, XII). Adding an external annotator would be a protocol change: owner decision. |
| R4 | Generalisation beyond the 7 repositories | Major | Disclosed, with S16 evidence; wording rules enforced |
| R5 | Novelty provisional; ◐ related-work claims | Major | **Partly done** (18 Nov): 20 papers checked in full text and 6 tools in pinned source (`related_work_fulltext_audit.md`). Four of our descriptions were corrected; the absence claim is scoped. 14 works remain NOT FULL-TEXT VERIFIED (ACM bot check, CAPTCHA, no open copy). The final novelty audit (D11) remains. |
| R6 | Calibration B vs analysis B | Minor | **Fixed** (Sec. IX): calibration at fixed B = 1,000 for comparability with R4-13; the only B check on record (R4-03c Sec. 3) concerns an earlier unguarded version; no claim about B = 10,000 beyond that |
| R7 | Demo table may be misread as evaluation | Minor | Labelled. Placement is owner decision D13. |
| R8 | Formal definition of δ̃_r (tie averaging) in the paper | Minor | **Fixed** (Sec. IX, eqs. 2a–2c), from analysis plan Sec. 5 and `pqscan/bench/matching.py` |
| R9 | Reproducibility verified on one OS only | Minor | **Applied**: stated in Sec. X-C |
| R10 | PROTOCOL_REVIEW class unreachable | Minor | Disclosed (Sec. VII); owner decision D10 |
| R11 | Citation precision in the policy text (W6) | Minor | Manuscript cites the precise sections; policy text is owner decision D9 |
| R12 | AI-use disclosure and the AI reviewer's non-independence | Minor | **Threat fixed** (Sec. XII: not an independent annotator; shared failure modes; no inter-annotator reliability). The AI-use disclosure wording remains owner decision D6. |
| R13 | IEEE formatting | — | Blocked on the sample paper (D1). No compliance claim made. |

## 4. Bottom line

- **Now:** this is an implementation and pre-registered evaluation-design paper. It is technically accurate, traceable and honest about what is missing.
- **It becomes an empirical research paper** only after the owner-gated pipeline (`owner_action_checklist.md`) reaches E. That includes DV annotation, the 14-day re-label gap, F1, T annotation and F2.
