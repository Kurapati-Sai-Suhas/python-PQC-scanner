# Demo commands (exact, in order)

Run in **PowerShell from the repository root** with the demo venv activated (see `README.md`). Without
activation, replace `pqscan` with `& $env:USERPROFILE\.venvs\pqscan-demo\Scripts\pqscan.exe` and `semgrep`
with `& $env:USERPROFILE\.venvs\pqscan-demo\Scripts\semgrep.exe`. The CLI is defined in `pqscan/cli.py`; there is one sub-command, `scan`.

The recorded results of every command are in `outputs/` (see `outputs/RUN_LOG.md`). Commands 2–4 below show
the paths that produced the recorded files. **During a live demo, write to a scratch folder instead**
(e.g. `-o $env:TEMP\03_cbom.json`) so the committed record is not overwritten.

## 0. Environment check

```powershell
python --version
pqscan --version
semgrep --version
```

Recorded: `Python 3.12.10`, `pqscan 0.1.0.dev0`, `1.185.0` (`outputs/raw_run_transcript.txt`).

Optional, shows which `pqscan` package is being used (`-I` keeps the current folder off `sys.path`):

```powershell
python -I -c "import pqscan; print(pqscan.__file__)"
```

## 1. Default scan — text summary (the main live demo)

```powershell
pqscan scan docs\demo\demo_repo
```

Recorded output: `outputs/01_summary.txt`. Defaults: `--format summary`, policy v1.1, `--tier-threshold T2`,
`--arm full`, Semgrep on. One line per site: `file:line  algorithm  role  tier  action  target-class`.

## 2. Full JSON report (evidence, decision and recommendation per site)

```powershell
pqscan scan docs\demo\demo_repo --format json -o docs\demo\outputs\02_scan.json
```

## 3. CycloneDX 1.6 CBOM

```powershell
pqscan scan docs\demo\demo_repo --format cbom -o docs\demo\outputs\03_cbom.json
```

The CBOM is validated against the CycloneDX 1.6 schema before it is written; an invalid CBOM gives exit
code 3. Add `--timestamp 2026-11-16T00:00:00Z` only if you want a timestamp recorded (omitted by default so
the file is byte-identical across runs).

## 4. SARIF 2.1.0 (for code-scanning UIs)

```powershell
pqscan scan docs\demo\demo_repo --format sarif -o docs\demo\outputs\04_scan.sarif
```

## 5. Stricter policy threshold — show tier-gated abstention

```powershell
pqscan scan docs\demo\demo_repo --tier-threshold T3
```

Recorded output: `outputs/05_summary_threshold_T3.txt`. Choices: `T0`, `T1`, `T2` (default), `T3`.

## 6. Ablation arm — method name only

```powershell
pqscan scan docs\demo\demo_repo --arm method-only
```

Recorded output: `outputs/06_summary_arm_method-only.txt`. Arms: `method-only`, `method+args`,
`method+args+recv`, `full` (default).

## 7. Without Semgrep (Module B only) — also the fallback if Semgrep is broken on demo day

```powershell
pqscan scan docs\demo\demo_repo --no-semgrep
```

Recorded output: `outputs/07_summary_no-semgrep.txt` (same sites; status line says `semgrep: not-run`).

## 8. Module A on its own — the raw Semgrep call the pipeline makes

```powershell
$rules = python -I -c "from pqscan.detect.runner import RULES_DIR; print(RULES_DIR)"
Push-Location docs\demo\demo_repo
semgrep --config $rules --json --quiet --metrics=off --no-git-ignore --max-target-bytes 2000000 --timeout 30 --disable-version-check ambiguous.py ecdsa_tokens.py envelope.py key_agreement.py key_inventory.py legacy_pycryptodome.py signing_service.py | Out-File -Encoding utf8 ..\outputs\08_semgrep_raw.json
Pop-Location
```

Same flags and rules as `pqscan/detect/runner.py`. Use `Out-File -Encoding utf8` rather than `>`: in Windows
PowerShell 5.1, `>` may write UTF-16, which some JSON viewers reject. The recorded file was produced by the
equivalent Git Bash command in `outputs/RUN_LOG.md`; this PowerShell form was also run on the same day and
returned the same 25 Semgrep results (exit 0). To keep the recorded file intact, write to a different name.

The same holds for the default scan: running `pqscan scan docs\demo\demo_repo` from PowerShell on the run
date produced output identical to `outputs/01_summary.txt`.

## Other options (not used in the demo)

| Option | Effect |
|---|---|
| `--exclude-tests` | skip test files (`tests/`, `test_*.py`, `*_test.py`, `conftest.py`) |
| `--policy <yaml>` | use another policy file (the engine rejects policies that break ML-KEM/ML-DSA separation) |
| `--max-file-bytes N` | skip files larger than N bytes (default 2,000,000) |
| `--file-timeout S` | per-file analysis time limit in seconds (default 30) |
| `-v` | verbose logging |

Exit codes: `0` scan completed (with or without findings), `2` usage/input error (e.g. path is not a
directory), `3` internal failure (including a CBOM that fails schema validation).

## Re-rendering the screenshots (optional)

```powershell
py -3.12 -m pip install pillow      # only if Pillow is not already installed for that Python
py -3.12 docs\demo\screenshots\render_screenshots.py
```

Pillow is not a pqscan dependency; use any Python that has it, not the demo venv.

## Safety reminder

Only scan `docs\demo\demo_repo`. Do not point the scanner at the benchmark folders or any held-out test
repository during the demo.
