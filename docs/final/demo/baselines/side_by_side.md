# Baseline side-by-side on the synthetic demo fixture (demonstration, not evaluation)

**What this is.** Six pinned baseline tools and four pqscan arms were run on the **synthetic** lecturer-demo fixture (`docs/demo/demo_repo/`, 7 files) with the project's batch runner. Each tool was at its pinned commit (`benchmark/baselines_manifest.json`).

**What this is not.**
- The fixture has **no human labels**, so nothing below is scored as correct or incorrect. Any correctness reading against the fixture's designed intent (`docs/demo/expected_outputs.md`) is illustrative only.
- No development, validation or test repository output is shown here (annotation guide v1.1 Sec. 2).

**Reproduce:**

```bash
# make a directory containing a copy of docs/demo/demo_repo, then:
.venv/Scripts/python -m pqscan.bench.batch --tools-dir .cache/baselines --repos-dir <dir> --out <out> --pqscan-arms "full,method+args+recv,method+args,method-only"
.venv/Scripts/python docs/final/demo/baselines/side_by_side.py <out> <dir>
```

Run on 18 Nov 2026. Raw tool outputs are not committed: they embed local scratch paths. The table below is regenerated exactly by the second command.

## Execution

| Method | Status | Exit code | Seconds | Files |
|---|---|---|---|---|
| pqcheck | ok | 1 | 5.0 | {'processed': 7} |
| pqc-audit | ok | 0 | 0.9 | {'processed': 7} |
| PostQuant | ok | 1 | 0.9 | {'processed': 7} |
| qsafe | ok | 0 | 0.4 | {'processed': 7} |
| QSA-regex | ok | 0 | 56.0 | {'processed': 7} |
| pqblocks-scan | ok | 0 | 0.5 | {'processed': 7} |
| pqscan:full | ok | 0 | 9.5 | {'processed': 7} |
| pqscan:method+args+recv | ok | 0 | 9.1 | {'processed': 7} |
| pqscan:method+args | ok | 0 | 9.8 | {'processed': 7} |
| pqscan:method-only | ok | 0 | 9.4 | {'processed': 7} |

Not run:
- CBOMkit (sonar-cryptography): not run by owner decision D4 = A (2026-11-14): inventory tool without per-site migration advice; supports pyca but not PyCryptodome; never scored on recommendations; reported as not run in every table (docs/implementation/cbomkit_route.md, docs/review/owner_decision_package.md).
- Mehl ESEM 2026 scanner: Zenodo record 10.5281/zenodo.19634475 contains results only, no scanner source; repository-level comparison only

Python 3.12.10 � Windows-11-10.0.26300-SP0 � created 2026-11-18T05:41:21+00:00

## Per-site side-by-side

Threshold of the pqscan arms in this run: T2. Cells for external tools and B1: the recommended class (SIG = signature family, KEM = KEM family, DUAL = both offered, PQC_ALREADY, 'flag only' = finding without a target, '—' = no finding at that line).

