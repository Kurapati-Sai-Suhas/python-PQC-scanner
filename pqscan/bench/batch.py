"""Reproducible batch runner for the pinned baseline tools and the pqscan arms (Phase 3, checklist C5).

    python -m pqscan.bench.batch --tools-dir .cache/baselines --repos-dir .cache/repos/dev --out runs/dev
           [--tools pqcheck,qsafe,...] [--pqscan-arms full,method+args] [--timeout 1800]

For every (method, repository) pair it writes, next to the method's raw output:

* `<prefix>_<repo>.log`      : command, start/end, exit status, elapsed time, the tool's stdout and stderr;
* `<prefix>_<repo>.run.json` : the same metadata, the output file's SHA-256, the pinned and checked-out
                               tool commit, and a per-file status for every Python file in the repository;
* `batch_summary.json`       : one record per run, plus the tools that were not run and why.

The file names follow `pqscan.bench.run.TOOL_FILES`, so `judge_external` finds the outputs and parses the
logs (for example pqblocks-scan's "Scan error: <path>" lines).

Rules that keep execution failures from being counted as misses:
* any earlier output for the same run is deleted before the run, so a missing report always means that
  this run produced none (judged as EXECUTION_FAILURE for every site of the repository);
* a timeout kills the tool and is recorded as a failed run;
* a tool whose checkout is missing, or not at its pinned commit, is not run, and the reason is recorded;
* per-file status uses the tool's measured failure profile (`file_failure_profile` in the manifest) and
  its own error log, never the absence of findings.

Scanned repositories are passed to the tools as paths only; this module never imports or executes them.
"""
from __future__ import annotations
import argparse, datetime as _dt, hashlib, json, os, platform, re, subprocess, sys, time
from pathlib import Path
from .fileprobe import file_condition
from .run import TOOL_FILES

PROJECT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = PROJECT / "benchmark" / "baselines_manifest.json"
PQSCAN_FILE = "pqscan_{arm}_{repo}.json"
SKIP_DIRS = {"node_modules", "__pycache__", "venv", "build", "dist"}

# per-file status values written to <prefix>_<repo>.run.json
RUN_FAILED = "run-failed"            # the tool produced no report at all
LOGGED_FAILURE = "logged-failure"    # the tool's own log names the file as failed
KNOWN_SKIP = "skipped-by-profile"    # the file's condition is one the tool silently drops (measured)
PROCESSED = "processed"              # none of the above: the tool is taken to have analysed the file


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(path: Path) -> str | None:
    if not (path / ".git").exists():
        return None
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True,
                              timeout=30, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def python_files(repo: Path) -> list[str]:
    """Every .py file under `repo` (relative, forward slashes); no symlinks, hidden or build directories."""
    out = []
    for dirpath, dirnames, filenames in os.walk(repo, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS
                             and not os.path.islink(os.path.join(dirpath, d)))
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            if fn.endswith(".py") and not p.is_symlink():
                out.append(p.relative_to(repo).as_posix())
    return out


def findings_digest(tool_name: str, out_file: Path, repo: Path) -> str | None:
    """SHA-256 of the tool's findings as parsed by its adapter (file relative to the repository, line,
    rule, text), sorted. Three pinned tools embed timestamps, durations or random serial numbers in their
    reports, so raw report hashes differ between identical runs; this digest is the determinism check."""
    from ..baselines.adapters import ADAPTERS
    if tool_name not in ADAPTERS or not out_file.exists():
        return None
    root = repo.resolve().as_posix().rstrip("/") + "/"
    rows = []
    for f in ADAPTERS[tool_name](out_file):
        path = f.file.replace("\\", "/")
        if path.startswith(root):
            path = path[len(root):]
        rows.append([path, f.line, f.rule, f.text])
    return hashlib.sha256(json.dumps(sorted(rows), ensure_ascii=False).encode("utf-8")).hexdigest()


def logged_failed_files(log_text: str, pattern: str | None) -> set[str]:
    if not pattern:
        return set()
    return {m.group("path").replace("\\", "/") for m in re.finditer(pattern, log_text, re.M)}


def file_statuses(repo: Path, files: list[str], profile: dict, output_exists: bool, failed: set[str]) -> dict[str, dict]:
    statuses = {}
    for rel in files:
        cond = file_condition(repo / rel)
        if not output_exists:
            st = RUN_FAILED
        elif any(f == rel or f.endswith("/" + rel) for f in failed):
            st = LOGGED_FAILURE
        elif cond in profile.get("silently_skips", []):
            st = KNOWN_SKIP
        else:
            st = PROCESSED
        statuses[rel] = {"condition": cond, "status": st}
    return statuses


def _prefix(tool: str) -> str:
    return TOOL_FILES[tool].split("{repo}")[0]


def _resolve_exe(tool_dir: Path, kind: str, exe: str) -> str | None:
    """Executable for a pinned tool: its own virtualenv for Python tools, `node` on PATH for Node tools,
    the current interpreter for `{python}` (used by test stubs)."""
    if exe == "{python}":
        return sys.executable
    if kind == "node":
        from shutil import which
        return which(exe) or which(exe + ".cmd")
    for sub in ("Scripts", "bin"):
        for name in (exe + ".exe", exe):
            p = tool_dir / ".venv" / sub / name
            if p.exists():
                return str(p)
    return None


