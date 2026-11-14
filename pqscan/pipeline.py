"""End-to-end scan: safe file walk -> Module B evidence -> Module C roles -> Module D policy, with
Module A (Semgrep) run alongside and joined by location. Never imports or executes scanned code.
"""
from __future__ import annotations
import importlib, logging, multiprocessing as mp, os, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from . import __version__
from .detect import run_semgrep_report, SemgrepError
from .policy import load_policy, Policy, Recommendation
from .roles import classify, RoleDecision
from .semantic.evidence import analyze_source, SiteEvidence

log = logging.getLogger("pqscan")
SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules", "__pycache__", ".tox", ".nox", "build", "dist", "site-packages", ".eggs"}
TEST_PARTS = {"tests", "test", "testing"}
# libraries with public-key cryptography that pqscan does not analyse (api_coverage.md Sec. 3)
UNSUPPORTED_LIBS = {"rsa": "python-rsa", "ecdsa": "python-ecdsa", "OpenSSL": "pyOpenSSL", "M2Crypto": "M2Crypto",
                    "nacl": "PyNaCl", "jwcrypto": "jwcrypto", "oqs": "liboqs-python", "pqcrypto": "pqcrypto",
                    "Crypto.PublicKey.ElGamal": "PyCryptodome ElGamal", "ssl": "ssl (protocol configuration)",
                    "paramiko": "paramiko (as a library)", "asyncssh": "asyncssh (as a library)"}


@dataclass
class Finding:
    evidence: SiteEvidence
    decision: RoleDecision
    recommendation: Recommendation
    scope: str                                  # app | test | vendored | example
    semgrep_rules: list[str] = field(default_factory=list)


@dataclass
class ScanResult:
    root: str
    tool_version: str
    policy_version: str
    tier_threshold: str
    arm: str
    findings: list[Finding] = field(default_factory=list)
    excluded: list[dict[str, Any]] = field(default_factory=list)     # sites Module C excluded (reason kept)
    errors: list[dict[str, str]] = field(default_factory=list)       # per-file EXECUTION_FAILURE records
    files_scanned: int = 0
    files_skipped: list[dict[str, str]] = field(default_factory=list)
    semgrep_status: str = "not-run"
    semgrep_errors: list[dict[str, str]] = field(default_factory=list)
    semgrep_only: list[dict[str, Any]] = field(default_factory=list)  # Semgrep candidates with no semantic site
    unsupported: list[dict[str, Any]] = field(default_factory=list)   # imports of out-of-scope crypto libraries


def scope_of(rel: str) -> str:
    parts = rel.split("/")
    name = parts[-1]
    if any(p in ("vendor", "_vendor", "third_party", "vendored") for p in parts[:-1]):
        return "vendored"
    if any(p in TEST_PARTS for p in parts[:-1]) or name.startswith("test_") or name.endswith("_test.py") or name == "conftest.py":
        return "test"
    if any(p in ("examples", "example", "demo", "demos", "docs") for p in parts[:-1]):
        return "example"
    return "app"


def iter_python_files(root: Path, max_bytes: int, include_tests: bool, skipped: list[dict[str, str]]):
    """Walk `root` without following symlinks; never leave the root."""
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        kept = []
        for d in sorted(dirnames):
            full = os.path.join(dirpath, d)
            rel_d = Path(full).relative_to(root).as_posix()
            if os.path.islink(full) or os.path.isjunction(full):
                skipped.append({"file": rel_d + "/", "reason": "symlink/junction directory not followed"})
            elif d in SKIP_DIRS or d.startswith("."):
                skipped.append({"file": rel_d + "/", "reason": "excluded directory (build/VCS/virtualenv/hidden)"})
            else:
                kept.append(d)
        dirnames[:] = kept
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            p = Path(dirpath) / fn
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                skipped.append({"file": rel, "reason": "symlink not followed"}); continue
            try:
                resolved = p.resolve()
                resolved.relative_to(root)
            except (ValueError, OSError):
                skipped.append({"file": rel, "reason": "resolves outside the scan root"}); continue
            if not include_tests and scope_of(rel) == "test":
                continue
            try:
                size = p.stat().st_size
            except OSError as e:
                skipped.append({"file": rel, "reason": f"stat failed: {e.__class__.__name__}"}); continue
            if size > max_bytes:
                skipped.append({"file": rel, "reason": f"larger than {max_bytes} bytes"}); continue
            yield p, rel


def unsupported_imports(rel: str, source: str) -> list[dict[str, Any]]:
    """Imports of public-key crypto libraries outside the supported scope, reported explicitly."""
    import ast
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return []
    out = []
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names = [node.module]
        for n in names:
            for prefix, lib in UNSUPPORTED_LIBS.items():
                if n == prefix or n.startswith(prefix + "."):
                    out.append({"file": rel, "line": node.lineno, "module": n, "library": lib,
                                "status": "unsupported: not analysed, no role or recommendation"})
    return out


def _analyze_file(path: str, rel: str) -> tuple[list[SiteEvidence], list[dict[str, Any]]]:
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8", errors="replace")
    return analyze_source(rel, text), unsupported_imports(rel, text)


