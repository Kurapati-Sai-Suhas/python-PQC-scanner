# PQScan: 10-minute demonstration guide (college submission, 20 Nov 2026)

Run these commands in PowerShell from the repository root. Install first (README, "Install"):

```powershell
uv venv .venv --python 3.12
uv pip install --python .venv/Scripts/python.exe -e ".[bench,dev]"
```

## 1. Show that the tool works (about 3 minutes)

```powershell
.venv\Scripts\pqscan --version
.venv\Scripts\pqscan scan docs\demo\demo_repo
```

Expected (recorded in `docs/demo/outputs/01_summary.txt`):
- 7 files and 23 sites;
- 20 RECOMMEND, 1 FLAG_NO_TARGET and 2 ABSTAIN;
- target classes SIG 8, KEM 6, KEM_DEM 6, INVENTORY 1 and ABSTAIN 2.

Points to make:
- **Role, not algorithm name.** `signing_service.py` RSA sites become `SIG` (ML-DSA, FIPS 204). `envelope.py` RSA decryption becomes `KEM_DEM` (KEM + KDF + AEAD redesign, SP 800-227), never a drop-in replacement.
- **Abstention.** In `ambiguous.py`, line 19 is UNKNOWN and abstains; line 15 has evidence tier T0, below the T2 threshold, and abstains.
- **Static only.** The scanned code is never imported or executed.

## 2. Show the three export formats (about 2 minutes)

Write to a scratch folder, so the committed records are not overwritten:

```powershell
.venv\Scripts\pqscan scan docs\demo\demo_repo --format json  -o $env:TEMP\scan.json
.venv\Scripts\pqscan scan docs\demo\demo_repo --format cbom  -o $env:TEMP\cbom.json
.venv\Scripts\pqscan scan docs\demo\demo_repo --format sarif -o $env:TEMP\scan.sarif
```

- **JSON:** the full evidence trail for each site.
- **CBOM:** CycloneDX 1.6, validated before it is written; an invalid CBOM gives exit code 3.
- **SARIF:** version 2.1.0.

Committed examples: `docs/demo/outputs/02_scan.json`, `03_cbom.json`, `04_scan.sarif`.

## 3. Show the evidence gate (about 2 minutes)

```powershell
.venv\Scripts\pqscan scan docs\demo\demo_repo --tier-threshold T3
.venv\Scripts\pqscan scan docs\demo\demo_repo --arm method-only
```

- A stricter threshold gives more abstentions.
- The method-only ablation arm shows what name-only evidence gives.

## 4. Show verification (about 3 minutes)

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\python docs\paper\verify_evidence.py
.venv\Scripts\python scripts\f1_readiness.py
```

- **Tests:** 775 passed, 1 skipped at commit `9f3bea9` and later. In a fresh clone without the pinned repository checkouts, 2 more tests skip.
- **Evidence checks:** 112 values, 0 failed.
- **F1 readiness:** the checklist reports **NOT READY** and lists every missing prerequisite. This is the honest research status.

## What NOT to claim

- **No accuracy figures.** No labels exist, so there are no accuracy, precision, recall or hypothesis results.
- **No validated calibration.** The statistics were calibrated in simulation under an assumed model, for fixed repositories only. The random-repository scenario (S16) fails the adopted criterion, so F1 is blocked (`docs/audit/ta01_s16_historical_verification.md`).
- **No human review.** The specification reviews were AI reviews. The external human review is pending.
