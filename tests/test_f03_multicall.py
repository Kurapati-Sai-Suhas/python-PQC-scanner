"""F03 (owner decision): statement-level sampling (V6) is kept; multi-call candidate statements are marked from source
only; the measurement evidence reproduces; the census never reads tool attribution; the pool and orders are unchanged."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from pqscan.bench import annotate as AN
from pqscan.bench import multicall as M

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("f03_census", ROOT / "scripts" / "f03_multicall_census.py")
CEN = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CEN)
EVIDENCE = ROOT / "docs" / "audit" / "evidence" / "f03_multicall_pool.json"
PRE_CORRECTION_COMMIT = "d051cc1"          # last commit before the F03 decision; orders must be byte-identical to it


def _checkouts_ready() -> bool:
    try:
        for of in CEN.order_files(ROOT):
            o = json.loads(of.read_text(encoding="utf-8"))
            repo = ROOT / ".cache" / "repos" / of.parent.name / o["repo"]
            head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            if head != o["commit"]:
                return False
        return bool(CEN.order_files(ROOT))
    except OSError:
        return False


def test_statement_calls_are_listed_in_source_order():
    src = ("x = self.public_key().prepared_key.verify(sig, msg)\n"
           "a, b = k.sign(m), k.verify(s, m)\n"
           "if key.verify(s, m):\n"
           "    other.sign(m)\n"
           "c = (\n"
           "    mlkem.public_key().public_bytes_raw()\n"
           "    + x25519.public_key().public_bytes_raw()\n"
           ")\n")
    assert [(c["kind"], c["name"]) for c in M.statement_calls(src, 1)] == [("key_material", "public_key"),
                                                                            ("operation", "verify")]
    assert [c["name"] for c in M.statement_calls(src, 2)] == ["sign", "verify"]
    assert [c["name"] for c in M.statement_calls(src, 3)] == ["verify"]          # compound header only, not its body
    two = M.statement_calls(src, 5)
    assert [c["name"] for c in two] == ["public_key", "public_key"] and two[0]["line"] < two[1]["line"]
    assert M.statement_calls(src, 4) == [{"line": 4, "col": 10, "name": "sign", "kind": "operation"}]
    assert M.statement_calls("def broken(:\n", 1) is None and M.statement_calls(src, 99) is None
    assert M.statement_calls(src, 1) == M.statement_calls(src, 1)                 # deterministic


def test_mark_flags_only_statements_with_two_or_more_calls():
    assert M.mark("k.sign(m)\n", 1) == {"multi_call": False}
    m = M.mark("k.public_key().verify(s, m)\n", 1)
    assert m["multi_call"] is True and [c["name"] for c in m["calls"]] == ["public_key", "verify"]
    assert M.mark("padding.PKCS1v15()\n", 1) == {"multi_call": False}              # no supported call by name


def test_issued_todo_entry_is_marked_from_source(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\nk.public_key().verify(s, m)\n", encoding="utf-8")
    assert AN._multi(tmp_path, {"file": "a.py", "line": 2})["multi_call"] is True
    assert AN._multi(tmp_path, {"file": "a.py", "line": 1}) == {"multi_call": False}
    assert AN._multi(tmp_path, {"file": "missing.py", "line": 1}) == {"multi_call": False}


def test_census_never_reads_tool_attribution(tmp_path, monkeypatch):
    cand = tmp_path / "benchmark" / "candidates" / "development"
    cand.mkdir(parents=True)
    (cand / "order_x.json").write_text(json.dumps({"repo": "x", "commit": "c0ffee", "strata": {
        "S1-app": [{"candidate_id": "C-1", "file": "a.py", "line": 1, "scope": "app"}]}}), encoding="utf-8")
    (cand / "pool_sources_x.json").write_text('{"a.py:1": ["some-tool"]}', encoding="utf-8")
    src = tmp_path / ".cache" / "repos" / "development" / "x"
    src.mkdir(parents=True)
    (src / "a.py").write_text("k.public_key().verify(s, m)\n", encoding="utf-8")
    seen: list[str] = []
    real_rt, real_rb = Path.read_text, Path.read_bytes
    monkeypatch.setattr(Path, "read_text", lambda self, *a, **k: (seen.append(str(self)), real_rt(self, *a, **k))[1])
    monkeypatch.setattr(Path, "read_bytes", lambda self, *a, **k: (seen.append(str(self)), real_rb(self, *a, **k))[1])
    monkeypatch.setattr(CEN.subprocess, "run", lambda *a, **k: SimpleNamespace(stdout="c0ffee\n"))
    res = CEN.census(tmp_path)
    assert res["pool_candidates"] == 1 and len(res["multi_call"]) == 1
    assert seen and not any("pool_sources" in s for s in seen)


@pytest.mark.skipif(not _checkouts_ready(), reason="pinned DV checkouts not present (scripts/fetch_pinned.py repos)")
def test_committed_evidence_reproduces_eight_multi_call_candidates():
    stored = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert CEN.census(ROOT) == stored
    assert stored["pool_candidates"] == 3503 and len(stored["multi_call"]) == 8
    assert {m["stratum"] for m in stored["multi_call"]} <= {"S1-app", "S1-nonapp"}


def test_pool_and_orders_are_not_rebuilt():
    stored = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    for rel, h in stored["orders_sha256"].items():
        assert hashlib.sha256((ROOT / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == h
        old = subprocess.run(["git", "show", f"{PRE_CORRECTION_COMMIT}:{rel}"], cwd=ROOT, capture_output=True)
        if old.returncode == 0:                    # history available: byte-identical to before the decision
            assert hashlib.sha256(old.stdout.replace(b"\r\n", b"\n")).hexdigest() == h
