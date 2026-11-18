"""AI-review records, owner-AI comparison and owner adjudication (protocol v1.0.4 Sec. 3; guide v1.1 Sec. 1, 6;
decisions V1, V8, V9; R4-19 items 6-7).

* The AI-review interface and model identity must be recorded by the owner before any review
  (`docs/benchmark/ai_review_identity.json`, V8). Without it, prompts are refused.
* The prompt = the fixed template `docs/benchmark/ai_review_prompt_v1.md` + guide v1.1 Sec. 3-4 (decision procedure
  and evidence rules), followed by the packets. Its SHA-256 (template part, without packets) is recorded per record.
* The owner pastes the prompt into a fresh isolated session (or the API with a pinned model; Claude never handles the
  owner's key), saves the verbatim response, and the parser turns it into AI-review records. The parser never fills a
  field the response did not give; absent fields are listed in `missing_fields` and produce no disagreement.
* AI-review records are envelopes with a partial site part (site_id + the 8 compared fields) and a meta part with
  meta.ai (labels.validate_record kind "ai_review").
* Comparison covers the 8 fields; possible_roles is compared as a set. AI "insufficient_context" records are not
  disagreements; they are counted.
* Adjudication: one row per disagreement with final value, reason, category (kept, adopted_ai, third_value,
  unresolved) and the context_difference tag. Final labels = owner primary, except adjudicated fields; unresolved
  fields keep the owner's value and are listed in meta.unresolved. Every rule violation raises ReviewError.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from .labels import COMPARED_FIELDS, LabelError, validate_record

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "docs" / "benchmark" / "ai_review_prompt_v1.md"
GUIDE = ROOT / "docs" / "benchmark" / "annotation_guide.md"
IDENTITY = ROOT / "docs" / "benchmark" / "ai_review_identity.json"
CATEGORIES = ("kept", "adopted_ai", "third_value", "unresolved")
AI_EXTRA = ("ambiguity", "evidence_lines", "rationale")


class ReviewError(ValueError):
    pass


IDENTITY_REQUIRED = ("interface_or_api", "model", "recorded_utc", "isolation")
IDENTITY_OPTIONAL = ("app_version", "notes")
# guide v1.1 Sec. 6: one fresh ChatGPT Temporary Chat per batch, with these all off
ISOLATION_YES = ("fresh_temporary_chat_per_batch",)
ISOLATION_OFF = ("custom_instructions", "memory_and_chat_history_reference", "projects", "connectors", "file_library",
                 "browsing_search")
_PLACEHOLDER = re.compile(r"FILL|TODO|[<>]")
_UTC = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z$")   # as meta_schema ai.datetime_utc


def identity_problems(ident) -> list[str]:
    """Every reason the identity record is not acceptable (empty list = acceptable). Never fills anything in."""
    import datetime as _dt
    if not isinstance(ident, dict):
        return ["the identity record must be a JSON object"]
    probs = []
    for k in IDENTITY_REQUIRED:
        if k not in ident or (isinstance(ident[k], str) and not ident[k].strip()):
            probs.append(f"{k} is missing or empty")
    unknown = sorted(set(ident) - set(IDENTITY_REQUIRED) - set(IDENTITY_OPTIONAL))
    if unknown:
        probs.append(f"unknown keys {unknown} (allowed: {list(IDENTITY_REQUIRED + IDENTITY_OPTIONAL)})")
    for k in ("interface_or_api", "model", "recorded_utc") + IDENTITY_OPTIONAL:
        if k in ident and not isinstance(ident[k], str):
            probs.append(f"{k} must be a string")
    for k, v in ident.items():
        for s in ([v] if isinstance(v, str) else list(v.values()) if isinstance(v, dict) else []):
            if isinstance(s, str) and _PLACEHOLDER.search(s):
                probs.append(f"{k} still contains a placeholder (FILL, TODO, < or >)")
                break
    utc = ident.get("recorded_utc")
    if isinstance(utc, str) and utc.strip() and not _PLACEHOLDER.search(utc):
        if not _UTC.match(utc):
            probs.append("recorded_utc must look like YYYY-MM-DDTHH:MM:SSZ (UTC)")
        else:
            t = _dt.datetime.fromisoformat(utc.replace("Z", "+00:00"))
            if t > _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(minutes=5):
                probs.append("recorded_utc is in the future")
    iso = ident.get("isolation")
    if "isolation" in ident:
        if not isinstance(iso, dict):
            probs.append("isolation must be an object with the guide v1.1 Sec. 6 settings")
        else:
            expected = ISOLATION_YES + ISOLATION_OFF
            for k in expected:
                if k not in iso:
                    probs.append(f"isolation.{k} is not recorded")
            extra = sorted(set(iso) - set(expected))
            if extra:
                probs.append(f"isolation has unknown keys {extra}")
            for k in ISOLATION_YES:
                if k in iso and str(iso[k]).strip().lower() != "yes":
                    probs.append(f"isolation.{k} must be 'yes' (guide v1.1 Sec. 6)")
            for k in ISOLATION_OFF:
                if k in iso and str(iso[k]).strip().lower() != "off":
                    probs.append(f"isolation.{k} must be 'off' (guide v1.1 Sec. 6)")
    return probs


def load_identity(path: Path | None = None) -> dict:
    """The owner's record of the AI interface, model and isolation (V8; guide v1.1 Sec. 6). Required before the first
    review. Refused when missing, malformed, with a placeholder left in, or with a required isolation setting not
    switched off. Covers the ChatGPT Temporary Chat route; the API route of guide Sec. 6 is not supported here."""
    path = Path(path) if path is not None else IDENTITY
    if not path.exists():
        raise ReviewError(f"{path.name} is missing: the owner must record the AI interface and model before any review (V8)")
    try:
        ident = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ReviewError(f"AI identity record is not valid UTF-8 JSON: {e}") from None
    probs = identity_problems(ident)
    if probs:
        raise ReviewError("AI identity record not acceptable: " + "; ".join(probs))
    return ident


def identity_sha256(path: Path | None = None) -> str:
    """SHA-256 of the identity record in force (LF-normalised), stored with each AI review in the ledger."""
    path = Path(path) if path is not None else IDENTITY
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def guide_extract(guide_text: str) -> str:
    """Guide v1.1 Sec. 3 (decision procedure) and Sec. 4 (evidence rules), verbatim."""
    m = re.search(r"^## 3\. .*?(?=^## 5\. )", guide_text, re.S | re.M)
    if not m:
        raise ReviewError("guide sections 3-4 not found")
    return m.group(0).strip() + "\n"


def prompt_template() -> str:
    return TEMPLATE.read_text(encoding="utf-8").strip() + "\n\n" + guide_extract(GUIDE.read_text(encoding="utf-8"))


def template_sha256() -> str:
    return hashlib.sha256(prompt_template().encode("utf-8")).hexdigest()


def build_prompt(packets: list[dict], identity_path: Path | None = None) -> tuple[str, str]:
    """(prompt text, template SHA-256). Refused until the owner's identity record exists."""
    load_identity(identity_path)
    parts = [prompt_template(), "\n== Candidates ==\n"]
    for p in packets:
        parts.append(p["text"])
        parts.append("")
    return "\n".join(parts), template_sha256()


