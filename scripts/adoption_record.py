"""Adoption records of the Phase 3 protocol: SHA-256 of every normative document.

    python scripts/adoption_record.py           # rewrite the CURRENT record (adoption_record_v1.0.5-r2.json)
    python scripts/adoption_record.py --check   # exit 1 if any current or historical hash is no longer satisfied

Records, oldest first; only the current one is ever (re)written:
* adoption_record_v1.0.4.json     (16 Nov 2026; protocol v1.0.4)
* adoption_record_v1.0.5.json     (18 Nov 2026; protocol v1.0.5, owner-approved pre-F1 decision register)
* adoption_record_v1.0.5-r1.json  (19 Nov 2026; code fixes G05/G06 after the second isolated AI review)
* adoption_record_v1.0.5-r2.json  (19 Nov 2026; CURRENT: editorial corrections for G01, G04, G07, G08, G09, G10, G11)

--check verifies every document of the current record against the working tree, and every hash of every historical
record against either the current file or a byte-identical copy in one of the archive folders
`docs/specification/archive/<version>/` (matched by file name). No historical record is rewritten.

Hashes use LF-normalised text, like scripts/tree_hash.py, so Windows and Linux checkouts agree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "specification"
RECORD = SPEC / "adoption_record_v1.0.5-r2.json"
HISTORY = [SPEC / "adoption_record_v1.0.4.json", SPEC / "adoption_record_v1.0.5.json",
           SPEC / "adoption_record_v1.0.5-r1.json"]
ARCHIVE = SPEC / "archive"
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
    # v1.0.5-r2: the policy encoding (its comment was corrected for G09)
    "pqscan/policy/policy_v1_1.yaml",
]


def sha256_text(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def archive_files() -> list[Path]:
    return sorted(p for p in ARCHIVE.rglob("*") if p.is_file())


def build() -> dict:
    return {
        "record": "Phase 3 protocol v1.0.5, revision r2: editorial corrections after the second isolated AI "
                  "specification review (G01, G04, G07, G08, G09, G10, G11); r1 carried the code fixes G05/G06. "
                  "No hypothesis, threshold, metric, estimand, test, family, sampling rule or label outcome changed.",
        "protocol_version": "1.0.5-r2",
        "annotation_guide_version": "1.2-r2",
        "analysis_plan_version": "1.0.1-r2",
        "role_taxonomy_version": "1.1-r2",
        "data_dictionary_version": "1.1",
        "scoring_policy_version": "1.0.1",
        "adopted_utc_date": "2026-11-19",
        "basis": "owner-authorised closure of the second-review findings (docs/audit/second_review_closure.md); "
                 "previous records adoption_record_v1.0.4.json, adoption_record_v1.0.5.json and "
                 "adoption_record_v1.0.5-r1.json are kept unchanged",
        "documents": {d: sha256_text(ROOT / d) for d in DOCS},
        "archived": {p.relative_to(ROOT).as_posix(): sha256_text(p) for p in archive_files()},
    }


def check_history(record: Path) -> list[str]:
    """Every hash of a historical record must still be found: current file, or an archive copy with the same name."""
    rec = json.loads(record.read_text(encoding="utf-8"))
    copies: dict[str, set[str]] = {}
    for p in archive_files():
        copies.setdefault(p.name, set()).add(sha256_text(p))
    bad = []
    for d, h in rec["documents"].items():
        if sha256_text(ROOT / d) != h and h not in copies.get(Path(d).name, set()):
            bad.append(f"{record.name}: the recorded text of {d} is neither current nor archived")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        rec = json.loads(RECORD.read_text(encoding="utf-8"))
        bad = [f"hash mismatch: {d}" for d, h in {**rec["documents"], **rec["archived"]}.items()
               if sha256_text(ROOT / d) != h]
        bad += [f"not in the current record: {d}" for d in DOCS if d not in rec["documents"]]
        for r in HISTORY:
            bad += check_history(r)
        for d in bad:
            print(d)
        return 1 if bad else 0
    RECORD.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", RECORD.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
