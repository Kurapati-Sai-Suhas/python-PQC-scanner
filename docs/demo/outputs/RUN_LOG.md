# Run log — demonstration outputs

Every file in this folder (except this log) was written by the commands below, unedited. The complete
verbatim transcript, with each command line, start time (UTC), exit code and wall time, is
`raw_run_transcript.txt`.

## When and where

| Item | Value |
|---|---|
| Run date/time | 2026-11-16, first command 05:55:58 UTC, last command 05:56:26 UTC (11:25–11:26 local, UTC+05:30) |
| Machine | Windows 11 Home, `ver` = 10.0.26300.9974 |
| Working directory | repository root (`commands.md` paths are relative to it) |
| Scanned folder | `docs/demo/demo_repo/` only (7 synthetic files). No other repository was fetched, cloned or scanned. |

## Environment (fresh virtual environment, created for this run)

| Component | Version | How it was obtained |
|---|---|---|
| Python | 3.12.10 | `py -3.12 -m venv demo-venv` (new, empty venv outside the repository) |
| pip | 26.3 | `python -m pip install --upgrade pip` (venv started with 25.0.1) |
| pqscan | 0.1.0.dev0 | `python -m pip install -e <snapshot>` where `<snapshot>` is `git archive phase2-complete pqscan pyproject.toml README.md` extracted to a scratch folder (tag object `b8b8f72e`, commit `81f561e3`) |
| Semgrep | 1.185.0 | pinned dependency of pqscan, installed by the same command |
| cyclonedx-python-lib | 11.12.0 | pinned dependency |
| jsonschema / PyYAML / typer / pydantic | 4.25.1 / 6.0.3 / 0.29.1 / 2.14.3 | dependencies resolved by pip on the run date |

The transcript shows that `pqscan` was imported from the tag snapshot, not from the working tree
(`python -I -c "import pqscan; print(pqscan.__file__)"`). For reference, `git diff --stat phase2-complete HEAD
-- pqscan pyproject.toml` on the run date listed only three added files under `pqscan/bench/` (Phase 3
benchmark tooling); the scanner modules (detect, semantic, roles, policy, export, pipeline, cli) were
identical, so an editable install of the current checkout produces the same scanner behaviour.

`PYTHONIOENCODING=utf-8` was set for the run (see troubleshooting in `../expected_outputs.md`).

## Commands and outputs

`pqscan` below is the venv's `Scripts\pqscan.exe`; `semgrep` is the venv's `Scripts\semgrep.exe`.

| # | Command | Output file | Exit |
|---|---|---|---|
| 0 | `python --version`; `pqscan --version`; `semgrep --version`; package versions | `raw_run_transcript.txt` | 0 |
| 1 | `pqscan scan docs/demo/demo_repo` | `01_summary.txt` | 0 |
| 2 | `pqscan scan docs/demo/demo_repo --format json -o docs/demo/outputs/02_scan.json` | `02_scan.json` | 0 |
| 3 | `pqscan scan docs/demo/demo_repo --format cbom -o docs/demo/outputs/03_cbom.json` | `03_cbom.json` (validated against CycloneDX 1.6 by pqscan before writing; exit 3 otherwise) | 0 |
| 4 | `pqscan scan docs/demo/demo_repo --format sarif -o docs/demo/outputs/04_scan.sarif` | `04_scan.sarif` | 0 |
| 5 | `pqscan scan docs/demo/demo_repo --tier-threshold T3` | `05_summary_threshold_T3.txt` | 0 |
| 6 | `pqscan scan docs/demo/demo_repo --arm method-only` | `06_summary_arm_method-only.txt` | 0 |
| 7 | `pqscan scan docs/demo/demo_repo --no-semgrep` | `07_summary_no-semgrep.txt` | 0 |
| 8 | (from `docs/demo/demo_repo`) `semgrep --config <pqscan rules dir> --json --quiet --metrics=off --no-git-ignore --max-target-bytes 2000000 --timeout 30 --disable-version-check ambiguous.py ecdsa_tokens.py envelope.py key_agreement.py key_inventory.py legacy_pycryptodome.py signing_service.py` | `08_semgrep_raw.json` | 0 |

No command wrote anything to stderr. Each scan took 3–5 s wall time, most of it Semgrep start-up
(command 7, without Semgrep, took about 1 s).

### Notes on command 8 (raw Semgrep)

Command 8 reproduces the Semgrep call that `pqscan/detect/runner.py` makes (same flags, same rules, same
files) so the audience can see Module A's raw output. Two differences from the call inside the pipeline:
the pipeline passes absolute file paths and runs from the scan root, while command 8 passes the file names
relative to `docs/demo/demo_repo`. Semgrep prefixes each `check_id` with the dotted path of the rules
directory (here the scratch-folder path of the tag snapshot, which includes the local user folder);
`pqscan` strips that prefix and keeps only the rule id (e.g. `pqscan.pyca.rsa.keygen`). On another machine
the prefix will differ. Semgrep CE without a login prints `"requires login"` in place of the matched
source lines; that is Semgrep's behaviour, not redaction by us.