def _json_objects(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        s = line.strip().rstrip(",")
        if s.startswith("{") and s.endswith("}"):
            try:
                out.append(json.loads(s))
            except json.JSONDecodeError:
                continue
    return out


def parse_ai_response(text: str, packets: list[dict], identity: dict, *, datetime_utc: str, prompt_sha256: str) -> dict:
    """AI-review records from a verbatim response. Returns {"records", "problems", "absent"}; never invents values."""
    by_id = {p["candidate_id"]: p for p in packets}
    records, problems, seen = [], [], set()
    for obj in _json_objects(text):
        cid = obj.get("candidate_id")
        if cid not in by_id:
            problems.append(f"response names unknown candidate {cid!r}")
            continue
        if cid in seen:
            problems.append(f"response repeats candidate {cid}")
            continue
        seen.add(cid)
        site = {"site_id": cid} | {k: obj[k] for k in COMPARED_FIELDS if k in obj}
        missing = [k for k in COMPARED_FIELDS if k not in obj]
        incomplete = [k for k in ("status",) + AI_EXTRA if k not in obj]
        if incomplete or obj.get("status") not in ("ok", "insufficient_context"):
            # never filled in: the record is rejected and the candidate counts as not reviewed
            problems.append(f"{cid}: AI output incomplete or invalid ({incomplete or ['status']}); not reviewed")
            seen.discard(cid)
            continue
        meta = {"candidate_id": cid, "annotator": "ai_review", "label_kind": "ai_review", "submitted_utc": datetime_utc,
                "evidence_lines": obj["evidence_lines"], "rationale": obj["rationale"], "ambiguity": obj["ambiguity"],
                "ai": {"interface_or_api": identity["interface_or_api"], "model": identity["model"],
                       "datetime_utc": datetime_utc, "prompt_sha256": prompt_sha256,
                       "packet_sha256": by_id[cid]["sha256"], "status": obj["status"]}}
        rec = {"site": site, "meta": meta, "missing_fields": sorted(missing)}
        errs = validate_record({"site": site, "meta": meta}, "ai_review")
        if errs:
            problems += [f"{cid}: {e}" for e in errs]
            continue
        records.append(rec)
    absent = [c for c in by_id if c not in seen]
    return {"records": records, "problems": problems, "absent": absent}


def _norm(field: str, value):
    return sorted(value) if field == "possible_roles" and isinstance(value, list) else value


def compare(primary: list[dict], ai: list[dict]) -> dict:
    """Disagreements on the 8 compared fields. AI insufficient-context records and AI-absent fields are counted, not
    treated as disagreements."""
    ai_by = {r["site"]["site_id"]: r for r in ai}
    rows, insufficient, not_reviewed = [], [], []
    for p in primary:
        cid = p["meta"]["candidate_id"]
        if p["meta"].get("annotator_added"):
            continue
        a = ai_by.get(cid)
        if a is None:
            not_reviewed.append(cid)
            continue
        if a["meta"]["ai"]["status"] == "insufficient_context":
            insufficient.append(cid)
            continue
        for f in COMPARED_FIELDS:
            if f not in a["site"]:
                continue
            ov, av = _norm(f, p["site"].get(f)), _norm(f, a["site"][f])
            if ov != av:
                rows.append({"candidate_id": cid, "field": f, "owner_value": json.dumps(p["site"].get(f)),
                             "ai_value": json.dumps(a["site"][f])})
    return {"disagreements": rows, "insufficient_context": insufficient, "not_reviewed": not_reviewed}


def write_disagreements(rows: list[dict], path: Path) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["candidate_id", "field", "owner_value", "ai_value", "final_value", "reason",
                                          "category", "context_difference"])
        w.writeheader()
        for r in rows:
            w.writerow({**r, "final_value": "", "reason": "", "category": "", "context_difference": ""})


