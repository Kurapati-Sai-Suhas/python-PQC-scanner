# Demonstration-day checklist

## The day before

- [ ] Fresh venv works: follow `README.md` steps 1–4 on the demo laptop (not only the dev machine).
- [ ] `pqscan --version` → `pqscan 0.1.0.dev0`; `semgrep --version` → `1.185.0`.
- [ ] Run `pqscan scan docs\demo\demo_repo` and compare with `outputs/01_summary.txt`: same 23 lines, same
      counts (`ABSTAIN=2, FLAG_NO_TARGET=1, RECOMMEND=20`). If it differs, do not present the recorded files
      as current — find out why first.
- [ ] Run sections 5 and 7 of `commands.md` once (threshold T3, `--no-semgrep`) so first-run delays
      (antivirus scan of `semgrep.exe`) happen before the demo.
- [ ] Rehearse `presentation_script.md` with a timer (target 10 min, hard stop 12).
- [ ] Have the slides cite the base paper: Zhang, ICSE-Companion '26, DOI 10.1145/3774748.3795653.
- [ ] Copy `docs/demo/` (including `screenshots/` and `outputs/`) to a USB stick or cloud folder as a
      backup.

## 30 minutes before

- [ ] Laptop on mains power; notifications off (Focus / Do Not Disturb).
- [ ] Windows Terminal (PowerShell) open at the repository root; font size ≥ 16; window wide enough for
      the summary lines (~110 columns).
- [ ] `& $env:USERPROFILE\.venvs\pqscan-demo\Scripts\Activate.ps1` (if blocked: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`).
- [ ] `$env:PYTHONIOENCODING = "utf-8"`.
- [ ] `git status` shows nothing surprising under `docs/demo/` (the recorded outputs are unmodified).
- [ ] Editor tabs ready: `docs/demo/demo_repo/README.md`, `ambiguous.py`, `architecture.md`,
      `outputs/02_scan.json`.
- [ ] Image viewer ready with `screenshots/02_summary_default.png` and `03_summary_threshold_T3.png`
      (fallback).
- [ ] Clear the terminal (`cls`).

## During the demo

- [ ] Say once that the fixture is synthetic and that the screenshots (if used) are rendered from captured
      output.
- [ ] Only scan `docs\demo\demo_repo`. Never scan benchmark folders, `repos/`, or any held-out test
      repository.
- [ ] Write exports to `$env:TEMP`, not over `docs\demo\outputs\`.
- [ ] If Semgrep fails: add `--no-semgrep` (same sites; status `semgrep: not-run`) and say so.
- [ ] If the live run fails entirely: use the screenshots and `outputs/` files, and say they are from the
      recorded run on 2026-11-16 (`outputs/RUN_LOG.md`).
- [ ] Do not quote any Phase 3 numbers — none exist.

## Questions you may get (short, honest answers)

- *How accurate is it?* — Not measured yet; that is Phase 3, on an annotated benchmark with held-out
  repositories. The demo only shows behaviour.
- *Why not just map RSA → ML-KEM?* — Because RSA signing needs ML-DSA; see `signing_service.py` vs
  `envelope.py` in the output.
- *Why abstain instead of guessing?* — A wrong family (KEM for a signature) is harmful; abstention states the
  missing evidence so a human can decide.
- *Why is `legacy_pycryptodome.py:17` PK_DECRYPT?* — See `expected_outputs.md` §1.7: the rule falls back on
  the key being private; same KEM_DEM target, imprecise label.
- *Does it run the code?* — No. `ast` and Semgrep only; per-file worker processes with time limits.

## Afterwards

- [ ] Do not commit anything regenerated during the live demo over the recorded `outputs/` files.
- [ ] Note any question you could not answer for the project log.
