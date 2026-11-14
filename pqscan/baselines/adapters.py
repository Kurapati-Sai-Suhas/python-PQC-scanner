"""Adapters: each external tool's native output -> list of ToolFinding(file, line, text, rule).

The adapters only read the tools' own report files; they never re-interpret findings. Matching to
sites uses path-suffix comparison, so absolute, clone-prefixed and relative paths all work.
Tool versions and invocations are pinned in `baselines_manifest.json`.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class ToolFinding:
    file: str      # as emitted by the tool, normalised to forward slashes
    line: int
    text: str      # the tool's migration / recommendation text (or a description when it has none)
    rule: str


def _n(p: str) -> str:
    return p.replace("\\", "/")


def load_pqcheck_sarif(path: Path) -> list[ToolFinding]:
    s = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for x in s["runs"][0]["results"]:
        loc = x["locations"][0]["physicalLocation"]
        out.append(ToolFinding(_n(loc["artifactLocation"]["uri"]), int(loc["region"]["startLine"]), x["message"]["text"], x["ruleId"]))
    return out


def load_pqcaudit_cbom(path: Path) -> list[ToolFinding]:
    cb = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for c in cb.get("components", []):
        props = {p["name"].split(":")[-1]: p["value"] for p in c.get("properties", [])}
        for o in c.get("evidence", {}).get("occurrences", []):
            out.append(ToolFinding(_n(o["location"]), int(o["line"]),
                                   f"{c['name']} usage={c['bom-ref'].split(':')[-1]} target={props.get('migrationTarget')}", c["bom-ref"]))
    return out


def load_postquant_json(path: Path) -> list[ToolFinding]:
    p = json.loads(Path(path).read_text(encoding="utf-8"))
    return [ToolFinding(_n(x["file"]), int(x["line"]), x.get("migration", ""), x["patternId"]) for x in p["findings"]]


def load_qsafe_json(path: Path) -> list[ToolFinding]:
    q = json.loads(Path(path).read_text(encoding="utf-8"))
    return [ToolFinding(_n(x["file"]), int(x["line"]), x.get("migration", ""), f"{x['algorithm']}/{x['context']}") for x in q["findings"]]


def load_qsa_regex_json(path: Path) -> list[ToolFinding]:
    q = json.loads(Path(path).read_text(encoding="utf-8"))
    return [ToolFinding(_n(x["file"]), int(x["line_number"]), x.get("pqc_replacement", ""), x["algorithm"]) for x in q["findings"]]


def load_sarif_generic(path: Path) -> list[ToolFinding]:
    """Any SARIF 2.1.0 report whose result messages carry the migration advice (pqblocks-scan 0.1.0)."""
    s = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for run in s.get("runs", []):
        for x in run.get("results", []):
            loc = x["locations"][0]["physicalLocation"]
            out.append(ToolFinding(_n(loc["artifactLocation"]["uri"]), int(loc["region"]["startLine"]), x["message"]["text"], x.get("ruleId", "")))
    return out


ADAPTERS: dict[str, Callable[[Path], list[ToolFinding]]] = {
    "pqcheck": load_pqcheck_sarif, "pqc-audit": load_pqcaudit_cbom, "PostQuant": load_postquant_json,
    "qsafe": load_qsafe_json, "QSA-regex": load_qsa_regex_json, "pqblocks-scan": load_sarif_generic,
}


def findings_in_window(findings: list[ToolFinding], site_file: str, lo: int, hi: int) -> list[ToolFinding]:
    sf = _n(site_file)
    return [f for f in findings if (f.file == sf or f.file.endswith("/" + sf)) and lo <= f.line <= hi]
