"""Classify the condition of a source file, independently of any tool, so that a tool's silence on
a file it is known to fail on is recorded as EXECUTION_FAILURE rather than MISSED."""
from __future__ import annotations
import ast
from pathlib import Path

CONDITIONS = ("ok", "syntax-error", "null-byte", "non-utf8", "unreadable", "missing")


def file_condition(path: Path) -> str:
    p = Path(path)
    if not p.exists():
        return "missing"
    try:
        raw = p.read_bytes()
    except OSError:
        return "unreadable"
    if b"\x00" in raw:
        return "null-byte"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return "non-utf8"
    try:
        ast.parse(text)
    except (SyntaxError, ValueError):
        return "syntax-error"
    return "ok"
