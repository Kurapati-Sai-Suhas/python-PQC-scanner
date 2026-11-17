# Final project demonstration

This demo shows what `pqscan` does on code. It is **not** an evaluation result: none of the scanned code is labelled, so the outputs show behaviour, not accuracy. Demonstration outputs live only in `docs/demo/` and `docs/final/demo/`. They are kept apart from benchmark data (`benchmark/`, `runs/`). No benchmark repository is scanned here.

## 1. What is shown

| Part | Input | What it demonstrates |
|---|---|---|
| A | `docs/demo/demo_repo/` (7 synthetic files, 23 sites) | Every role, tier gating, abstention, PK-encryption redesign, inventory, and the arm and threshold switches. Lecturer script in `docs/demo/presentation_script.md`. |
| B | Installed **pyca `cryptography` 47.0.0** (77 `.py` files) | Real code: Ed25519 sign/verify recommended (T2); RSA/EC sites without visible key provenance abstain (T1); a symmetric receiver is excluded |
| C | Installed **PyCryptodome 4.4.0** (228 `.py` files) | Real code at scale: 1,214 sites in 0 failures; KEM-DEM redesign for RSA PKCS#1 decryption; DSA → ML-DSA; EC-or-DSA ambiguity → abstain; key material → inventory |
| D | Validation | CycloneDX 1.6 (strict) and SARIF 2.1.0 schema validation of every CBOM and SARIF file. The CBOM is byte-identical across runs. |

Parts B and C use libraries already installed as pqscan's dependencies. Nothing is downloaded, and neither library is a development, validation or test repository. pyjwt is also installed, but it is a development repository and is excluded, because guide v1.1 Sec. 2 forbids the owner seeing tool output on a repository before labelling it.

## 2. Install (fresh environment)

PowerShell, from the repository root:

```powershell
py -3.12 -m venv $env:USERPROFILE\.venvs\pqscan-demo
& $env:USERPROFILE\.venvs\pqscan-demo\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
pqscan --version          # pqscan 0.1.0.dev0
semgrep --version         # 1.185.0 (pinned dependency)
$env:PYTHONIOENCODING = "utf-8"
```

The project venv (`.venv`, see README) works too.

## 3. Live commands (about 5 minutes)

```powershell
# A. synthetic fixture: the main walkthrough (docs/demo/commands.md has the full list)
pqscan scan docs\demo\demo_repo
pqscan scan docs\demo\demo_repo --tier-threshold T3
pqscan scan docs\demo\demo_repo --format cbom -o $env:TEMP\demo_cbom.json

# B. real code: pyca cryptography (scan a COPY of its .py files; paths in the output are relative)
$src = python -c "import cryptography, pathlib; print(pathlib.Path(cryptography.__file__).parent)"
$ver = python -c "import cryptography; print(cryptography.__version__)"
New-Item -ItemType Directory -Force $env:TEMP\pqreal\cryptography-$ver | Out-Null
Copy-Item -Recurse -Force $src $env:TEMP\pqreal\cryptography-$ver\
Get-ChildItem -Recurse -File $env:TEMP\pqreal\cryptography-$ver | Where-Object Extension -ne ".py" | Remove-Item   # .py only, as recorded
Get-ChildItem -Recurse -Directory -Filter __pycache__ $env:TEMP\pqreal\cryptography-$ver | Remove-Item -Recurse -Force
Push-Location $env:TEMP\pqreal
pqscan scan cryptography-$ver
pqscan scan cryptography-$ver --format json -o crypto_scan.json
Pop-Location

# D. validation of the recorded outputs
python docs\final\demo\validate_outputs.py
```

The recording used the project venv's cryptography **47.0.0**. A fresh `pip install` currently resolves a newer cryptography (50.0.2 on 17 Nov 2026), so a live scan of B can differ from the recorded output. For the exact recorded version, run B with the project venv (`.venv\Scripts\pqscan.exe`), or show the recorded file and screenshot 01.

**What to show and say:**
- **A.** Walk through one site per role:
  - SIGN → ML-DSA;
  - KEY_ESTABLISHMENT → ML-KEM redesign;
  - PK_ENCRYPT → "KEM + KDF + AEAD, not a drop-in replacement";
  - key material → inventory;
  - UNKNOWN → abstain.

  Then show `--tier-threshold T3` turning recommendations into abstentions.
