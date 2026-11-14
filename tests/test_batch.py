"""Batch runner (checklist C5): success, failure, timeout, not-installed and unpinned cases, using stub tools.

Real baseline tools are not needed: each stub is a small Python script run through the `{python}` placeholder.
The failure fixture repository (`tests/fixtures/baseline_errors/repos/errrepo`) supplies one valid, one
syntax-error, one non-UTF-8 and one null-byte file.
"""
from __future__ import annotations
import json, shutil, textwrap
from pathlib import Path
import pytest
from pqscan.bench import batch
from pqscan.bench.batch import (KNOWN_SKIP, LOGGED_FAILURE, PROCESSED, RUN_FAILED, run_batch, run_external,
                                run_pqscan, main)
from pqscan.bench.run import judge_external

ERRREPO = Path(__file__).parent / "fixtures" / "baseline_errors" / "repos" / "errrepo"
FILES = {"good.py", "syntax_error.py", "latin1.py", "nullbyte.py"}

STUB = textwrap.dedent('''
    import json, os, sys, time
    mode, repo = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    files = sorted(f for f in os.listdir(repo) if f.endswith(".py"))
    if mode == "qsafe-ok":                       # report on stdout (manifest "stdout")
        print(json.dumps({"findings": [{"file": f, "line": 4, "migration": "Replace with ML-DSA",
                                        "algorithm": "RSA", "context": "sign"} for f in files]}))
    elif mode == "pqblocks-abort":               # pqblocks-scan 0.1.0 behaviour: abort, no report
        for f in files:
            if b"\\x00" in open(os.path.join(repo, f), "rb").read():
                print(f"Scan error: {os.path.join(repo, f)}: null byte")
                sys.exit(2)
    elif mode == "pqblocks-partial":             # logs one file as failed but still writes a report
        print(f"Scan error: {os.path.join(repo, 'syntax_error.py')}: invalid syntax")
        res = [{"ruleId": "rsa", "message": {"text": "Replace with ML-DSA-65"},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": f}, "region": {"startLine": 4}}}]}
               for f in files if f != "syntax_error.py"]
        open(out, "w").write(json.dumps({"version": "2.1.0", "runs": [{"results": res}]}))
    elif mode == "sleep":
        print("partial", flush=True); time.sleep(30)
    elif mode == "crash":
        print("Traceback: boom", file=sys.stderr); sys.exit(1)
''')


def _manifest(tmp: Path, tools: dict) -> Path:
    m = tmp / "manifest.json"
    m.write_text(json.dumps({"tools": tools, "not_runnable": {"CBOMkit": "needs Docker"}}), encoding="utf-8")
    return m


def _tool_dir(tmp: Path, name: str) -> Path:
    d = tmp / "tools" / name
    d.mkdir(parents=True)
    (d / "stub.py").write_text(STUB, encoding="utf-8")
    return d


def _tool(mode: str, stdout: str | None = None, out_arg: str | None = None, profile: dict | None = None) -> dict:
    run = ["{python}", "{tooldir}/stub.py", mode, "{repo}"] + ([out_arg] if out_arg else [])
    t = {"kind": "command", "run": run, "file_failure_profile": profile or {"silently_skips": [], "whole_run_fails_on": [], "error_log": None}}
    if stdout:
        t["stdout"] = stdout
    return t


def _sites():
    return [{"site_id": f, "repo": "errrepo", "file": f, "line_start": "4", "line_end": "4", "method": "sign",
             "gt_role": "SIGN", "assessability": "DETERMINATE", "eligible": "yes", "hybrid_component": "no"} for f in sorted(FILES)]


def _repo(tmp: Path) -> Path:
    r = tmp / "repos" / "errrepo"
    shutil.copytree(ERRREPO, r)
    return r


