"""Adoption records of the Phase 3 protocol: SHA-256 of every normative document.

    python scripts/adoption_record.py           # rewrite docs/specification/adoption_record_v1.0.5.json
    python scripts/adoption_record.py --check   # exit 1 if any recorded hash no longer matches

Two records are checked:
* v1.0.5 (current; adopted 18 Nov 2026 by owner approval of the pre-F1 decision register): every current normative
  document, the pre-F1 run specification and the archived v1.0.4 texts;
* v1.0.4 (historical; `adoption_record_v1.0.4.json`, never rewritten): every recorded hash must still be found, either in
  the current file (documents unchanged since v1.0.4) or in its byte-identical archive copy under
  `docs/specification/archive/v1.0.4/` (documents corrected in v1.0.5).

Hashes use LF-normalised text, like scripts/tree_hash.py, so Windows and Linux checkouts agree. The current record is
regenerated (and committed) whenever an adopted document is corrected before F1; the F1 freeze record hashes the same
files again.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "specification" / "adoption_record_v1.0.5.json"
RECORD_V104 = ROOT / "docs" / "specification" / "adoption_record_v1.0.4.json"
ARCHIVE_V104 = ROOT / "docs" / "specification" / "archive" / "v1.0.4"
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
    # implementation artefacts fixed during R4-19 (normative for annotation; hashed again at F1)
    "docs/benchmark/meta_schema.json",
    "docs/benchmark/ai_review_prompt_v1.md",
    "pqscan/bench/packets.py",
    # v1.0.5: pre-F1 owner decisions (D7, D15, H-1 to H-6, F12) and the amendment record
    "docs/specification/run_specification_pre_f1.md",
    "docs/specification/run_specification_pre_f1.json",
    "docs/specification/amendment_v1.0.5.md",
]


def sha256_text(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def archived() -> list[str]:
    return sorted(p.relative_to(ROOT).as_posix() for p in ARCHIVE_V104.glob("*.md"))


def build() -> dict:
    return {
        "record": "Phase 3 protocol adoption v1.0.5 (pre-F1 corrections after the isolated specification review)",
        "protocol_version": "1.0.5",
        "annotation_guide_version": "1.2",
        "analysis_plan_version": "1.0.1",
        "role_taxonomy_version": "1.1",
        "data_dictionary_version": "1.1",
        "scoring_policy_version": "1.0.1",
        "adopted_utc_date": "2026-11-18",
        "basis": "owner approval of the pre-F1 decision register docs/audit/owner_decision_register_v1.0.5.md, "
                 "before any labelling and any test-split access; supersedes adoption_record_v1.0.4.json, which is kept",
        "documents": {d: sha256_text(ROOT / d) for d in DOCS},
        "archived_v1.0.4": {d: sha256_text(ROOT / d) for d in archived()},
    }


def check_v104() -> list[str]:
    """Every v1.0.4 hash must still exist: in the current file or in its archive copy."""
    rec = json.loads(RECORD_V104.read_text(encoding="utf-8"))
    bad = []
    for d, h in rec["documents"].items():
        here = sha256_text(ROOT / d) == h
        arch = ARCHIVE_V104 / Path(d).name
        if not here and not (arch.exists() and sha256_text(arch) == h):
            bad.append(f"v1.0.4 text of {d} is neither current nor archived")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        rec = json.loads(RECORD.read_text(encoding="utf-8"))
        bad = [f"hash mismatch: {d}" for d, h in {**rec["documents"], **rec["archived_v1.0.4"]}.items()
               if sha256_text(ROOT / d) != h]
        bad += [f"not in the v1.0.5 record: {d}" for d in DOCS if d not in rec["documents"]]
        bad += check_v104()
        for d in bad:
            print(d)
        return 1 if bad else 0
    RECORD.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", RECORD.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
