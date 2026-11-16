# pqscan — lecturer demonstration package

This folder demonstrates the **Phase 2** scanner `pqscan` (tag `phase2-complete`, version `0.1.0.dev0`) on
a small **synthetic** fixture. It uses only functionality that was verified at the Phase 2 gate. It contains
**no Phase 3 results** (none exist yet) and never touches the benchmark or the held-out test repositories.

Base paper: Lei Zhang, "Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum Cryptography
Migration", ICSE-Companion '26, pp. 402–403, DOI [10.1145/3774748.3795653](https://doi.org/10.1145/3774748.3795653).

## Package index

| File / folder | Contents |
|---|---|
| `README.md` | this file: environment setup and index |
| `demo_repo/` | **DEMONSTRATION FIXTURE — synthetic, written for this demo.** Seven small files with PyCA `cryptography` and PyCryptodome RSA/ECC usage. Scanned only, never imported or run. |
| `commands.md` | the exact commands, in demo order |
| `outputs/` | **real** outputs captured from those commands in a fresh virtual environment, saved verbatim; `outputs/RUN_LOG.md` records date/time, versions and exit codes |
| `expected_outputs.md` | walk-through of the real outputs: ML-KEM vs ML-DSA per site and why, abstentions, tier-threshold effect, troubleshooting |
| `screenshots/` | PNG images **rendered from the captured output files** (not screen captures); `screenshots/CAPTIONS.md` names the source log of each |
| `architecture.md` | one-page architecture, derived from the code |
| `presentation_script.md` | 8–12 minute talk script with timings |
| `checklist.md` | demonstration-day checklist |

## Clean environment setup (Windows 11, Python 3.12)

The commands below are for **PowerShell**, run from the repository root (the folder that contains
`pyproject.toml`). They create a fresh virtual environment that is separate from the development `.venv`.
The recorded run used exactly this route (`py -3.12 -m venv`, `pip install -e`), with the venv in a scratch
folder; see `outputs/RUN_LOG.md`.

### 1. Check Python 3.12

```powershell
py -3.12 --version
```

Expect `Python 3.12.x`. If the launcher says 3.12 is not installed, install Python 3.12 from python.org
(tick "Add python.exe to PATH" is optional; the `py` launcher is enough). `pqscan` requires Python ≥ 3.12.

### 2. Create and activate a fresh virtual environment (outside the repository)

The venv is created in your user folder, not in the repository, so it can never be committed by accident
(`.gitignore` only covers `.venv/`, `venv/` and `env/`).

```powershell
py -3.12 -m venv $env:USERPROFILE\.venvs\pqscan-demo
& $env:USERPROFILE\.venvs\pqscan-demo\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If activation fails with "running scripts is disabled on this system", either run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (affects this window only) or skip activation
and call the tools by full path, e.g. `& $env:USERPROFILE\.venvs\pqscan-demo\Scripts\pqscan.exe`.

### 3. Install the project in editable mode

```powershell
python -m pip install -e .
```

This installs `pqscan` and its pinned dependencies from `pyproject.toml`, **including `semgrep==1.185.0`**
(Module A). No extra packages are needed for the demo; do not add anything to `pyproject.toml`. The
download is large (Semgrep and its dependencies); allow a few minutes.

**Optional — install exactly the tagged Phase 2 code.** The recorded outputs in `outputs/` were produced
from a snapshot of tag `phase2-complete`, made read-only with `git archive` (this does not change the
checkout or `.git`):

```powershell
New-Item -ItemType Directory -Force $env:TEMP\pqscan-phase2 | Out-Null
git archive --format=zip -o $env:TEMP\pqscan-phase2.zip phase2-complete pqscan pyproject.toml README.md
Expand-Archive -Force $env:TEMP\pqscan-phase2.zip $env:TEMP\pqscan-phase2
python -m pip install -e $env:TEMP\pqscan-phase2
```

Keep running the demo commands from this checkout (the tag does not contain `docs/demo/`). On the run
date the scanner modules at the tag and on the current branch were identical (`outputs/RUN_LOG.md`), so
either install gives the same results.

### 4. Verify Semgrep and pqscan

```powershell
pqscan --version
semgrep --version
```

Expect `pqscan 0.1.0.dev0` and `1.185.0`. `pqscan` looks for `semgrep.exe` next to the running Python first
(the venv's `Scripts` folder), then on `PATH`. If Semgrep cannot be found the scan still completes, but the
summary shows `semgrep: failed: …` and no Semgrep rule ids are joined; see the troubleshooting section of
`expected_outputs.md`.

Alternative with `uv` (as in the project README):

```powershell
uv venv $env:USERPROFILE\.venvs\pqscan-demo --python 3.12
uv pip install --python $env:USERPROFILE\.venvs\pqscan-demo\Scripts\python.exe -e .
```

### 5. Run the demo

Follow `commands.md`. The first command is:

```powershell
pqscan scan docs\demo\demo_repo
```

## Integrity notes

- Everything in `outputs/` was produced by actually running the commands in `commands.md`; nothing was
  edited by hand. `RUN_LOG.md` gives the exact environment.
- The screenshots are images rendered from those captured text files by a small script
  (`screenshots/render_screenshots.py`); they are not photographs of a live terminal.
- The fixture is synthetic. Results on it show what the scanner *does*; they are not evaluation results and
  say nothing about accuracy on real projects. That is Phase 3's job.
