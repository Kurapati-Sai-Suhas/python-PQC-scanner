"""scripts/f1_readiness.py: reports NOT READY while prerequisites are missing, never performs F1, never writes the real
freeze record or tag, verifies the confirmed eight-member H4 Part 1 set and that the test split is unopened."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("f1_readiness", ROOT / "scripts" / "f1_readiness.py")
F1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F1)


def test_not_ready_and_never_freezes():
    r = F1.run()
    assert r["status"].startswith("NOT READY")
    assert not r["freeze_record_exists"] and not r["freeze_tag_exists"]
    assert any("EXTERNAL HUMAN REVIEW" in m for m in r["missing_prerequisites"])
    assert any("explicit owner approval" in m for m in r["missing_prerequisites"])
    src = (ROOT / "scripts" / "f1_readiness.py").read_text(encoding="utf-8")
    assert "git tag " not in src.replace('"tag", "-l"', "")          # only lists tags, never creates one
    assert "FREEZE_RECORD.write" not in src


def test_h4_part1_verified_and_test_split_unopened():
    items = {i["item"]: i for i in F1.run()["items"]}
    assert items["H4"]["status"] == "VERIFIED" and len(items["H4"]["detail"]) == 8
    assert items["T"]["status"] == "VERIFIED"