| site | pqscan role (full) | pqscan full | pqscan method+args+recv | pqscan method+args | pqscan method-only | B1-algorithm | B1-dual | pqcheck | pqc-audit | PostQuant | qsafe | QSA-regex | pqblocks-scan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ambiguous.py:15 | SIGN | ABSTAIN ABSTAIN (T0) | ABSTAIN ABSTAIN (T0) | ABSTAIN ABSTAIN (T0) | ABSTAIN ABSTAIN (T0) | DUAL | DUAL | — | — | PQC_ALREADY | — | — | — |
| ambiguous.py:19 | UNKNOWN | ABSTAIN ABSTAIN (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | KEM | DUAL | KEM | DUAL | DUAL | KEM | DUAL | DUAL |
| ambiguous.py:21 | SIGN | RECOMMEND SIG (T2) | RECOMMEND SIG (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | KEM | DUAL | KEM | — | SIG | — | KEM | — |
| ambiguous.py:22 | PK_DECRYPT | RECOMMEND KEM_DEM (T2) | RECOMMEND KEM_DEM (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | KEM | DUAL | KEM | — | flag only | — | — | — |
| ecdsa_tokens.py:9 | SIGN | RECOMMEND SIG (T3) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | SIG | DUAL | SIG | DUAL | DUAL | SIG | SIG | SIG |
| ecdsa_tokens.py:10 | SIGN | RECOMMEND SIG (T3) | RECOMMEND SIG (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | SIG | DUAL | flag only | — | SIG | SIG | SIG | — |
| envelope.py:9 | PK_DECRYPT | RECOMMEND KEM_DEM (T3) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | KEM | DUAL | KEM | DUAL | DUAL | KEM | DUAL | DUAL |
| envelope.py:11 | PK_ENCRYPT | RECOMMEND KEM_DEM (T3) | RECOMMEND KEM_DEM (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | KEM | DUAL | — | — | PQC_ALREADY | — | — | — |
| envelope.py:12 | PK_DECRYPT | RECOMMEND KEM_DEM (T3) | RECOMMEND KEM_DEM (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | KEM | DUAL | — | — | — | — | — | — |
| key_agreement.py:8 | KEY_ESTABLISHMENT | RECOMMEND KEM (T3) | RECOMMEND KEM (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | KEM | KEM | flag only | KEM | KEM | — | KEM | KEM |
| key_agreement.py:9 | KEY_ESTABLISHMENT | RECOMMEND KEM (T3) | RECOMMEND KEM (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | KEM | KEM | flag only | KEM | KEM | — | KEM | KEM |
| key_agreement.py:10 | KEY_ESTABLISHMENT | RECOMMEND KEM (T3) | RECOMMEND KEM (T2) | ABSTAIN ABSTAIN (T0) | ABSTAIN ABSTAIN (T0) | KEM | KEM | — | — | — | — | — | — |
| key_agreement.py:14 | KEY_ESTABLISHMENT | RECOMMEND KEM (T3) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | SIG | DUAL | SIG | DUAL | DUAL | SIG | SIG | — |
| key_agreement.py:15 | KEY_ESTABLISHMENT | RECOMMEND KEM (T3) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | SIG | DUAL | SIG | DUAL | DUAL | SIG | SIG | — |
| key_agreement.py:16 | KEY_ESTABLISHMENT | RECOMMEND KEM (T3) | RECOMMEND KEM (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | SIG | DUAL | flag only | — | KEM | KEM | KEM | — |
| key_inventory.py:10 | KEY_MATERIAL_ONLY | FLAG_NO_TARGET INVENTORY (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | KEM | DUAL | KEM | DUAL | DUAL | KEM | DUAL | flag only |
| legacy_pycryptodome.py:11 | SIGN | RECOMMEND SIG (T3) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | KEM | DUAL | KEM | DUAL | DUAL | KEM | DUAL | DUAL |
| legacy_pycryptodome.py:13 | SIGN | RECOMMEND SIG (T3) | RECOMMEND SIG (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | KEM | DUAL | flag only | — | SIG | — | — | — |
| legacy_pycryptodome.py:17 | PK_DECRYPT | RECOMMEND KEM_DEM (T3) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | KEM | DUAL | KEM | DUAL | DUAL | KEM | DUAL | DUAL |
| legacy_pycryptodome.py:19 | PK_ENCRYPT | RECOMMEND KEM_DEM (T3) | RECOMMEND KEM_DEM (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | KEM | DUAL | — | — | PQC_ALREADY | — | — | — |
| signing_service.py:9 | SIGN | RECOMMEND SIG (T3) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T1) | KEM | DUAL | KEM | DUAL | DUAL | KEM | DUAL | DUAL |
| signing_service.py:11 | SIGN | RECOMMEND SIG (T3) | RECOMMEND SIG (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | KEM | DUAL | flag only | — | flag only | — | — | — |
| signing_service.py:13 | VERIFY | RECOMMEND SIG (T3) | RECOMMEND SIG (T2) | ABSTAIN ABSTAIN (T1) | ABSTAIN ABSTAIN (T0) | KEM | DUAL | flag only | — | flag only | — | — | — |

Sites (of 23) at which each external tool reported anything: {"pqcheck": 18, "pqc-audit": 11, "PostQuant": 21, "qsafe": 11, "QSA-regex": 14, "pqblocks-scan": 9}

## How to read it

- **pqscan arms** run at the default threshold T2. The H2 comparisons in the protocol use the comparator arms at T0, so this table shows the arms' *evidence tier*, not the H2 setting.
- **B1-algorithm** maps by algorithm family (RSA → KEM, EC → SIG). It therefore gives KEM for RSA signing (`signing_service.py`, `legacy_pycryptodome.py:11,13`) and SIG for EC (P-384) key agreement (`key_agreement.py:14–16`).
- **B1-dual** gives DUAL for every multi-purpose algorithm. See D15 in `docs/audit/research_decisions_and_novelty.md`.
- **External tools** are shown as classified by the benchmark harness's own text classifier (`pqscan/bench/judge.py`). "PQC_ALREADY" and "DUAL" are that classifier's readings of the tool's text.
- **Coverage differs:** pqscan's full arm reports all 23 sites, and the tools report between 9 and 21 of them. Any real comparison must therefore state its coverage (F-A at natural coverage; F-B coverage-matched).