def _worker_main(conn, analyzer: str) -> None:
    """Child process: analyse files sent over `conn` one at a time. Runs only the analyser (parsing);
    scanned code is never imported or executed here either."""
    mod, name = analyzer.split(":")
    fn = getattr(importlib.import_module(mod), name)
    while True:
        try:
            msg = conn.recv()
        except EOFError:
            return
        if msg is None:
            return
        path, rel = msg
        try:
            conn.send(("ok", fn(path, rel)))
        except RecursionError:
            conn.send(("err", "recursion limit (deeply nested code)"))
        except Exception as e:  # noqa: BLE001 - reported to the parent as an execution failure
            conn.send(("err", f"{e.__class__.__name__}: {str(e)[:200]}"))


class IsolatedAnalyzer:
    """One long-lived worker process. A file that exceeds its time limit gets its worker killed and
    replaced, so a pathological file cannot hang the scan or be blamed on the files after it."""

    def __init__(self, analyzer: str = "pqscan.pipeline:_analyze_file", timeout_s: float = 30.0):
        self.analyzer, self.timeout_s = analyzer, timeout_s
        self.ctx = mp.get_context("spawn")
        self.proc = None
        self.conn = None

    def _start(self) -> None:
        parent, child = self.ctx.Pipe()
        self.proc = self.ctx.Process(target=_worker_main, args=(child, self.analyzer), daemon=True)
        self.proc.start()
        child.close()
        self.conn = parent

    def _kill(self) -> None:
        if self.proc is not None and self.proc.is_alive():
            self.proc.kill()
        if self.proc is not None:
            self.proc.join(5)
        if self.conn is not None:
            self.conn.close()
        self.proc = self.conn = None

    def analyze(self, path: str, rel: str):
        """Return ("ok", result) or ("err", message). The time limit counts from this file's start."""
        if self.proc is None or not self.proc.is_alive():
            self._start()
        self.conn.send((path, rel))
        started = time.monotonic()
        if self.conn.poll(self.timeout_s):
            try:
                return self.conn.recv()
            except (EOFError, OSError):
                self._kill()
                return ("err", "analysis worker terminated unexpectedly")
        self._kill()
        return ("err", f"analysis exceeded {self.timeout_s}s (stopped after {time.monotonic() - started:.1f}s)")

    def close(self) -> None:
        if self.conn is not None:
            try:
                self.conn.send(None)
            except (OSError, BrokenPipeError):
                pass
        if self.proc is not None:
            self.proc.join(5)
        self._kill()


def scan(root: Path, policy: Policy | None = None, arm: str = "full", include_tests: bool = True,
         max_bytes: int = 2_000_000, file_timeout_s: float = 30.0, run_semgrep_rules: bool = True,
         analyzer: str = "pqscan.pipeline:_analyze_file") -> ScanResult:
    root = Path(root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    policy = policy or load_policy()
    res = ScanResult(root=str(root), tool_version=__version__, policy_version=policy.version,
                     tier_threshold=policy.threshold.value, arm=arm)
    files = list(iter_python_files(root, max_bytes, include_tests, res.files_skipped))
    res.files_scanned = len(files)
    evidences: list[SiteEvidence] = []
    # every file is analysed in a worker process with its own time limit; failures are recorded as
    # EXECUTION_FAILURE records, never as abstentions, and never block the remaining files
    worker = IsolatedAnalyzer(analyzer, file_timeout_s)
    try:
        for p, rel in files:
            status, payload = worker.analyze(str(p), rel)
            if status != "ok":
                res.errors.append({"file": rel, "error": payload}); continue
            evs, unsup = payload
            res.unsupported.extend(unsup)
            for ev in evs:
                if ev.site_kind == "parse-error":
                    res.errors.append({"file": rel, "error": "; ".join(ev.notes)})
                else:
                    evidences.append(ev)
    finally:
        worker.close()
    # Module A alongside: join Semgrep candidates by (file, line)
    sem_index: dict[tuple[str, int], list[str]] = {}
    if run_semgrep_rules:
        try:
            cands, sem_errors = run_semgrep_report(root, targets=[p for p, _ in files], max_target_bytes=max_bytes)
            for c in cands:
                sem_index.setdefault((c.location.file, c.location.line), []).append(c.rule_id)
            res.semgrep_status = "ok" if not sem_errors else f"ok with {len(sem_errors)} file error(s)"
            res.semgrep_errors = sem_errors
        except SemgrepError as e:
            res.semgrep_status = f"failed: {str(e)[:200]}"
            log.warning("semgrep failed: %s", e)
    matched_keys: set[tuple[str, int]] = set()
    for ev in evidences:
        d = classify(ev, arm)
        key = (ev.candidate.location.file, ev.candidate.location.line)
        rules = sorted(set(sem_index.get(key, [])))
        if rules:
            matched_keys.add(key)
        if d.role is None:
            res.excluded.append({"file": key[0], "line": key[1], "kind": ev.site_kind, "reason": d.reason})
            continue
        rec = policy.apply(d, ev.hybrid_apis, ev.hybrid_combined)
        res.findings.append(Finding(ev, d, rec, scope_of(key[0]), rules))
    for (f, line), rules in sorted(sem_index.items()):
        if (f, line) not in matched_keys and not any(e["file"] == f and e["line"] == line for e in res.excluded):
            res.semgrep_only.append({"file": f, "line": line, "rules": sorted(set(rules))})
    res.findings.sort(key=lambda x: (x.evidence.candidate.location.file, x.evidence.candidate.location.line, x.evidence.candidate.location.col))
    return res
