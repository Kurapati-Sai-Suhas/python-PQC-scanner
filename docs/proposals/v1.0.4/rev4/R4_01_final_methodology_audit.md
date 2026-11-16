# R4-01 Final methodology audit of revision 3 — PROPOSED, NOT ADOPTED (revision 4)

Scope: revision 3 (`docs/proposals/v1.0.4/rev3/`) checked against the frozen documents, the code (read-only) and new simulations (`rev4/scripts`, `rev4/results`). Earlier tests passing is not taken as proof of validity: every revision 3 claim was re-derived.

## 1. Defects found in revision 3

| # | Severity | Defect | Evidence | Revision 4 response |
|---|---|---|---|---|
| D1 | **critical** | The H2 arms' thresholds were never specified. The method+args arm only yields T0/T1, so at τ = T2 it never recommends, and equal coverage would be degenerate | `docs/dev/roles_on_pilot.md` (method+args tiers T0 = 2, T1 = 28) | V18: both arms at T0 (no tier gate), then matched; the proposed system (T2) as secondary |
| D2 | **critical** | The confirmatory repository-level t test assumes randomly sampled repositories; the 7 were selected purposively | `repository_split.md` Sec. 2; verification records | V13′: confirmatory inference restricted to the 7 repositories; generalisation exploratory |
| D3 | **critical** | Within-repository coverage matching makes outcomes dependent. Paired tests then overstate the variance about 2× (very conservative); this was never analysed | `results/matching.md`: variance ratio 0.486; score-test rejection 0.0025 at nominal 0.025 | stratified re-matching bootstrap as primary (calibrated rejection 0.0145) |
| D4 | major | Revision 3 called the site-level score test "not valid" in general. It is valid for the fixed-repository estimand and invalid only for generalisation | `results/h2_type1.csv`: fixed-mode site tests ≤ 0.0300; random mode up to 0.118 | estimand-specific test choice (R4-02 Sec. 5) |
| D5 | major | Margin step: confirmatory status with power 0.07–0.43 at a true 15 pp (fixed mode, α/4–α) contradicts the owner's rule against pretending adequacy | `results/h2_power.csv` | V10a‴: magnitude exploratory, direction confirmatory (alternative: confirmatory with m = 4) |
| D6 | major | The sign-flip test was proposed as robustness under Holm m = 4, but its smallest p (1/128 = 0.0078) exceeds α/4 = 0.00625 | arithmetic; `results/h2_power.csv` (power 0 at α/4) | descriptive only |
| D7 | major | Coverage was used as if 1 − abstentions. The frozen definition is RECOMMEND / eligible, and FLAG_NO_TARGET exists | `data_dictionary.md`; `pilot_harness/summary.md` (B4: 0 abstentions, coverage 23/30) | R4-03 uses the frozen definition |
| D8 | moderate | S2 exclusion could hide tool false positives and make the frame look comprehensive | design review | R4-05 Sec. 1: separate false-positive and S2 reporting |
| D9 | moderate | `context_used` had no timing rule or value criteria | design review | R4-05 Sec. 5: recorded in the hashed primary file before the AI review; two values with criteria |
| D10 | minor | Revision 3's worked Holm narrative was not written out as a table | — | R4-02 Sec. 6 (computed table; a narrative error in the draft was caught by computation and corrected) |

## 2. Decision-by-decision

| # | Revision 3 | Revision 4 verdict | Reason |
|---|---|---|---|
| V1 | single investigator + blind ChatGPT + owner adjudication | **APPROVE** | unchanged; wording limits retained |
| V2 | quotas 30/25, 360, 13 repositories | **APPROVE** | arithmetic verified (7 × 30 + 6 × 25 = 360); manifest has 13 |
| V3 | intra-rater per phase | **MODIFY → V3′** | 8 fields; enforced gap; bootstrap within repositories (R4-05 Sec. 3) |
| V4 | consensus and AI-label secondary analyses | **APPROVE** | applied to matched outcomes |
| V5 | test-file rule | **APPROVE** | verified on 683 development/validation files (revision 3) |
| V6 | sampler, ledger, validation (M1–M14) | **APPROVE** | unchanged; plus a test for the bootstrap and matching code |
| V7 | frame audit | **MODIFY → V7′** | explicit "can / cannot estimate" (R4-05 Sec. 4) |
| V8 | AI isolation and identity | **APPROVE** | unchanged |
| V9 | unresolved bounding | **APPROVE** | unchanged |
| V10a′ | fixed sequence, confirmatory margin | **REJECT → V10a‴** | margin underpowered at plausible effects; direction confirmatory, magnitude exploratory |
| V10b′ | Holm m = 4 | **MODIFY → V10b″** | Holm m = 3 (B1, B3, B4) recommended; m = 4 kept as the owner's alternative; FWER verified for both |
| V11 | S1-nonapp and precedence | **APPROVE** | — |
| V12 | coverage matching | **MODIFY → V12′** | frozen coverage definition; output-adaptive target; within-repository; re-matching bootstrap; seed sensitivity |
| V13 | repository-level t confirmatory | **REJECT → V13′** | purposive selection; confirmatory inference about the 7 repositories only |
| V14 | S2 and annotator-added excluded | **MODIFY → V14′** | false-positive and out-of-scope reporting added |
| V15 | 13 repositories | **APPROVE** | factual |
| V16 | `context_used` | **MODIFY → V16′** | timing, criteria, packet-first on a 10% subset |
| V17 | one-sided 0.025 | **APPROVE** | defined as the family level |
| **V18 (new)** | — | **NEW** | H2 arm thresholds (D1) |

## 3. Verdict

**MODIFY.** Revision 3 cannot be approved as written because of D1–D3. Revision 4 resolves them, and its documents are **ready for owner review**. Approval is the owner's decision, and the open choices are listed in `R4_06`.
