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

## Not yet done

The runner has not been run on the real development repositories with the real pinned tools in this session, because the tools are not installed in `.cache/`. This is the next step before F1, and it confirms the measured profiles still hold.
