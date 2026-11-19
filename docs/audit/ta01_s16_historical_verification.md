# TA01: historical verification of the S16 calibration exemption (19 Nov 2026)

**Question (owner instruction, 19 Nov 2026):** was S16 explicitly outside the inferential acceptance criterion **before its result was observed**? If yes, record the fixed-repository scope and report S16 as an out-of-scope generalisation diagnostic. If no, do not exclude S16 retrospectively. Report the calibration failure and keep F1 blocked until an adopted and calibrated solution exists.

**Answer: NOT ESTABLISHED.** S16 is not excluded. Acceptance criterion 2 of the analysis plan (Sec. 11) is not met under the adopted text, so **F1 is blocked**.

## Evidence, in date order (all in Git history)

| # | Date (commit time, IST) | Commit | What it shows |
|---|---|---|---|
| 1 | before 16 Nov 2026 (planning stage; archived 16 Nov 11:22) | `0b628f4` | The planning calibration reports already **observed** S16 above the limit. `docs/proposals/v1.0.4/rev4/R4_03c_bootstrap_calibration_report.md` line 57: S16 = 0.0422 at α = 0.025; line 105: "Repositories as a sample from a wider population: **no**". `R4_13_calibration_report_v12pp.md` line 53: S16 = 0.0415, shown in italics as "generalisation". The scope statement and the observation appear **together**, in the same reports. |
| 2 | 16 Nov 11:31 | `325b9b3` | Protocol v1.0.4 adopted. `phase3_analysis_plan.md` Sec. 11, item 2: "The 18 single-comparison scenarios, the 8 near-equal-coverage cells and the 8 family configurations must give: every Type I cell ≤ nominal + 3 MC-SE". **No scenario is exempted.** S16 is one of the 18 (S00–S17). Sec. 11 item 4: if the criteria fail, "work stops and the owner decides, before F1". The protocol states that inference is conditional on the seven fixed repositories, but the adopted acceptance criterion does not carve S16 out on that basis. |
| 3 | 16 Nov 12:12 | `3e8ee67` | The acceptance script was written **after** adoption. `scripts/phase3_acceptance.py` line 242 says `ok = (...) or k == "S16"`. This exemption exists only in code, not in the adopted plan. |
| 4 | 17 Nov 22:49 | `a89743a` | The acceptance run reports S16 = 0.0415 (MC-SE 0.0014), marked "yes (generalisation; not used for inference)", and the overall result ACCEPTED. The limit is 0.025 + 3 × 0.0011 ≈ 0.028. |

**Not to be confused with:** plan Sec. 10 also has a sensitivity item labelled "S16" (the cluster bootstrap by repository, labelled "not a population CI"). That is a reporting item, not the calibration scenario S16.

## Conclusion under the owner's rule

- The exemption was never adopted as part of the acceptance criterion. It was introduced in the acceptance script after adoption. The planning reports that motivated it already contained the S16 result, so even the informal scope statement does not predate the observation.
- Therefore S16 is **not** excluded retrospectively. Criterion 2 is **not met**: one Type I cell exceeds nominal + 3 MC-SE. The statement "ACCEPTED" in `docs/implementation/acceptance/` was correct only under the script's unadopted exemption.
- The acceptance records and the nine E30 closure files are **not modified**; they remain the historical record. This document and revision r6 record the correct reading.
- **F1 stays blocked** until an appropriately adopted and calibrated solution exists.

## Owner decision required (options; nothing decided here)

| Option | What it means | Consequence |
|---|---|---|
| A | Adopt a new, explicitly pre-specified acceptance criterion that scopes inference to the seven fixed repositories, **acknowledged as adopted after S16 was observed** | Honest, but visibly post hoc. A reviewer may reject it. It must be disclosed as such in every report. |
| B | Develop and calibrate a procedure that is valid for randomly drawn repositories (for example, a repository-level method), then re-run the whole acceptance | A different study design. It needs new code, a new calibration and a new adoption record. Weeks of work. |
| C | Keep F1 blocked and report the study as specified, implemented and calibrated, with the failed S16 cell disclosed. Run no confirmatory evaluation | No inferential claims at all. This is the current state. |

**For the college submission (deadline 20 Nov 2026):** the paper reports option C as the current status. That means the calibration result includes the failed S16 cell, F1 is not performed, and no hypothesis result exists.
