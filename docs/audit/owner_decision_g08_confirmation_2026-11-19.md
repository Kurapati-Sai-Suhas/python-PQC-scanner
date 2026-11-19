# Owner decision: G08 confirmation (third-review finding TB01), 19 Nov 2026

**Trigger.** The third AI review, Package B (`docs/review/spec_review_v1.0.5-r3/review_outputs/package_B_closure_audit.md`, finding TB01, major), noted a mismatch. The G08 record quoted the owner's wording "include the seven specified pqscan arms" and recorded an interpretation in which H4 Part 1 contains only two pqscan arms, yet it marked G08 CLOSED. Because H4 Part 1 requires every tool in its set to meet the 30% flip criterion, the set must be confirmed before any H4 evaluation.

**Owner decision (verbatim substance, received 19 Nov 2026).** H4 Part 1 contains exactly eight baselines:
1. the six registered external-tool baselines;
2. B1-algorithm;
3. B2-method-args.

The remaining five pqscan arms are reported separately and must not be added to H4 Part 1. The inclusion criterion is membership in the registered F-A baseline set. It is **not** based on evidence tier, on whether an arm is T0 or T2, or on whether an arm is external or internal. No H4 threshold, flip requirement (30%), hypothesis, metric, statistical method or estimand changes. This confirms the interpretation of the decision already recorded; it authorises no evaluation and does not bypass the F1, F2 or E gates.

## The eight identifiers (H4 Part 1)

| # | Identifier | Kind | Why included |
|---|---|---|---|
| 1 | `pqcheck` | external tool | registered F-A baseline |
| 2 | `pqc-audit` | external tool | registered F-A baseline |
| 3 | `PostQuant` | external tool | registered F-A baseline |
| 4 | `qsafe` | external tool | registered F-A baseline |
| 5 | `QSA-regex` | external tool | registered F-A baseline |
| 6 | `pqblocks-scan` | external tool | registered F-A baseline |
| 7 | `pqscan:B1-algorithm` | internal arm | registered F-A baseline (D15) |
| 8 | `pqscan:B2-method-args` | internal arm, **T0** | registered F-A baseline; included because of that membership, although it is a T0 arm |

**Reported separately, never in Part 1 (five pqscan arms):** `pqscan:B4-full-T2` (the proposed analyser, H4 Part 2), `pqscan:B1-dual` (descriptive only, D15), `pqscan:B3-full-noabst`, `pqscan:method-args-recv-T0`, `pqscan:method-only-T0`.

**Why H1b uses a different set.** H1b (RQ1) asks about *existing scanners*, so its separately registered set is the six external tools (F12, H-4). That set is unchanged. H4 Part 1 (RQ4) asks whether transformations change the outcome of any baseline method the proposed analyser is compared with, so it uses the F-A baseline set. The set used is printed next to every H1b and H4 result.

## Implementation (revision v1.0.5-r4; wording only, set unchanged)

| Source | Change | Agreement |
|---|---|---|
| `pqscan/bench/h4.py` | Docstring states the criterion; new `REPORTED_SEPARATELY` (the five arms) | `PART1_BASELINES` = the eight, unchanged |
| `docs/specification/run_specification_pre_f1.json` (authoritative) | `pqscan_arm_roles` reworded (no "T0 comparator" criterion); `part1_inclusion_criterion`, `h1b_versus_h4_sets`, `owner_confirmation`; decision `OD-2026-11-19-G08C` | `decision_set_part1` = `families.F-A.baselines` = the eight, unchanged |
| `docs/specification/run_specification_pre_f1.md` | Owner-confirmation bullet and H1b-versus-H4 bullet added; "The T0 comparators" changed to "The arms" | Lists the same eight, in order |
| `tests/test_g08_confirmation_and_fa_assumptions.py` | New: enforces exactly eight, the other five separate, the criterion, and the unchanged H1b set | — |

Pre-change texts are archived byte-for-byte in `docs/specification/archive/v1.0.5-r3/`. The original G08 record (`owner_decisions_g02_g03_g08_g10.md`) and the third-review audit are preserved verbatim; a dated pointer is appended to the former.

**TB01 status:** resolved by explicit owner confirmation. **G08 status:** CLOSED (interpretation confirmed by the owner, 19 Nov 2026).