def build_command(tool: dict, tool_dir: Path, repo: Path, name: str, out: Path) -> tuple[list[str] | None, Path | None, str]:
    """Substitute placeholders in the manifest's `run` and `stdout` fields."""
    subst = {"repo": str(repo.resolve()), "name": name, "out": str(out.resolve()), "project": str(PROJECT),
             "tooldir": str(tool_dir.resolve()), "python": "{python}"}
    args = [a.format(**subst) for a in tool["run"]]
    exe = _resolve_exe(tool_dir, tool.get("kind", "python"), args[0])
    if exe is None:
        return None, None, f"executable '{args[0]}' not found in the tool's environment (not installed)"
    stdout = Path(tool["stdout"].format(**subst)) if tool.get("stdout") else None
    return [exe, *args[1:]], stdout, ""


def expected_output(tool_name: str, tool: dict, out: Path, name: str) -> Path:
    if tool.get("stdout"):
        return Path(tool["stdout"].format(out=str(out.resolve()), name=name))
    return out / TOOL_FILES[tool_name].format(repo=name)


def run_one(cmd: list[str], cwd: Path, stdout_path: Path | None, timeout: float) -> dict:
    t0 = time.monotonic()
    rec = {"started_utc": _now(), "timed_out": False, "exit_code": None, "stdout": "", "stderr": "", "error": ""}
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL)
        rec["exit_code"] = p.returncode
        out_text = p.stdout.decode("utf-8", errors="replace")
        if stdout_path is not None:
            stdout_path.write_bytes(p.stdout)        # the report itself, byte-exact
            rec["stdout"] = f"<{len(p.stdout)} bytes written to {stdout_path.name}>"
        else:
            rec["stdout"] = out_text
        rec["stderr"] = p.stderr.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired as e:
        rec["timed_out"] = True
        rec["stdout"] = (e.stdout or b"").decode("utf-8", errors="replace")
        rec["stderr"] = (e.stderr or b"").decode("utf-8", errors="replace")
        if stdout_path is not None and stdout_path.exists():
            stdout_path.unlink()                     # a partial report is not a report
    except OSError as e:
        rec["error"] = f"{type(e).__name__}: {e}"
    rec["ended_utc"] = _now()
    rec["elapsed_s"] = round(time.monotonic() - t0, 3)
    return rec


def write_log(path: Path, cmd: list[str] | None, rec: dict) -> None:
    lines = [f"# command: {' '.join(cmd) if cmd else '(not run)'}",
             f"# started: {rec.get('started_utc', '')}  ended: {rec.get('ended_utc', '')}",
             f"# exit_code: {rec.get('exit_code')}  timed_out: {rec.get('timed_out')}  elapsed_s: {rec.get('elapsed_s')}"]
    if rec.get("error"):
        lines.append(f"# error: {rec['error']}")
    lines += ["# --- stdout ---", rec.get("stdout", ""), "# --- stderr ---", rec.get("stderr", "")]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_external(tool_name: str, tool: dict, tool_dir: Path, repo: Path, name: str, out: Path,
                 timeout: float, allow_unpinned: bool = False) -> dict:
    prefix = _prefix(tool_name)
    log_path = out / f"{prefix}{name}.log"
    out_file = expected_output(tool_name, tool, out, name)
    for stale in (out_file, log_path):
        if stale.exists():
            stale.unlink()
    head = git_head(tool_dir)
    record = {"method": tool_name, "repo": name, "repo_commit": git_head(repo), "tool_commit_pinned": tool.get("commit"),
              "tool_commit_checked_out": head, "output_file": out_file.name, "log_file": log_path.name}
    cmd, stdout_path, why = None, None, ""
    if not tool_dir.exists():
        why = f"tool directory {tool_dir} does not exist (not installed)"
    elif tool.get("commit") and head != tool["commit"] and not allow_unpinned:
        why = f"tool checkout {head} is not the pinned commit {tool['commit']}"
    else:
        cmd, stdout_path, why = build_command(tool, tool_dir, repo, name, out)
    if cmd is None:
        rec = {"started_utc": _now(), "ended_utc": _now(), "elapsed_s": 0.0, "exit_code": None, "timed_out": False,
               "error": why, "stdout": "", "stderr": ""}
    else:
        rec = run_one(cmd, tool_dir, stdout_path, timeout)
    write_log(log_path, cmd, rec)
    exists = out_file.exists() and not rec["timed_out"]
    failed = logged_failed_files(log_path.read_text(encoding="utf-8"), (tool.get("file_failure_profile") or {}).get("error_log"))
    files = python_files(repo)
    statuses = file_statuses(repo, files, tool.get("file_failure_profile") or {}, exists, failed)
    record.update({k: rec[k] for k in ("started_utc", "ended_utc", "elapsed_s", "exit_code", "timed_out", "error")})
    record.update({"command": cmd, "run_status": "ok" if exists else "failed",
                   "output_sha256": _sha256(out_file) if exists else None,
                   "findings_sha256": findings_digest(tool_name, out_file, repo) if exists else None,
                   "log_sha256": _sha256(log_path),
                   "files_total": len(files), "file_status_counts": _counts(statuses), "files": statuses})
    (out / f"{prefix}{name}.run.json").write_text(json.dumps(record, indent=1, sort_keys=True), encoding="utf-8")
    return record


