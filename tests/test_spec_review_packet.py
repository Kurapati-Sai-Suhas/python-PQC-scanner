"""Specification-review packet (scripts/spec_review_packet.py): complete, hashed, deterministic, size-limited,
instructions first, free of local paths and secrets, and in sync with the committed packet."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("spec_review_packet", ROOT / "scripts" / "spec_review_packet.py")
SRP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SRP)


def _h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_deterministic_and_committed_packet_is_current():
    p1, m1 = SRP.build()
    p2, m2 = SRP.build()
    assert p1 == p2 and m1 == m2
    assert SRP.check() == [], "committed packet out of date: run python scripts/spec_review_packet.py"


def test_all_documents_included_with_correct_hashes():
    parts, m = SRP.build()
    joined = "".join(parts)
    assert [d["path"] for d in m["documents"]] == SRP.DOCS
    required = {"docs/specification/evaluation_protocol.md", "docs/benchmark/annotation_guide.md",
                "docs/specification/phase3_analysis_plan.md", "docs/specification/phase3_decisions.md",
                "docs/specification/run_specification_pre_f1.md", "docs/specification/run_specification_pre_f1.json"}
    assert required <= set(SRP.DOCS)
    for d in m["documents"]:
        text = SRP.norm_text(ROOT / d["path"])
        text = text if text.endswith("\n") else text + "\n"
        assert d["sha256"] == _h(text)
        begin = f"=== BEGIN DOCUMENT: {d['path']} (sha256 {d['sha256']}) ===\n"
        end = f"=== END DOCUMENT: {d['path']} ===\n"
        i, j = joined.index(begin), joined.index(end)
        assert i < j
        # the document body is intact once the part headers/footers that fall inside it are removed
        body = joined[i + len(begin):j]
        body = re.sub(r"\nEND OF PART \d+ OF \d+\. Reply only: RECEIVED PART \d+ OF \d+\n"
                      r"PART \d+ OF \d+ — specification review packet \(protocol v1\.0\.4\)\n\n", "", body)
        assert body == text


def test_adopted_versions_match_the_documents():
    _, m = SRP.build()
    proto = SRP.norm_text(ROOT / "docs/specification/evaluation_protocol.md")
    guide = SRP.norm_text(ROOT / "docs/benchmark/annotation_guide.md")
    assert m["protocol_version"] == "1.0.4" and "1.0.4" in proto
    assert m["annotation_guide_version"] == "1.1" and "1.1" in guide


def test_parts_respect_size_limit_and_framing():
    parts, m = SRP.build()
    n = len(parts)
    assert n == len(m["parts"]) >= 2
    for i, (p, meta) in enumerate(zip(parts, m["parts"]), 1):
        assert len(p) <= SRP.MAX_PART_CHARS
        assert meta["chars"] == len(p) and meta["sha256"] == _h(p)
        assert p.startswith(f"PART {i} OF {n} ")
        if i < n:
            assert p.endswith(f"Reply only: RECEIVED PART {i} OF {n}\n")
        else:
            assert "END OF PACKET" in p.splitlines()[-1]


def test_instructions_come_first_and_are_hashed():
    parts, m = SRP.build()
    instr = SRP.norm_text(SRP.INSTRUCTIONS)
    assert m["instructions"]["sha256"] == _h(instr)
    head = parts[0].split("\n", 2)[2]
    assert head.startswith("REVIEW INSTRUCTIONS (fixed)\n\n" + instr)
    assert parts[0].index(instr) < parts[0].index("=== BEGIN DOCUMENT:")
    for rule in ("RECEIVED PART", "OUTPUT FORMAT", "Do not browse", "needs external verification"):
        assert rule.lower() in instr.lower()


def test_no_local_paths_secrets_or_private_data():
    parts, m = SRP.build()
    blob = "".join(parts) + json.dumps(m)
    for pat in (r"[A-Za-z]:\\Users", r"/c/Users", r"(?i)appdata", r"@gmail\.com",
                r"sk-[A-Za-z0-9]{20,}", r"(?i)api[_-]?key\s*[:=]\s*\S{12,}", r"ghp_[A-Za-z0-9]{20,}"):
        assert not re.search(pat, blob), pat
    for forbidden in ("runs/", "docs/dev/", "raw_tool_outputs", "benchmark/annotation/"):
        assert not any(d["path"].startswith(forbidden) for d in m["documents"])


def test_no_timestamp_commit_or_identity_values_in_manifest():
    _, m = SRP.build()
    s = json.dumps(m)
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", s)
    assert not re.search(r"\b[0-9a-f]{40}\b", s.replace(m["instructions"]["sha256"], ""))  # no git commit id
    assert "recorded_utc" not in s and "interface_or_api" not in s


def test_identity_status_reflects_the_file(tmp_path):
    assert SRP.identity_status(tmp_path).startswith("NOT RECORDED")
    (tmp_path / "docs" / "benchmark").mkdir(parents=True)
    p = tmp_path / "docs" / "benchmark" / "ai_review_identity.json"
    p.write_text("{}", encoding="utf-8")                                   # exists but empty: not accepted
    assert SRP.identity_status(tmp_path).startswith("INVALID")
    iso = {"fresh_temporary_chat_per_batch": "yes"} | {k: "off" for k in (
        "custom_instructions", "memory_and_chat_history_reference", "projects", "connectors", "file_library",
        "browsing_search")}
    p.write_text(json.dumps({"interface_or_api": "TEST interface", "model": "TEST-MODEL",
                             "recorded_utc": "2026-11-16T09:00:00Z", "isolation": iso}), encoding="utf-8")
    assert SRP.identity_status(tmp_path) == "recorded"


def test_check_detects_a_changed_source(tmp_path):
    for rel in SRP.DOCS + [SRP.INSTRUCTIONS.relative_to(ROOT).as_posix()]:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dst)
    SRP.write(tmp_path)
    assert SRP.check(tmp_path) == []
    p = tmp_path / "docs/specification/phase3_decisions.md"
    p.write_text(p.read_text(encoding="utf-8") + "\nedited\n", encoding="utf-8")
    assert any("manifest differs" in x for x in SRP.check(tmp_path))
    with pytest.raises(FileNotFoundError):
        SRP.build(tmp_path / "missing")
