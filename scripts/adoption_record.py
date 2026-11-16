"""Adoption record of protocol v1.0.4 (R4-19 item 16): SHA-256 of every normative Phase 3 document.

    python scripts/adoption_record.py           # rewrite docs/specification/adoption_record_v1.0.4.json
    python scripts/adoption_record.py --check   # exit 1 if any recorded hash no longer matches

Hashes use LF-normalised text, like scripts/tree_hash.py, so Windows and Linux checkouts agree. The record is
regenerated (and committed) whenever an adopted document is corrected before F1; the F1 freeze record hashes
the same files again.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "specification" / "adoption_record_v1.0.4.json"
DOCS = [
    "docs/specification/evaluation_protocol.md",
    "docs/specification/phase3_analysis_plan.md",
    "docs/specification/phase3_decisions.md",
    "docs/benchmark/annotation_guide.md",
    "docs/specification/scoring_policy.md",
    "docs/specification/data_dictionary.md",
    "docs/specification/role_taxonomy.md",
    "docs/specification/recommendation_policy.md",
    "docs/benchmark/benchmark_schema.json",
    "docs/specification/evaluation_protocol_v1.0.3.md",
    "docs/benchmark/annotation_guide_v1.0.md",
]


def sha256_text(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def build() -> dict:
    return {
        "record": "Phase 3 protocol adoption (R4-19 item 16)",
        "protocol_version": "1.0.4",
        "annotation_guide_version": "1.1",
        "analysis_plan_version": "1.0",
        "adopted_utc_date": "2026-11-16",
        "basis": "owner approval of R4-18 as amended by R4-21 Sec. 6 (C1-C6) and edge-case rules A-D, before any test-split access",
        "documents": {d: sha256_text(ROOT / d) for d in DOCS},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        rec = json.loads(RECORD.read_text(encoding="utf-8"))
        bad = [d for d, h in rec["documents"].items() if sha256_text(ROOT / d) != h]
        for d in bad:
            print("hash mismatch:", d)
        return 1 if bad else 0
    RECORD.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", RECORD.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
