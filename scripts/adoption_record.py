"""Adoption records of the Phase 3 protocol: SHA-256 of every normative document.

    python scripts/adoption_record.py           # rewrite the CURRENT record (adoption_record_v1.0.5-r6.json)
    python scripts/adoption_record.py --check   # exit 1 if any current or historical hash is no longer satisfied

Records, oldest first; only the current one is ever (re)written:
* adoption_record_v1.0.4.json     (16 Nov 2026; protocol v1.0.4)
* adoption_record_v1.0.5.json     (18 Nov 2026; protocol v1.0.5, owner-approved pre-F1 decision register)
* adoption_record_v1.0.5-r1.json  (19 Nov 2026; code fixes G05/G06 after the second isolated AI review)
* adoption_record_v1.0.5-r2.json  (19 Nov 2026; editorial corrections for G01, G04, G07, G08, G09, G10, G11)
* adoption_record_v1.0.5-r3.json  (19 Nov 2026; owner decisions G02, G03, G08, G10)
* adoption_record_v1.0.5-r4.json  (19 Nov 2026; owner confirmation of G08 after third-review finding TB01)
* adoption_record_v1.0.5-r5.json  (19 Nov 2026; labelling-rule decisions TA06, TA07, TA11, TA19)
* adoption_record_v1.0.5-r6.json  (19 Nov 2026; CURRENT: pre-F1 analysis decisions; TA01 outcome: F1 blocked)

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
RECORD = SPEC / "adoption_record_v1.0.5-r6.json"
HISTORY = [SPEC / "adoption_record_v1.0.4.json", SPEC / "adoption_record_v1.0.5.json",
           SPEC / "adoption_record_v1.0.5-r1.json", SPEC / "adoption_record_v1.0.5-r2.json",
           SPEC / "adoption_record_v1.0.5-r3.json", SPEC / "adoption_record_v1.0.5-r4.json",
           SPEC / "adoption_record_v1.0.5-r5.json"]
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
    # v1.0.5-r3: the frozen H4 tool registry (owner decision G08)
    "pqscan/bench/h4.py",
    # v1.0.5-r6: the supported-API list that defines a site (owner decision TA10)
    "docs/specification/api_coverage.md",
]


def sha256_text(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def archive_files() -> list[Path]:
    return sorted(p for p in ARCHIVE.rglob("*") if p.is_file())


def build() -> dict:
    return {
        "record": "Phase 3 protocol v1.0.5, revision r6: owner decisions TA03, TA04, TA05, TA08, TA28 (H1a, H3, H4 "
                  "computation), TA09 (kappa rule names the owner intra-rater kappa), TA10 (api_coverage.md hashed), TA17 "
                  "(K = 7 asserted in the E driver), TA22 (unresolved bounding for F-A and H1 as sensitivities), W6 "
                  "(policy citation precision), N1 (limitation), D14 (Mehl reason). TA01: S16 not excluded retrospectively; "
                  "calibration criterion 2 not met; F1 blocked. No hypothesis, threshold, test, family, sampling rule or "
                  "label outcome changed.",
        "protocol_version": "1.0.5-r6",
        "annotation_guide_version": "1.2-r5",
        "analysis_plan_version": "1.0.1-r3",
        "role_taxonomy_version": "1.1-r5",
        "data_dictionary_version": "1.1-r3",
        "benchmark_schema_version": "1.2",
        "synthetic_generator_version": "1.1",
        "scoring_policy_version": "1.0.1",
        "recommendation_policy_version": "1.1 (citation precision r6)",
        "adopted_utc_date": "2026-11-19",
        "basis": "owner decisions docs/audit/owner_decisions_pre_f1_analysis_2026-11-19.md and "
                 "docs/audit/ta01_s16_historical_verification.md; previous records v1.0.4, v1.0.5, v1.0.5-r1 to "
                 "v1.0.5-r5 are kept unchanged",
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