def run_pqscan(arm: str, repo: Path, name: str, out: Path, timeout: float, extra_args: list[str] | None = None) -> dict:
    out_file = out / PQSCAN_FILE.format(arm=arm, repo=name)
    log_path = out_file.with_suffix(".log")
    for stale in (out_file, log_path):
        if stale.exists():
            stale.unlink()
    cmd = [sys.executable, "-m", "pqscan.cli", "scan", str(repo.resolve()), "--format", "json", "--arm", arm,
           "-o", str(out_file.resolve()), *(extra_args or [])]
    rec = run_one(cmd, PROJECT, None, timeout)
    write_log(log_path, cmd, rec)
    exists = out_file.exists() and not rec["timed_out"] and rec["exit_code"] == 0
    failures: set[str] = set()
    if exists:
        try:
            data = json.loads(out_file.read_text(encoding="utf-8"))
            failures = {f.get("file", "") for f in data.get("execution_failures", [])}
        except (OSError, ValueError):
            exists = False
    files = python_files(repo)
    statuses = file_statuses(repo, files, {}, exists, failures)
    record = {"method": f"pqscan:{arm}", "repo": name, "repo_commit": git_head(repo), "command": cmd,
              "output_file": out_file.name, "log_file": log_path.name, "run_status": "ok" if exists else "failed",
              "output_sha256": _sha256(out_file) if exists else None,
              "findings_sha256": _sha256(out_file) if exists else None, "log_sha256": _sha256(log_path),
              "files_total": len(files), "file_status_counts": _counts(statuses), "files": statuses,
              **{k: rec[k] for k in ("started_utc", "ended_utc", "elapsed_s", "exit_code", "timed_out", "error")}}
    out_file.with_suffix(".run.json").write_text(json.dumps(record, indent=1, sort_keys=True), encoding="utf-8")
    return record


def _counts(statuses: dict[str, dict]) -> dict[str, int]:
    c: dict[str, int] = {}
    for v in statuses.values():
        c[v["status"]] = c.get(v["status"], 0) + 1
    return dict(sorted(c.items()))


def run_batch(tools_dir: Path, repos: dict[str, Path], out: Path, tools: list[str], arms: list[str],
              timeout: float, manifest_path: Path = DEFAULT_MANIFEST, allow_unpinned: bool = False) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    runs = []
    for name, repo in sorted(repos.items()):
        for t in tools:
            if t not in manifest["tools"]:
                raise SystemExit(f"unknown tool {t!r}; manifest has {sorted(manifest['tools'])}")
            runs.append(run_external(t, manifest["tools"][t], tools_dir / t, repo, name, out, timeout, allow_unpinned))
        for arm in arms:
            runs.append(run_pqscan(arm, repo, name, out, timeout))
    summary = {"created_utc": _now(), "python": sys.version.split()[0], "platform": platform.platform(),
               "manifest": str(manifest_path), "manifest_sha256": _sha256(manifest_path), "timeout_s": timeout,
               "not_run": manifest.get("not_runnable", {}),
               "runs": [{k: r[k] for k in ("method", "repo", "run_status", "exit_code", "timed_out", "elapsed_s",
                                           "error", "output_sha256", "findings_sha256", "file_status_counts")} for r in runs]}
    (out / "batch_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pqscan.bench.batch", description=__doc__.split("\n\n")[0])
    ap.add_argument("--tools-dir", type=Path, required=True, help="directory created by scripts/fetch_pinned.py baselines")
    ap.add_argument("--repos-dir", type=Path, required=True, help="one sub-directory per repository")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tools", default=",".join(TOOL_FILES))
    ap.add_argument("--pqscan-arms", default="full", help="comma-separated arms, or '' for none")
    ap.add_argument("--timeout", type=float, default=1800.0, help="per tool and repository, seconds")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--allow-unpinned", action="store_true", help="run tools not at their pinned commit (development only)")
    a = ap.parse_args(argv)
    repos = {d.name: d for d in sorted(a.repos_dir.iterdir()) if d.is_dir()}
    tools = [t for t in a.tools.split(",") if t]
    arms = [x for x in a.pqscan_arms.split(",") if x]
    s = run_batch(a.tools_dir, repos, a.out, tools, arms, a.timeout, a.manifest, a.allow_unpinned)
    for r in s["runs"]:
        print(f"{r['method']:<22} {r['repo']:<28} {r['run_status']:<7} exit={r['exit_code']} {r['elapsed_s']:>8.1f}s {r['file_status_counts']}")
    for k, v in s["not_run"].items():
        print(f"not run: {k}: {v}")
    return 0 if all(r["run_status"] == "ok" for r in s["runs"]) else 1


if __name__ == "__main__":
    sys.exit(main())
