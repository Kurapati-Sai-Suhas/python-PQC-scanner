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
| VI. Role inference | Precise; bounds stated (depth ≤ 2, within a module) | Add a worked example (the guide's Sec. 7 has pilot-based examples; use synthetic ones to avoid circularity) |
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
| R2 | RQ "at comparable coverage" vs F-A at natural coverage | Major | **Applied** (Sec. IX coverage note). Presentation choice recorded as owner decision D7. The RQ text is not changed. |
| R3 | Single-annotator ground truth | Major | Disclosed (Secs. VIII-C, XII). Adding an external annotator would be a protocol change: owner decision. |
| R4 | Generalisation beyond the 7 repositories | Major | Disclosed, with S16 evidence; wording rules enforced |
| R5 | Novelty provisional; ◐ related-work claims | Major | **Open**: final novelty audit (D11); full-text re-check (Claude can do the open-access items) |
| R6 | Calibration B vs analysis B | Minor | **Open**: add one justification sentence from R4-13 when finalising Sec. IX |
| R7 | Demo table may be misread as evaluation | Minor | Labelled. Placement is owner decision D13. |
| R8 | Formal definition of δ̃_r (tie averaging) in the paper | Minor | **Open**: copy the closed form from analysis plan Sec. 5 at the formatting stage |
| R9 | Reproducibility verified on one OS only | Minor | **Applied**: stated in Sec. X-C |
| R10 | PROTOCOL_REVIEW class unreachable | Minor | Disclosed (Sec. VII); owner decision D10 |
| R11 | Citation precision in the policy text (W6) | Minor | Manuscript cites the precise sections; policy text is owner decision D9 |
| R12 | AI-use disclosure and the AI reviewer's non-independence | Minor | **Open**: D6; add the threat sentence at the formatting stage |
| R13 | IEEE formatting | — | Blocked on the sample paper (D1). No compliance claim made. |

## 4. Bottom line

- **Now:** this is an implementation and pre-registered evaluation-design paper. It is technically accurate, traceable and honest about what is missing.
- **It becomes an empirical research paper** only after the owner-gated pipeline (`owner_action_checklist.md`) reaches E. That includes DV annotation, the 14-day re-label gap, F1, T annotation and F2.