## Reproducibility checks

- Command 3 was run a second time at 05:57:24 UTC into a scratch file; SHA-256 of both CBOMs was identical
  (`83e3a46a…b2b9e37d`). The CBOM contains no timestamp by default, so it is byte-identical across runs.
- `07_summary_no-semgrep.txt` lists exactly the same 23 sites, roles, tiers and actions as `01_summary.txt`;
  only `semgrep: not-run` differs. Module B finds sites independently of Semgrep; Semgrep's rule ids are
  joined to them by (file, line) in the JSON/CBOM/SARIF.

## SHA-256 of the output files (as written by the run)

```
d2115d05286849754b47bd10bf16ddde5c47e8a94a82c9d7689059d14e07d480  01_summary.txt
147690919d1f6c0eefd467476540071b00d74486084f28c43994ab910c227542  02_scan.json
83e3a46a16b9688e6bb49f9aacd5c394e909cea0a42296f54a1e451bb2b9e37d  03_cbom.json
a0b6200e7f7912eb8b2618fa19c793643ba34890898e152530fa045e14124409  04_scan.sarif
421ff1893f4cadf5d392c21a360e343bb5a5fb7e25e6cdb4faf905dd6c68e907  05_summary_threshold_T3.txt
ecb54023d5a325781f836c624c508c484fc3f3feae232e5279afbea03ef8cfd5  06_summary_arm_method-only.txt
a6113c3af97603328d88f3536d4c44b421cfd7111b723e69cbffcda3ef620c21  07_summary_no-semgrep.txt
9883e7eb75ded37bea3ff88c7d80328d4b518afdbd198e2d06ffee12ecdb7f66  08_semgrep_raw.json
246cbf2d0b4da84f29d7f571f36dde4cbd8b193de39c0953627ea98c87b295ae  raw_run_transcript.txt
```

Line endings: the files were written on Windows. If git converts line endings on commit or checkout, the
hashes of the text files can change while the content stays the same; compare with
`git config core.autocrlf` in mind.

## What did not work / caveats

- First attempt (05:54 UTC) was discarded and re-run: the helper commands `python -c "…"` that print the
  package path and rules directory were run without `-I`, so Python put the current directory (the
  repository root) on `sys.path` and those helper lines reported the working-tree package instead of the
  tag snapshot. The scans themselves (`pqscan.exe` does not put the current directory on `sys.path`) were
  not affected: files 01–07 of the discarded run had exactly the same byte sizes as the kept ones. The raw
  Semgrep file of the discarded run had used the working tree's rules folder (identical rules, different
  `check_id` prefix, hence a different size). All outputs were deleted and regenerated with `python -I` so
  the record is unambiguous. Only the second run is kept.
- Nothing else failed.

## Redaction of local paths (2026-11-16, before committing to the public repository)

Two files contained the absolute path of the local temporary folder used for the run (it includes the Windows user
name). In those two files, and only there, that folder prefix was replaced by `<SCRATCH>`; nothing else was changed.
SHA-256 of the unredacted originals (the originals themselves were overwritten by the redaction and are not retained;
re-running `../commands.md` reproduces equivalent outputs, with the path of whatever folder is used):

| File | Original SHA-256 | Replacements |
|---|---|---|
| `raw_run_transcript.txt` | `246cbf2d0b4da84f29d7f571f36dde4cbd8b193de39c0953627ea98c87b295ae` | 17 |
| `08_semgrep_raw.json` | `9883e7eb75ded37bea3ff88c7d80328d4b518afdbd198e2d06ffee12ecdb7f66` | 25 |

`../screenshots/01_versions.png` was re-rendered from the redacted transcript with the same script and Pillow version.

## Regeneration in revision r6 (19 Nov 2026; owner decision W6; appended)

`02_scan.json`, `03_cbom.json` and `04_scan.sarif` were regenerated with the commands in `../commands.md`, because the SP 800-227 citation in the policy templates changed from "Secs. 2.1, 5.2" to "Secs. 5.2.1, 4.3". The only differences are that citation and the content-derived CBOM serial number. The four summary outputs (01, 05, 06, 07) were regenerated and are byte-identical. The previous files are in `archive/pre-r6/`. SHA-256 (as written, LF): `02_scan.json` `1e0ec61b4643faef52ff972869f750b7cc008a52faebc3702014d2848a9f9633`, `03_cbom.json` `3841cec2e77d9913536d1c695be8f5984477ba20107a12a266fb969eb432f601`, `04_scan.sarif` `2d5411e5460be4cf4159e7778163f962f38fc64f732f9da36436e53a7b0d79f8`.
