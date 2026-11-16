"""Strict label validation (protocol v1.0.4 Sec. 3; annotation guide v1.1 Sec. 5; decisions V6, V16; R4-19 item 4).

A label file has one envelope per line: {"site": <docs/benchmark/benchmark_schema.json record>, "meta": <
docs/benchmark/meta_schema.json record>}. Validation never coerces: the string "false" for a boolean, an unknown or
duplicate candidate ID, a missing issued candidate, or a missing evidence line is an error, and the whole file is
rejected with every problem listed.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SITE_SCHEMA = ROOT / "docs" / "benchmark" / "benchmark_schema.json"
META_SCHEMA = ROOT / "docs" / "benchmark" / "meta_schema.json"
COMPARED_FIELDS = ("eligible", "gt_role", "assessability", "possible_roles", "hybrid_component", "obvious_from_name",
                   "evidence_needed", "key_provenance")
KIND_ANNOTATOR = {"primary": "owner", "packet_first": "owner", "relabel": "owner", "final": "owner",
                  "ai_review": "ai_review"}


class LabelError(ValueError):
    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__(f"{len(problems)} problem(s): " + "; ".join(problems[:5]) + (" ..." if len(problems) > 5 else ""))


@lru_cache(maxsize=None)
def _validators():
    full = json.loads(SITE_SCHEMA.read_text(encoding="utf-8"))
    site = Draft202012Validator(full)
    # AI-review records carry only site_id and the compared fields the AI actually gave (never filled in)
    partial = {"$schema": full["$schema"], "type": "object", "additionalProperties": False, "required": ["site_id"],
               "properties": {k: full["properties"][k] for k in ("site_id",) + COMPARED_FIELDS}}
    meta = Draft202012Validator(json.loads(META_SCHEMA.read_text(encoding="utf-8")))
    return site, meta, Draft202012Validator(partial)


def annotator_added_id(repo: str, file: str, line: int) -> str:
    return "A-" + hashlib.sha256(f"annotator_added|{repo}|{file}|{line}".encode("utf-8")).hexdigest()[:12]


def validate_record(rec: object, kind: str) -> list[str]:
    """Problems with one envelope (empty list = valid)."""
    if kind not in KIND_ANNOTATOR:
        raise ValueError(f"unknown label kind {kind!r}")
    if not isinstance(rec, dict) or set(rec) != {"site", "meta"}:
        return ["record must be an object with exactly the keys 'site' and 'meta'"]
    site_full, meta_v, site_partial = _validators()
    site_v = site_partial if kind == "ai_review" else site_full
    out = [f"site.{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in site_v.iter_errors(rec["site"])]
    out += [f"meta.{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in meta_v.iter_errors(rec["meta"])]
    if out:
        return out
    s, m = rec["site"], rec["meta"]
    if s["site_id"] != m["candidate_id"]:
        out.append("site.site_id must equal meta.candidate_id")
    if m["label_kind"] != kind:
        out.append(f"meta.label_kind is {m['label_kind']!r}, expected {kind!r}")
    if m["annotator"] != KIND_ANNOTATOR[kind]:
        out.append(f"meta.annotator must be {KIND_ANNOTATOR[kind]!r} for {kind} labels")
    if s.get("eligible") is True and not m["evidence_lines"] and kind != "ai_review":
        out.append("an eligible label needs at least one evidence line (guide v1.1 Sec. 4)")
    if m.get("unresolved") and kind not in ("final", "primary", "relabel"):
        out.append("unresolved fields are recorded by the owner")
    if kind == "ai_review" and m.get("annotator_added"):
        out.append("the AI review cannot add sites")
    return out


def validate_file(path: Path, kind: str, issued: list[str] | None = None) -> list[dict]:
    """Validate a whole label file. With `issued`, every issued candidate must be labelled exactly once and nothing
    else may appear, except owner-added sites (meta.annotator_added with an A- ID). Raises LabelError."""
    problems: list[str] = []
    records: list[dict] = []
    seen: set[str] = set()
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            problems.append(f"line {n}: not JSON ({e.msg})")
            continue
        errs = validate_record(rec, kind)
        problems += [f"line {n}: {e}" for e in errs]
        if errs:
            continue
        cid = rec["meta"]["candidate_id"]
        if cid in seen:
            problems.append(f"line {n}: duplicate candidate {cid}")
        seen.add(cid)
        records.append(rec)
    if issued is not None:
        listed = {r["meta"]["candidate_id"] for r in records if not r["meta"].get("annotator_added")}
        missing = [c for c in issued if c not in listed]
        unknown = sorted(listed - set(issued))
        if missing:
            problems.append(f"{len(missing)} issued candidate(s) not labelled: {missing[:5]}")
        if unknown:
            problems.append(f"unknown candidate ID(s) (not issued in this batch): {unknown[:5]}")
    if problems:
        raise LabelError(problems)
    return records


def eligibility_of(rec: dict) -> object:
    """Final eligibility for the sampler: True/False, or "unresolved" when the owner left it unresolved."""
    return "unresolved" if "eligible" in (rec["meta"].get("unresolved") or []) else rec["site"]["eligible"]