- **B.** `ssh.py:546` and `ssh.py:562` (Ed25519 verify and sign, T2 → SIG). Contrast `ssh.py:1590` and `ssh.py:1608` (EC/RSA sign, T1 → ABSTAIN): the key arrives as a parameter, so the bounded provenance cannot see it, and pqscan abstains instead of guessing.
- **C.** Use the recorded summary (`docs/final/demo/outputs/real/pycryptodome-4.4.0_summary.txt`) or screenshot 02. Point out `Crypto/SelfTest/Cipher/test_pkcs1_15.py:53` (RSA PK_DECRYPT, T3 → KEM_DEM, "call shape cannot be preserved") and the DSA signing sites (→ ML-DSA, DSA-specific sentence).
- **D.** Every CBOM is valid CycloneDX 1.6 and every SARIF is valid 2.1.0.

**Say explicitly:**
- No labelled evaluation has been run yet, so no accuracy figure exists.
- The planned evaluation (protocol v1.0.4) is pre-registered and its statistics are calibrated. It waits for owner annotation and the F1 freeze.

## 4. Recorded outputs

| File | Content |
|---|---|
| `docs/demo/outputs/` | Part A outputs (lecturer demo, 16 Nov), with `RUN_LOG.md` |
| `docs/final/demo/outputs/real/cryptography-47.0.0_{summary.txt,scan.json,cbom.json,scan.sarif}` | Part B |
| `docs/final/demo/outputs/real/pycryptodome-4.4.0_summary.txt`, `*_{scan.json,cbom.json,scan.sarif}.gz` | Part C. The large files are gzipped deterministically; the raw SHA-256 values are in `RUN_LOG.md`. |
| `docs/final/demo/outputs/real/real_stats.json` | Counts by action, class, role, tier, algorithm, scope and Semgrep overlap |
| `docs/final/demo/outputs/real/source_manifest.json` | File counts and tree SHA-256 of the scanned library copies |
| `docs/final/demo/outputs/validation.txt` | Part D |
| `docs/final/demo/outputs/transcript.txt` | Full transcript of the recorded fresh-environment run (scratch paths redacted to `<FD>`) |
| `docs/final/demo/screenshots/*.png` | Rendered from the captured text files (not live captures); renderer `render_screenshots.py` |

## 5. Reproduce everything

Git Bash, from the repository root:

```bash
bash docs/final/demo/run_final_demo.sh "$TEMP/pqscan-final-demo"
```

The script:
- builds a **new** venv from `git archive HEAD`;
- re-runs the seven lecturer-demo commands and compares them byte-for-byte with `docs/demo/outputs/`, printing IDENTICAL or DIFFERENT per file;
- copies the installed libraries' `.py` files;
- scans them to summary, JSON, CBOM (twice, as a determinism check) and SARIF.

It takes about 5–6 minutes, most of it the pip install. Then:

```bash
.venv/Scripts/python docs/final/demo/validate_outputs.py
.venv/Scripts/python docs/final/demo/screenshots/render_screenshots.py
```

## 6. Architecture (one paragraph)

| Module | Package | Job |
|---|---|---|
| A | `pqscan/detect` | Semgrep rules: candidate detection and rule ids |
| B | `pqscan/semantic` | AST, import and alias resolution, bounded key provenance, consumer tracing; never imports or executes scanned code |
| C | `pqscan/roles` | Role and evidence tier (T0–T3) |
| D | `pqscan/policy` | Frozen policy v1.1, mapping role → target class (SIG, KEM, KEM_DEM, INVENTORY, PROTOCOL_REVIEW, NO_ACTION_HYBRID, ABSTAIN), with a tier threshold |
| E | `pqscan/export` | JSON, CycloneDX 1.6 CBOM (validated before writing; exit 3 if invalid), SARIF 2.1.0 |
| F, G | `pqscan/bench`, `pqscan/baselines` | Benchmark tooling: sampling, annotation integrity, matching, H2/F-A statistics, baselines |

Details: `docs/demo/architecture.md`.

## 7. Limits to state in any presentation

- No labelled evaluation exists. The demo shows behaviour, not accuracy.
- Parts B and C are library-internal code. The research question targets application call sites.
- PROTOCOL_CONFIG sites are not detected (readiness report W4). Finite-field DH, DSA beyond PyCryptodome, PQ/T hybrids and cross-repository flows are limited.
- Statistical calibration holds under an assumed planning model for the seven fixed test repositories. It is not evidence of real-world scanner accuracy.
