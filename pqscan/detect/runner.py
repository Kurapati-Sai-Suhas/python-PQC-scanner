"""Run the bundled Semgrep rules on a directory and return Candidate records.

Security: Semgrep parses files; it never executes them. We pass --metrics=off and never
send file contents anywhere. Snippets are truncated to 200 characters and taken from the
source line only (never from multi-line string/key literals: lines that look like PEM
armour are redacted).
"""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys
from pathlib import Path
from typing import Iterable
import yaml
from ..models import Candidate, CandidateKind, Library, Location

RULES_DIR = Path(__file__).parent / "rules"
PEM_RE = re.compile(r"-----BEGIN|-----END|^[A-Za-z0-9+/=]{60,}$")


class SemgrepError(RuntimeError):
    pass


def semgrep_executable() -> str:
    """Prefer the semgrep next to the running interpreter (venv), then PATH."""
    exe = Path(sys.executable).parent / ("semgrep.exe" if os.name == "nt" else "semgrep")
    if exe.exists():
        return str(exe)
    found = shutil.which("semgrep")
    if not found:
        raise SemgrepError("semgrep executable not found; install semgrep==1.185.0 in the environment")
    return found


def load_rule_metadata(rules_dir: Path = RULES_DIR) -> dict[str, dict]:
    meta: dict[str, dict] = {}
    for f in sorted(rules_dir.glob("*.yaml")):
        doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        for r in doc.get("rules", []):
            meta[r["id"]] = r.get("metadata", {})
    return meta


def _snippet(root: Path, rel: str, line: int) -> str:
    try:
        with open(root / rel, encoding="utf-8", errors="replace") as fh:
            for i, text in enumerate(fh, 1):
                if i == line:
                    s = text.rstrip("\n")
                    return "<redacted key material>" if PEM_RE.search(s) else s.strip()[:200]
    except OSError:
        pass
    return ""


def run_semgrep(root: Path, rules_dir: Path = RULES_DIR, timeout_s: int = 600, max_target_bytes: int = 2_000_000,
                include_tests: bool = True, targets: list[Path] | None = None) -> list[Candidate]:
    """Run all bundled rules on `root` and return candidates sorted by (file, line, col, rule)."""
    return run_semgrep_report(root, rules_dir, timeout_s, max_target_bytes, include_tests, targets)[0]


def _confined_python_files(root: Path, include_tests: bool) -> list[Path]:
    """Default target list: the pipeline's own confined walk (no symlinks/junctions out of the root)."""
    from ..pipeline import iter_python_files
    return [p for p, _ in iter_python_files(root, 10**12, include_tests, [])]


def run_semgrep_report(root: Path, rules_dir: Path = RULES_DIR, timeout_s: int = 600, max_target_bytes: int = 2_000_000,
                       include_tests: bool = True, targets: list[Path] | None = None,
                       batch_size: int = 150) -> tuple[list[Candidate], list[dict[str, str]]]:
    """As run_semgrep, plus the per-file errors Semgrep reported (parse failures etc.), which are
    recorded rather than fatal.

    Semgrep is given explicit file targets, never the directory: given a directory it follows Windows
    junctions out of the root and applies its default ignore list (e.g. `tests/`). Results whose
    resolved path is outside the root are dropped before any file is opened."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise SemgrepError(f"scan root is not a directory: {root}")
    files = [Path(t).resolve() for t in (targets if targets is not None else _confined_python_files(root, include_tests))]
    files = [f for f in files if f.is_file() and _inside(f, root)]
    meta = load_rule_metadata(rules_dir)
    out: list[Candidate] = []
    errors: list[dict[str, str]] = []
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        cmd = [semgrep_executable(), "--config", str(rules_dir), "--json", "--quiet", "--metrics=off",
               "--no-git-ignore", "--max-target-bytes", str(max_target_bytes), "--timeout", "30",
               "--disable-version-check", *map(str, batch)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, encoding="utf-8", errors="replace", cwd=root)
        except subprocess.TimeoutExpired as e:
            raise SemgrepError(f"semgrep timed out after {timeout_s}s") from e
        if proc.returncode not in (0, 1) or not proc.stdout.strip():
            raise SemgrepError(f"semgrep failed (exit {proc.returncode}): {proc.stderr[-2000:]}")
        data = json.loads(proc.stdout)
        for r in data.get("results", []):
            path = Path(r["path"])
            path = (path if path.is_absolute() else root / path).resolve()
            if not _inside(path, root):
                continue                      # never report or open anything outside the scan root
            rel = path.relative_to(root).as_posix()
            rule_id = r["check_id"]
            for known in meta:
                if r["check_id"] == known or r["check_id"].endswith("." + known):
                    rule_id = known
                    break
            m = meta.get(rule_id, {})
            loc = Location(rel, r["start"]["line"], r["start"]["col"], r["end"]["line"], r["end"]["col"])
            out.append(Candidate(location=loc, rule_id=rule_id, library=Library(m.get("library", "unknown")),
                                 kind=CandidateKind(m.get("kind", "method-candidate")), algorithm=m.get("algorithm", "ANY"),
                                 api=m.get("api", ""), coverage_row=m.get("coverage_row", "-"),
                                 snippet=_snippet(root, rel, loc.line)))
        for e in data.get("errors", []):
            if e.get("level") == "error":
                errors.append({"path": _rel_or_redacted(str(e.get("path", "")), root), "message": str(e.get("type", "error"))[:80]})
    out.sort(key=lambda c: (c.location.file, c.location.line, c.location.col, c.rule_id))
    return out, errors


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _rel_or_redacted(p: str, root: Path) -> str:
    if not p:
        return ""
    path = Path(p)
    path = (path if path.is_absolute() else root / path).resolve()
    return path.relative_to(root).as_posix() if _inside(path, root) else "<outside scan root>"


def candidates_to_json(cands: Iterable[Candidate]) -> str:
    return json.dumps([c.to_dict() for c in cands], indent=1, sort_keys=True)
