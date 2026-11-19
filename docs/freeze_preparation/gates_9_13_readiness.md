# Gates F1, test annotation, F2, E and results: readiness (19 Nov 2026, commit 1cdc2d7 + this preparation)

Nothing in this file performs or approves a gate. It lists, for each gate, what must be true and how it will be checked, so that the owner can see the exact remaining path.

## Phase 9: F1 pre-test freeze (explicit approval gate)

- **Check:** `python scripts/f1_readiness.py` (exit 1 until ready). Current output: `f1_package_DRAFT/f1_readiness.json`, status **NOT READY: DRAFT, NOT APPROVED**.
- **Computed now:**
  - commit and tree fingerprint;
  - SHA-256 of all item-2 documents, the baseline manifest, the sampling frame, the synthetic dataset, the AI identity, prompt and packet rules, the statistical code and the calibration evidence;
  - the H4 Part 1 set verified as exactly the eight confirmed baselines;
  - all seven test repositories confirmed unopened.
- **Missing:**
  - the external human review (Phase 7);
  - DV labels and ledger heads;
  - DV reliability (needs the ≥ 14-day re-label);
  - frame audit;
  - DV feasibility;
  - the signed attribution attestation;
  - the Experiment E commands, with the H1, H3 and H4 analysis code they need;
  - the owner decisions listed in `docs/audit/owner_decisions_needed_before_annotation_and_F1.md`;
  - **explicit owner approval**.
- **When approved:** the owner commits `docs/freeze/pretest_freeze.json` (protocol Stage F1 items 1–9) and tags the commit `phase3-pretest-freeze`. No assistant creates that record or tag on its own.

## Phase 10: test-split fetch and annotation (after F1)

| Pre-fetch check | How |
|---|---|
| F1 genuinely complete | the tag `phase3-pretest-freeze` exists and points at a commit whose `docs/freeze/pretest_freeze.json` hashes match the working tree |
| Approved commit and manifest hashes | compare `benchmark/real/manifest.json` and the item-2 hashes with the freeze record |
| Test-split access rules | protocol Sec. 6 "Between F1 and F2": frozen batch run only; no manual scanner use (self-attested) |
| Attribution isolation | `pool_sources` written to the sealed directory (TB05 asks for one named path; owner decision) |
| Forbidden-token safeguards | `tests/test_forbidden_gate.py`, `tests/test_g05_g06_forbidden_gate.py` (pass at 1cdc2d7) |

Then the owner fetches the pinned test commits (`scripts/fetch_pinned.py`), runs the frozen batch, builds candidate orders, and annotates per the guide. The test re-label follows ≥ 14 days after the last test primary label (enforced by `reliability.py`).

## Phase 11: F2 label freeze (explicit approval gate)

The F2 package needs:
- complete annotation records and the ledger heads;
- unresolved cases (with the bounding of protocol Sec. 5.6);
- the exclusion log and execution failures;
- annotation provenance;
- the reliability analysis (intra-rater κ with CI, owner–AI agreement, AI repeat-run consistency) and the re-label dates;
- data-integrity checks (schema validation of every label; ledger chain verification) and label hashes;
- the self-attestation that sealed outputs were not opened (TA24/TB04 asks to extend it to manual scanner runs);
- owner approval.

## Phase 12: evaluation E (explicit approval gate)

One registered run after F2:
- H1a/H1b on the test labels;
- F-B (H2a, H2-3, H2-4) with matching, bootstrap, guard, gate and Holm;
- H2b;
- F-A (exact McNemar plus Holm over the eight baselines);
- H3 (risk–coverage);
- H4 on Dataset A with the confirmed eight-member Part 1 set.

All failures and missing observations are reported, along with logs and hashes. **Prerequisite:** the E driver and the H1, H3 and H4 analysis code, written and tested before F1 on development data only.

## Phase 13: results

Only after E. Until then, the paper keeps its present status: no accuracy or hypothesis result exists.