# ------------------------------------------------------------------ success
def test_successful_run_writes_report_log_and_run_record(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    t = _tool("qsafe-ok", stdout="{out}/qsafe_{name}.json")
    rec = run_external("qsafe", t, _tool_dir(tmp_path, "qsafe"), repo, "errrepo", out, timeout=60)
    assert rec["run_status"] == "ok" and rec["exit_code"] == 0 and not rec["timed_out"]
    assert (out / "qsafe_errrepo.json").exists() and len(rec["output_sha256"]) == 64
    assert (out / "qsafe_errrepo.log").read_text(encoding="utf-8").startswith("# command:")
    on_disk = json.loads((out / "qsafe_errrepo.run.json").read_text(encoding="utf-8"))
    assert set(on_disk["files"]) == FILES and on_disk["file_status_counts"] == {PROCESSED: 4}
    assert {v["condition"] for v in on_disk["files"].values()} == {"ok", "syntax-error", "non-utf8", "null-byte"}
    assert rec["elapsed_s"] >= 0
    rows = judge_external(_sites(), out, "qsafe", repo.parent)
    assert {r["judgment"] for r in rows} == {"CORRECT"}


# ------------------------------------------------------------------ failures are never misses
def test_whole_run_abort_is_execution_failure_for_every_file(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    prof = {"silently_skips": [], "whole_run_fails_on": ["syntax-error", "null-byte"], "error_log": "^Scan error: (?P<path>.+?): "}
    t = _tool("pqblocks-abort", out_arg="{out}/pqblocks_{name}.sarif", profile=prof)
    rec = run_external("pqblocks-scan", t, _tool_dir(tmp_path, "pqblocks-scan"), repo, "errrepo", out, timeout=60)
    assert rec["run_status"] == "failed" and rec["exit_code"] == 2 and rec["output_sha256"] is None
    assert rec["file_status_counts"] == {RUN_FAILED: 4}
    assert "Scan error:" in (out / "pqblocks_errrepo.log").read_text(encoding="utf-8")
    rows = judge_external(_sites(), out, "pqblocks-scan", repo.parent)
    assert {r["judgment"] for r in rows} == {"EXECUTION_FAILURE"}


def test_logged_file_failure_is_recorded_per_file_and_judged_as_execution_failure(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    prof = {"silently_skips": [], "whole_run_fails_on": [], "error_log": "^Scan error: (?P<path>.+?): "}
    t = _tool("pqblocks-partial", out_arg="{out}/pqblocks_{name}.sarif", profile=prof)
    rec = run_external("pqblocks-scan", t, _tool_dir(tmp_path, "pqblocks-scan"), repo, "errrepo", out, timeout=60)
    assert rec["run_status"] == "ok"
    assert rec["files"]["syntax_error.py"]["status"] == LOGGED_FAILURE
    assert rec["files"]["good.py"]["status"] == PROCESSED
    rows = {r["site_id"]: r["judgment"] for r in judge_external(_sites(), out, "pqblocks-scan", repo.parent)}
    assert rows["syntax_error.py"] == "EXECUTION_FAILURE" and "MISSED" not in rows.values()


def test_silent_skip_profile_marks_files_not_missing(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    prof = {"silently_skips": ["syntax-error", "null-byte"], "whole_run_fails_on": [], "error_log": None}
    t = _tool("qsafe-ok", stdout="{out}/qsafe_{name}.json", profile=prof)
    rec = run_external("qsafe", t, _tool_dir(tmp_path, "qsafe"), repo, "errrepo", out, timeout=60)
    assert rec["files"]["nullbyte.py"]["status"] == KNOWN_SKIP
    assert rec["files"]["syntax_error.py"]["status"] == KNOWN_SKIP
    assert rec["files"]["latin1.py"]["status"] == PROCESSED


def test_stale_output_is_removed_before_a_failing_run(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    stale = out / "qsafe_errrepo.json"
    stale.write_text('{"findings": [{"file": "good.py", "line": 4, "migration": "ML-DSA", "algorithm": "RSA", "context": "x"}]}')
    t = _tool("crash", out_arg="{out}/unused")       # writes no report; exit 1
    rec = run_external("qsafe", t, _tool_dir(tmp_path, "qsafe"), repo, "errrepo", out, timeout=60)
    assert rec["run_status"] == "failed" and not stale.exists()
    assert "Traceback: boom" in (out / "qsafe_errrepo.log").read_text(encoding="utf-8")
    assert {r["judgment"] for r in judge_external(_sites(), out, "qsafe", repo.parent)} == {"EXECUTION_FAILURE"}


def test_timeout_kills_tool_and_discards_partial_report(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    t = _tool("sleep", stdout="{out}/qsafe_{name}.json")
    rec = run_external("qsafe", t, _tool_dir(tmp_path, "qsafe"), repo, "errrepo", out, timeout=2)
    assert rec["timed_out"] and rec["run_status"] == "failed"
    assert not (out / "qsafe_errrepo.json").exists()
    assert rec["file_status_counts"] == {RUN_FAILED: 4}


# ------------------------------------------------------------------ unsupported / not installed / unpinned
def test_missing_tool_is_recorded_not_run(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    rec = run_external("qsafe", _tool("qsafe-ok", stdout="{out}/qsafe_{name}.json"), tmp_path / "tools" / "absent",
                       repo, "errrepo", out, timeout=60)
    assert rec["run_status"] == "failed" and "not installed" in rec["error"] and rec["command"] is None
    assert "(not run)" in (out / "qsafe_errrepo.log").read_text(encoding="utf-8")


def test_unpinned_checkout_is_refused(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    t = _tool("qsafe-ok", stdout="{out}/qsafe_{name}.json")
    t["commit"] = "0" * 40
    rec = run_external("qsafe", t, _tool_dir(tmp_path, "qsafe"), repo, "errrepo", out, timeout=60)
    assert rec["run_status"] == "failed" and "pinned commit" in rec["error"]
    ok = run_external("qsafe", t, tmp_path / "tools" / "qsafe", repo, "errrepo", out, timeout=60, allow_unpinned=True)
    assert ok["run_status"] == "ok"


def test_python_tool_without_its_virtualenv_is_not_installed(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    t = {"kind": "python", "run": ["pqcheck", "scan", "{repo}"], "file_failure_profile": {}}
    rec = run_external("pqcheck", t, _tool_dir(tmp_path, "pqcheck"), repo, "errrepo", out, timeout=60)
    assert rec["run_status"] == "failed" and "not installed" in rec["error"]


# ------------------------------------------------------------------ pqscan arms
def test_pqscan_arm_records_its_own_execution_failures(tmp_path):
    repo, out = _repo(tmp_path), tmp_path / "out"
    out.mkdir()
    rec = run_pqscan("full", repo, "errrepo", out, timeout=300, extra_args=["--no-semgrep"])
    assert rec["run_status"] == "ok" and rec["exit_code"] == 0
    assert rec["files"]["syntax_error.py"]["status"] == LOGGED_FAILURE
    assert rec["files"]["nullbyte.py"]["status"] == LOGGED_FAILURE
    assert rec["files"]["good.py"]["status"] == PROCESSED
    assert (out / "pqscan_full_errrepo.json").exists() and (out / "pqscan_full_errrepo.log").exists()


# ------------------------------------------------------------------ batch level
def test_batch_summary_and_exit_code(tmp_path):
    repo = _repo(tmp_path)
    out = tmp_path / "out"
    _tool_dir(tmp_path, "qsafe")
    _tool_dir(tmp_path, "pqblocks-scan")
    prof = {"silently_skips": [], "whole_run_fails_on": ["null-byte"], "error_log": "^Scan error: (?P<path>.+?): "}
    m = _manifest(tmp_path, {"qsafe": _tool("qsafe-ok", stdout="{out}/qsafe_{name}.json"),
                             "pqblocks-scan": _tool("pqblocks-abort", out_arg="{out}/pqblocks_{name}.sarif", profile=prof)})
    s = run_batch(tmp_path / "tools", {"errrepo": repo}, out, ["qsafe", "pqblocks-scan"], [], 60, m)
    assert [(r["method"], r["run_status"]) for r in s["runs"]] == [("qsafe", "ok"), ("pqblocks-scan", "failed")]
    assert s["not_run"] == {"CBOMkit": "needs Docker"} and len(s["manifest_sha256"]) == 64
    assert json.loads((out / "batch_summary.json").read_text(encoding="utf-8"))["runs"][1]["exit_code"] == 2
    code = main(["--tools-dir", str(tmp_path / "tools"), "--repos-dir", str(repo.parent), "--out", str(out),
                 "--tools", "qsafe,pqblocks-scan", "--pqscan-arms", "", "--manifest", str(m)])
    assert code == 1          # at least one run failed


def test_unknown_tool_is_rejected(tmp_path):
    m = _manifest(tmp_path, {})
    with pytest.raises(SystemExit):
        run_batch(tmp_path / "tools", {"errrepo": _repo(tmp_path)}, tmp_path / "out", ["nope"], [], 60, m)


def test_file_inventory_skips_hidden_and_build_dirs(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "x.py").write_text("")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "y.py").write_text("")
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "z.py").write_text("")
    assert batch.python_files(tmp_path) == ["pkg/z.py"]
