"""Annotation packets for the blind AI-assisted review (protocol v1.0.4 Sec. 3; guide v1.1 Sec. 5-6; V8, V16;
R4-19 item 5).

Packet rule `packet-v1` (fixed; its hash is recorded at F1). For candidate (file, line) of a repository checkout at
its pinned commit, the packet contains, from that one file only:
  1. a header: candidate ID, file path (relative), line;
  2. every top-level import statement of the file;
  3. the context: the smallest enclosing class if it has at most CLASS_MAX_LINES lines, otherwise the smallest
     enclosing function; at module level, WINDOW lines either side of the candidate;
  4. up to MAX_CALLERS other functions in the same file that call the enclosing function by name (Step D: the direct
     caller, one level).
Every source line is prefixed with its line number; the candidate line is marked ">>". The source code is never
executed or imported; it is read as text and parsed with `ast`. Nothing outside the file is included, so labels that
need more context are recorded by the owner as `context_used = extended`.

Forbidden content: the packet template itself never contains tool names, the project's name, hypotheses or results
(FORBIDDEN). Source code is copied verbatim; if the scanned code itself contains a forbidden token, the packet is
still built and the token is reported in `warnings` for the owner to review, never silently edited.

Packet-first subset: a candidate is labelled packet-first iff u < rate(phase), where u is a uniform value from
SHA-256("20261113:packet:<phase>|<candidate_id>") and rate(phase) = max(0.10, 60 / planned issued candidates of the
phase). The planned counts are the workload estimates of R3-03 (DV about 468, T about 630), so the expected subset
is at least 60 (target >= 50; the realised count is reported, and a shortfall cannot be topped up later because
packet-first labels must precede the primary label).
"""
from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

RULE = "packet-v1"
CLASS_MAX_LINES, WINDOW, MAX_CALLERS = 400, 40, 3
# tool names, the project's name and the study's hypotheses/arms; matched case-insensitively on word boundaries
FORBIDDEN = ("pqscan", "pqcheck", "pqc-audit", "pqc_audit", "postquant", "qsafe", "pqblocks", "cbomkit",
             "quantum-safe auditor", "semgrep", "pypqc", "rolebench", "post-quantum crypto scanner", "provenance-aware",
             "method+args", "h2a", "h2b")
_FORBIDDEN_RE = re.compile(r"(?<![a-z0-9_])(" + "|".join(re.escape(t) for t in FORBIDDEN) + r")(?![a-z0-9_])")
PACKET_SEED = 20261113
PLANNED_CANDIDATES = {"DV": 468, "T": 630}


def _forbidden_in(text: str) -> list[str]:
    return sorted({m.group(1) for m in _FORBIDDEN_RE.finditer(text.lower())})


def _span(node: ast.AST) -> tuple[int, int]:
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    return start, node.end_lineno


def _enclosing(tree: ast.AST, line: int):
    cls = fn = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            a, b = _span(node)
            if a <= line <= b:
                if isinstance(node, ast.ClassDef):
                    if cls is None or _span(node)[0] >= _span(cls)[0]:
                        cls = node
                elif fn is None or _span(node)[0] >= _span(fn)[0]:
                    fn = node
    return cls, fn


def _callers(tree: ast.AST, name: str, exclude: tuple[int, int]) -> list[tuple[int, int]]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _span(node) != exclude:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    f = sub.func
                    callee = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
                    if callee == name:
                        out.append(_span(node))
                        break
    return sorted(set(out))[:MAX_CALLERS]


def build_packet(repo_root: Path, file: str, line: int, candidate_id: str) -> dict:
    text = (Path(repo_root) / file).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not 1 <= line <= len(lines):
        raise ValueError(f"{file}:{line} is outside the file ({len(lines)} lines)")
    header = f"Candidate: {candidate_id}\nFile: {file}\nLine: {line}\n"
    bad = _forbidden_in(header)
    if bad:
        raise ValueError(f"packet header would contain forbidden content: {bad}")
    sections: list[tuple[str, list[tuple[int, int]]]] = []
    notes = []
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        tree = None
        notes.append("the file does not parse; a line window is shown")
    if tree is not None:
        imports = [_span(n) for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        if imports:
            sections.append(("Imports", imports))
        cls, fn = _enclosing(tree, line)
        if cls is not None and _span(cls)[1] - _span(cls)[0] + 1 <= CLASS_MAX_LINES:
            ctx = _span(cls)
            sections.append(("Enclosing class", [ctx]))
        elif fn is not None:
            ctx = _span(fn)
            sections.append(("Enclosing function", [ctx]))
        else:
            ctx = (max(1, line - WINDOW), min(len(lines), line + WINDOW))
            sections.append(("Module context", [ctx]))
        if fn is not None:
            calls = [s for s in _callers(tree, fn.name, _span(fn)) if not (ctx[0] <= s[0] and s[1] <= ctx[1])]
            if calls:
                sections.append((f"Callers of {fn.name} in this file", calls))
    else:
        sections.append(("Line window", [(max(1, line - WINDOW), min(len(lines), line + WINDOW))]))
    width = len(str(len(lines)))
    body = [header]
    for title, spans in sections:
        body.append(f"--- {title} ---")
        for a, b in spans:
            for i in range(a, b + 1):
                mark = ">>" if i == line else "  "
                body.append(f"{mark} {i:>{width}} | {lines[i - 1]}")
            body.append("")
    if notes:
        body.append("Note: " + "; ".join(notes))
    packet_text = "\n".join(body).rstrip() + "\n"
    return {"rule": RULE, "candidate_id": candidate_id, "file": file, "line": line, "text": packet_text,
            "sha256": hashlib.sha256(packet_text.encode("utf-8")).hexdigest(),
            "warnings": [f"source contains forbidden token(s) {w}" for w in [_forbidden_in(text)] if w]}


def packet_first_rate(phase: str) -> float:
    if phase not in PLANNED_CANDIDATES:
        raise ValueError(f"packet-first applies to phases {sorted(PLANNED_CANDIDATES)}, not {phase!r}")
    return max(0.10, 60 / PLANNED_CANDIDATES[phase])


def packet_first(candidate_id: str, phase: str) -> bool:
    h = hashlib.sha256(f"{PACKET_SEED}:packet:{phase}|{candidate_id}".encode("utf-8")).hexdigest()
    return int(h[:16], 16) / 2**64 < packet_first_rate(phase)


def is_candidate_id(s: str) -> bool:
    return bool(re.fullmatch(r"[CA]-[0-9a-f]{12}", s))
