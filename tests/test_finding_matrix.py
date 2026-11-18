"""The verification matrix of the 21 review findings: complete, generated from one table, and honest about status."""
import csv
import importlib.util
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("finding_matrix", ROOT / "scripts" / "finding_matrix.py")
FM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FM)


def test_matrix_files_are_current_and_complete():
    assert FM.main(["--check"]) == 0
    rows = list(csv.DictReader((ROOT / "docs/audit/chatgpt_review_finding_verification.csv").open(encoding="utf-8")))
    ids = [r["id"] for r in rows]
    assert ids[:21] == [f"F{i:02d}" for i in range(1, 22)] and "E01" in ids and "PILOT" in ids
    tally = Counter(r["verdict"].split(" (")[0] for r in rows if r["id"].startswith("F"))
    assert tally == {"VALID": 14, "PARTIALLY VALID": 7}


def test_status_is_never_overstated():
    rows = {r["id"]: r for r in csv.DictReader((ROOT / "docs/audit/chatgpt_review_finding_verification.csv").open(encoding="utf-8"))}
    assert "PENDING" in rows["F14"]["status"]                  # the human review itself is not done
    assert "committed (77f7600)" in rows["E01"]["status"] and "E01 valid" in rows["E01"]["status"]
    assert "PASS" in rows["F05"]["status"]
