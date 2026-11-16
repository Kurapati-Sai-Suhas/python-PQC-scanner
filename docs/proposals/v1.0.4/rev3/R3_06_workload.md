# R3-06 Owner workload (PROPOSED, revision 3) — every figure is an assumption, not a measurement

Model: `scripts/workload_rev3.py`, output in `results/workload_rev3.md`. It uses the actual repository counts (6 development/validation at quota 25, 7 test at quota 30), B0 = 10 per repository, and the S1 yield, time and disagreement assumptions listed in that file.

| Activity | Low | Expected | High |
|---|---|---|---|
| Candidates, Phase DV / Phase T | 378 / 511 | 468 / 630 | 618 / 833 |
| Primary annotation (DV + T) | 19 h | 31 h | 54 h |
| AI review and export, including the 10% repeat runs (DV + T) | 8 h | 21 h | 54 h |
| Owner adjudication (DV + T) | 5 h | 14 h | 44 h |
| Intra-rater re-labelling (DV + T) | 4 h | 5 h | 9 h |
| Frame audit | 3 h | 5 h | 8 h |
| Pilot re-labelling (31) | 2 h | 3 h | 4 h |
| Synthetic subset (78) | 2 h | 3 h | 5 h |
| Specification review (run ChatGPT; sign-off) | 2 h | 4 h | 8 h |
| Final evaluation and reporting (owner's share) | 8 h | 16 h | 32 h |
| **Total** | **52 h** | **102 h** | **216 h** |

**Assumptions** (low / expected / high):
- S1 eligibility yield: 50 / 40 / 30%.
- Overshoot: 3 / 5 / 9 candidates per repository.
- Minutes per ineligible candidate: 0.75 / 1 / 1.5. Per eligible candidate: 2 / 3 / 4.
- S2 yield: 5 / 10 / 20%.
- AI handling: 0.5 / 1 / 2 min per candidate.
- Disagreement rate: 10 / 20 / 30%, at 3 / 4 / 6 min each.
- Re-label: 2 / 2.5 / 3.5 min per item.

The rows are rounded sums of the per-phase outputs of the script. The expected scenario is about **100 owner hours**. Revision 2's "60–105 h" was too narrow: it did not separate the AI-handling time per phase, and it did not model low-yield, high-disagreement conditions.
