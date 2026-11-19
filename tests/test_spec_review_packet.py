"""Specification-review packets (scripts/spec_review_packet.py): complete, hashed, deterministic, size-limited,
instructions first, free of local paths, secrets, labels and tool outputs, and in sync with the committed packets.
The v1.0.4 packet is the frozen record of the first review; the v1.0.5 packet is the second review's."""
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
REVIEWS = sorted(SRP.REVIEWS)


def _h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@pytest.mark.parametrize("review", REVIEWS)
def test_deterministic_and_committed_packet_is_current(review):
    p1, m1 = SRP.build(review)
    p2, m2 = SRP.build(review)
    assert p1 == p2 and m1 == m2
    assert SRP.check(review) == [], f"committed {review} packet out of date"


def test_first_review_packet_is_frozen():
    """The first review saw the v1.0.4 texts; the archive copies reproduce them byte-for-byte."""
    m = json.loads((ROOT / "docs/review/spec_review_v1.0.4/packet/manifest.json").read_text(encoding="utf-8"))
    rec = json.loads((ROOT / "docs/specification/adoption_record_v1.0.4.json").read_text(encoding="utf-8"))
    for d in m["documents"]:
        if d["path"] in rec["documents"]:
            assert d["sha256"] == rec["documents"][d["path"]], d["path"]
    assert m["protocol_version"] == "1.0.4" and len(m["parts"]) == 5


@pytest.mark.parametrize("review", REVIEWS)
def test_all_documents_included_with_correct_hashes(review):
    parts, m = SRP.build(review)
    joined = "".join(parts)
    cfg = SRP.REVIEWS[review]
    assert [d["path"] for d in m["documents"]] == cfg["docs"]
    required = {"docs/specification/evaluation_protocol.md", "docs/benchmark/annotation_guide.md",
                "docs/specification/phase3_analysis_plan.md", "docs/specification/phase3_decisions.md",
                "docs/specification/run_specification_pre_f1.md", "docs/specification/run_specification_pre_f1.json"}
    if not review.endswith("-B"):                     # Package B audits the closure record, not the spec
        assert required <= set(cfg["docs"])
    for d in m["documents"]:
        text = SRP.read_doc(review, d["path"], ROOT)
        text = text if text.endswith("\n") else text + "\n"
        assert d["sha256"] == _h(text)
        begin = f"=== BEGIN DOCUMENT: {d['path']} (sha256 {d['sha256']}) ===\n"
        end = f"=== END DOCUMENT: {d['path']} ===\n"
        i, j = joined.index(begin), joined.index(end)
        assert i < j
        body = joined[i + len(begin):j]
        body = re.sub(r"\nEND OF PART \d+ OF \d+\. Reply only: RECEIVED PART \d+ OF \d+\n"
                      r"PART \d+ OF \d+ — [^\n]+ \(protocol v[\w.-]+\)\n\n", "", body)
        assert body == text


def test_second_packet_contains_v103_and_the_normative_implementation_rules():
    docs = SRP.REVIEWS["v1.0.5"]["docs"]
    for rel in ("docs/specification/evaluation_protocol_v1.0.3.md", "pqscan/bench/candidates.py",
                "pqscan/bench/frame_audit.py", "pqscan/bench/multicall.py", "docs/specification/amendment_v1.0.5.md",
                "docs/review/spec_review_v1.0.5/decision_status.md"):
        assert rel in docs
    assert docs[0].endswith("decision_status.md")                     # adopted vs pending is read first
    status = SRP.norm_text(ROOT / docs[0])
    assert "## Adopted" in status and "## Pending" in status and "External human review" in status


def test_current_versions_match_the_documents():
    _, m = SRP.build("v1.0.5")
    proto = SRP.norm_text(ROOT / "docs/specification/evaluation_protocol.md")
    guide = SRP.norm_text(ROOT / "docs/benchmark/annotation_guide.md")
    assert m["protocol_version"] == "1.0.5" and proto.startswith("# Evaluation protocol (v1.0.5")
    assert m["annotation_guide_version"] == "1.2" and guide.startswith("# Annotation guide for PyPQC-RoleBench (v1.2)")


