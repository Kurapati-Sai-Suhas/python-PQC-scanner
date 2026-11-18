# Pre-F1 run specification (owner decisions on executing protocol v1.0.4)

**Machine-readable form:** `run_specification_pre_f1.json`. The JSON is authoritative for method identifiers. `tests/test_run_specification.py` checks it against the code.

**Status: pre-F1.**
- This is **not** part of the v1.0.4 adoption record. `adoption_record_v1.0.4.json` and every adopted document are unchanged.
- At F1, both files are hashed into `docs/freeze/pretest_freeze.json`: protocol "Stage F1", item 4 (baseline manifest) and item 7 (planned comparisons with their families).
- After F1 they may not change (protocol: "no change to … the baseline set or the analysis plan may influence Experiment E").

## Recorded owner decisions

| Id | Date | Decision |
|---|---|---|
| D7 | 2026-11-18 | **Option A.** RQ kept verbatim. F-B (H2a; H2-3, H2-4) compares at **matched recommendation volume** against the method/argument arms. F-A compares at **natural coverage** against the algorithm-name mapping, the method/argument-only mapping and the external tools. Every F-A finding is described as a natural-coverage comparison; no claim of superior correctness over algorithm-family baselines at comparable coverage. |
| D15 | 2026-11-18 | **`pqscan:B1-algorithm` is the single "simple algorithm-name mapping" in F-A**, using the mappings already in `pqscan/baselines/simple.py` (`ALG_RULE`, unchanged). **`pqscan:B1-dual` is descriptive only, outside F-A**, because it emits DUAL recommendations rather than a migration choice. The scanner is not modified or rebuilt. |

## Family F-A as it will be run (confirmatory; natural coverage)

| | Method identifier | Note |
|---|---|---|
| System | `pqscan:B4-full-T2` | `full` arm, τ = T2 (`pqscan/bench/fa.py` `SYSTEM`) |
| Baseline 1–6 | `pqcheck`, `pqc-audit`, `PostQuant`, `qsafe`, `QSA-regex`, `pqblocks-scan` | pinned in `benchmark/baselines_manifest.json` |
| Baseline 7 | `pqscan:B1-algorithm` | RSA → KEM, EC → SIG, X25519/X448/XDH/DH → KEM, Ed25519/Ed448/EdDSA/DSA → SIG, unresolved → DUAL |
| Baseline 8 | `pqscan:B2-method-args` | the method/argument-only mapping (`method+args` arm, always recommend) |

**Procedure (analysis plan Sec. 9, unchanged):**
- one-sided exact McNemar on both-ran sites;
- Holm across the baselines that ran, one-sided α = 0.025;
- ≤ 8 members, as the protocol requires;
- coverage printed with every result.

**Not run / not scored:**
- CBOMkit: D4 = A.
- Mehl ESEM 2026 scanner: D14 pending; not in F-A.

**Descriptive only:** `pqscan:B1-dual`.

## Family F-B (confirmatory; matched recommendation volume; unchanged)

| Comparison | Provenance-aware arm | Comparator |
|---|---|---|
| H2-1 (H2a) | `B3-full-noabst` | `B2-method-args` |
| H2-3 | `B3-full-noabst` | `method-args-recv-T0` |
| H2-4 | `B3-full-noabst` | `method-only-T0` |

Holm, m = 3, over guarded p-values, one-sided α = 0.025 (identifiers from `pqscan/baselines/simple.py` `H2_COMPARISONS`). H2b remains exploratory and outside error control.

## What this record does not change

- Protocol v1.0.4, annotation guide v1.1, analysis plan v1.0.
- All thresholds and decision rules.
- The F-A / F-B methodology.
- The baseline manifest.
- The test-split safeguards: `scripts/fetch_pinned.py --include-test` refuses until the F1 record and tag exist.
