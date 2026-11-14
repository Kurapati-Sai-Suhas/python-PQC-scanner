# Baseline batch runner (checklist C5)

Module: `pqscan/bench/batch.py`. Tests: `tests/test_batch.py` (13 tests; module coverage 92%). Added 14 Nov 2026 on branch `phase3-preparation`.

## Command

```bash
.venv/Scripts/python scripts/fetch_pinned.py baselines .cache/baselines
.venv/Scripts/python -m pqscan.bench.batch --tools-dir .cache/baselines --repos-dir .cache/repos/development --out runs/development --pqscan-arms full,method+args+recv,method+args,method-only
```

The exit status is 0 only when every run produced a report.

## What it records

For every method and repository, next to the raw output named as `pqscan.bench.run.TOOL_FILES` expects:

| File | Contents |
|---|---|
| `<prefix>_<repo>.log` | command, start and end (UTC), exit status, timeout flag, elapsed seconds, the tool's stdout (unless stdout is the report) and stderr |
| `<prefix>_<repo>.run.json` | the same metadata; pinned and checked-out tool commit; repository commit; output and log SHA-256; per-file condition (`fileprobe`) and status |
| `batch_summary.json` | one record per run; Python version and platform; manifest SHA-256; tools not run and why (CBOMkit, Mehl) |

Per-file status:
- `processed`: none of the other three applies;
- `skipped-by-profile`: the file's condition is one this tool silently drops, according to its measured profile;
- `logged-failure`: the tool's own log names the file;
- `run-failed`: the tool produced no report at all.

Tools do not report per-file success, so `processed` means the tool was given the file and is not known to have failed on it.

## Safeguards against counting failures as misses

1. Any earlier report and log for the same run are deleted first, so a missing report always comes from this run, and `judge_external` turns it into EXECUTION_FAILURE for every site.
2. A timeout kills the tool and deletes any partial report.
3. A tool directory that is missing, an executable not found in the tool's own virtualenv, or a checkout that is not at the pinned commit means the tool is not run. The reason is recorded. `--allow-unpinned` exists for development only.
4. Run logs are saved under the names `logged_failures` parses (pqblocks-scan's `Scan error: <path>` lines).
5. pqscan arms run through the CLI; a file in pqscan's own `execution_failures` list is a `logged-failure`.

Tests cover each of the following with stub tools on the four-file failure fixture, and check the resulting judgments through `judge_external`:
- a successful run;
- a whole-run abort;
- a per-file logged failure with a partial report;
- silent-skip profiles;
- a stale report from an earlier run;
- a crash;
- a timeout;
- a missing tool;
- a Python tool without its virtualenv;
- an unpinned checkout;
- a pqscan arm;
- the batch summary and exit status;
- an unknown tool name;
- the file inventory.

## First real run (14 Nov 2026, development repositories, real pinned tools)

Evidence: `docs/implementation/runner_evidence/`. The 5.9 MB of raw reports per run stay in the git-ignored `runs/` folder, because the pinned rebuild reproduces them.

1. **Rebuild.** `scripts/fetch_pinned.py` rebuilt all six tools at their pinned commits and the development and validation repositories. The 7 test-split repositories were skipped, because `--include-test` was not given. Two bugs were found and fixed:
   - a relative destination produced a relative virtualenv path that broke `uv pip install` run inside the tool directory (the destination is now resolved to an absolute path);
   - a re-run failed on an existing virtualenv (`uv venv --clear`).
2. **Two full batch runs.** Each covers 6 tools and 4 pqscan arms on 4 repositories: 40 runs, all with a report.
   - pqcheck and PostQuant exit with 1 when they find something, and a report is present, so they are correctly recorded as `ok`.
   - Times range from 0.2 s to 18.7 s per run, apart from one QSA-regex run of 78.8 s (PyJWT, run 1; 2.7 s in run 2).
3. **Reconciliation with the published pilot.** The new outputs were judged with the packaged judge on the 31 pilot sites, which are at the same paramiko and python-jose commits.
   - pqcheck, pqc-audit, PostQuant, qsafe and QSA-regex: **155 of 155 judgments identical** to `docs/pilot/h1_pilot_joined.csv`, in both runs.
   - pqblocks-scan: 31 of 31 identical to the Phase 2 pilot harness.
   - No execution failures on these repositories.
4. **Real-tool failure check.** All six tools were run on the four-file failure fixture. For every tool, the sites judged EXECUTION_FAILURE are exactly the files its measured profile predicts, and **no failed file was judged MISSED**. pqblocks-scan aborted its whole run (exit 2, no report), and all four files were recorded as `run-failed`. pqscan listed the syntax-error and null-byte files in its own `execution_failures`.
5. **Reproducibility.**
   - 28 of 40 raw reports are byte-identical between the two runs, including every pqscan arm, pqcheck, QSA-regex and pqblocks-scan.
   - The other 12 (PostQuant, pqc-audit and qsafe on each repository) differ only in timestamps, scan durations and CBOM serial-number UUIDs.
   - Their parsed findings are identical, giving **40 of 40 equal findings digests**.

   As a result, the runner now records `findings_sha256`, and protocol v1.0.2 makes it the determinism criterion.

## Not yet done

- The validation split has not been run through the batch runner. It was fetched, but has no labels yet; it is run when its labels exist.
- CBOMkit is not run (checklist C3).