@pytest.mark.parametrize("review", REVIEWS)
def test_parts_respect_size_limit_and_framing(review):
    parts, m = SRP.build(review)
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


@pytest.mark.parametrize("review", REVIEWS)
def test_instructions_come_first_and_are_hashed(review):
    parts, m = SRP.build(review)
    instr = SRP.norm_text(ROOT / SRP.REVIEWS[review]["dir"] / "review_instructions.md")
    assert m["instructions"]["sha256"] == _h(instr)
    head = parts[0].split("\n", 2)[2]
    assert head.startswith("REVIEW INSTRUCTIONS (fixed)\n\n" + instr)
    assert parts[0].index(instr) < parts[0].index("=== BEGIN DOCUMENT:")
    for rule in ("RECEIVED PART", "OUTPUT FORMAT", "needs external verification"):
        assert rule.lower() in instr.lower()


def test_second_review_instructions_carry_the_required_rules():
    instr = SRP.norm_text(ROOT / "docs/review/spec_review_v1.0.5/review_instructions.md").lower()
    for rule in ("do not start the review early", "verify every claim", "confirmed-contradiction", "missing-evidence",
                 "do not invent defects", "external standards verification", "limitations of this review",
                 "never conclude that the research is validated", "internal consistency is not evidence"):
        assert rule in instr, rule


@pytest.mark.parametrize("review", REVIEWS)
def test_no_local_paths_secrets_labels_or_tool_outputs(review):
    parts, m = SRP.build(review)
    blob = "".join(parts) + json.dumps(m)
    for pat in (r"[A-Za-z]:\\Users", r"/c/Users", r"(?i)appdata", r"@gmail\.com",
                r"sk-[A-Za-z0-9]{20,}", r"(?i)api[_-]?key\s*[:=]\s*\S{12,}", r"ghp_[A-Za-z0-9]{20,}"):
        assert not re.search(pat, blob), pat
    for forbidden in ("runs/", "docs/dev/", "raw_tool_outputs", "benchmark/annotation/", "benchmark/synthetic/",
                      "docs/pilot/", "benchmark/candidates/", "docs/benchmark/ai_review_identity"):
        assert not any(d["path"].startswith(forbidden) for d in m["documents"]), forbidden


@pytest.mark.parametrize("review", REVIEWS)
def test_no_timestamp_commit_or_identity_values_in_manifest(review):
    _, m = SRP.build(review)
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
    cfg = SRP.REVIEWS["v1.0.5"]
    for rel in cfg["docs"] + [f"{cfg['dir']}/review_instructions.md"]:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dst)
    SRP.write("v1.0.5", tmp_path)
    assert SRP.check("v1.0.5", tmp_path) == []
    p = tmp_path / "docs/specification/phase3_decisions.md"
    p.write_text(p.read_text(encoding="utf-8") + "\nedited\n", encoding="utf-8")
    assert any("manifest differs" in x for x in SRP.check("v1.0.5", tmp_path))
    with pytest.raises(FileNotFoundError):
        SRP.build("v1.0.5", tmp_path / "missing")


def test_third_review_package_a_is_uncoached_and_package_b_carries_the_closure_record():
    a, b = SRP.REVIEWS["v1.0.5-r3-A"]["docs"], SRP.REVIEWS["v1.0.5-r3-B"]["docs"]
    assert not [d for d in a if d.startswith(("docs/review/", "docs/audit/", "tests/"))]       # no history, no coaching
    assert {"pqscan/bench/h4.py", "pqscan/bench/guard_diagnostics.py", "pqscan/bench/h2.py"} <= set(a)
    assert b[0] == SRP.R3_DIFF and "docs/audit/owner_decisions_g02_g03_g08_g10.md" in b
    assert (ROOT / SRP.R3_DIFF).read_text(encoding="utf-8") == SRP.changes_diff()               # diff is current
    ia = (ROOT / SRP.REVIEWS["v1.0.5-r3-A"]["dir"] / "review_instructions.md").read_text(encoding="utf-8")
    assert "decision_status" not in ia and "no earlier review, finding, decision record" in ia