def read_adjudication(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def adjudicate(primary: list[dict], disagreements: list[dict], adjudication: list[dict]) -> list[dict]:
    """Final labels. Each disagreement needs exactly one adjudication row; rows for agreed fields are refused."""
    key = lambda r: (r["candidate_id"], r["field"])
    dis = {key(r): r for r in disagreements}
    adj: dict[tuple[str, str], dict] = {}
    for r in adjudication:
        k = key(r)
        if k in adj:
            raise ReviewError(f"two adjudication rows for {k}")
        if k not in dis:
            raise ReviewError(f"adjudication row for {k}, which is not a disagreement")
        if r.get("category") not in CATEGORIES:
            raise ReviewError(f"{k}: category must be one of {CATEGORIES}")
        if not (r.get("reason") or "").strip():
            raise ReviewError(f"{k}: a reason is required")
        if r.get("context_difference") not in ("true", "false"):
            raise ReviewError(f"{k}: context_difference must be 'true' or 'false'")
        adj[k] = r
    missing = [k for k in dis if k not in adj]
    if missing:
        raise ReviewError(f"{len(missing)} disagreement(s) not adjudicated: {missing[:3]}")
    finals = []
    for p in primary:
        cid = p["meta"]["candidate_id"]
        site, meta = json.loads(json.dumps(p["site"])), json.loads(json.dumps(p["meta"]))
        unresolved = list(meta.get("unresolved") or [])
        reasons = [meta["unresolved_reason"]] if meta.get("unresolved_reason") else []
        for (c, f), r in adj.items():
            if c != cid:
                continue
            owner_v, ai_v = json.loads(dis[(c, f)]["owner_value"]), json.loads(dis[(c, f)]["ai_value"])
            cat = r["category"]
            if cat == "unresolved":
                unresolved.append(f)
                reasons.append(f"{f}: {r['reason']}")
                continue
            final_v = json.loads(r["final_value"]) if r["final_value"].strip() else None
            if cat == "kept" and _norm(f, final_v) != _norm(f, owner_v):
                raise ReviewError(f"{(c, f)}: 'kept' must keep the owner's value")
            if cat == "adopted_ai" and _norm(f, final_v) != _norm(f, ai_v):
                raise ReviewError(f"{(c, f)}: 'adopted_ai' must take the AI's value")
            if cat == "third_value" and _norm(f, final_v) in (_norm(f, owner_v), _norm(f, ai_v)):
                raise ReviewError(f"{(c, f)}: 'third_value' must differ from both")
            site[f] = final_v
        meta["label_kind"] = "final"
        if unresolved:
            meta["unresolved"] = sorted(set(unresolved))
            meta["unresolved_reason"] = "; ".join(reasons)
        rec = {"site": site, "meta": meta}
        errs = validate_record(rec, "final")
        if errs:
            raise ReviewError(f"{cid}: final label invalid: {errs}")
        finals.append(rec)
    return finals


def unresolved_report(finals: list[dict]) -> dict:
    """Unresolved counts (V9). The > 5% flag applies to eligible sites (protocol Sec. 5.6)."""
    eligible = [r for r in finals if r["site"]["eligible"] or "eligible" in (r["meta"].get("unresolved") or [])]
    unres = [r for r in eligible if r["meta"].get("unresolved")]
    share = len(unres) / len(eligible) if eligible else 0.0
    by_field: dict[str, int] = {}
    for r in finals:
        for f in r["meta"].get("unresolved") or []:
            by_field[f] = by_field.get(f, 0) + 1
    return {"eligible_or_unresolved": len(eligible), "with_unresolved_field": len(unres), "share": share,
            "flag_over_5_percent": share > 0.05, "by_field": by_field,
            "list": [{"candidate_id": r["meta"]["candidate_id"], "fields": r["meta"]["unresolved"],
                      "reason": r["meta"].get("unresolved_reason", "")} for r in unres]}


__all__ = ["ReviewError", "LabelError", "load_identity", "build_prompt", "parse_ai_response", "compare",
           "write_disagreements", "read_adjudication", "adjudicate", "unresolved_report", "template_sha256",
           "identity_problems", "identity_sha256"]
