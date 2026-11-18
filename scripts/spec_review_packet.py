"""Specification-review packet for the isolated ChatGPT review of protocol v1.0.4 (R4-20 step 3; protocol Sec. 3:
"The specification review is 'ChatGPT review with owner sign-off'").

    python scripts/spec_review_packet.py           # (re)write docs/review/spec_review_v1.0.4/packet/
    python scripts/spec_review_packet.py --check   # exit 1 if the committed packet no longer matches its sources

The packet = the fixed instructions (`docs/review/spec_review_v1.0.4/review_instructions.md`) followed by the adopted
specification documents, each with its SHA-256 (LF-normalised, as in scripts/adoption_record.py), split at line
boundaries into numbered parts of at most MAX_PART_CHARS characters for pasting into one fresh isolated chat.
Deterministic: no timestamps, no commit id, no identity values (those belong in the owner's review record).
This script prepares the packet only. It never contacts any AI service and never starts the review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / "docs" / "review" / "spec_review_v1.0.4"
INSTRUCTIONS = REVIEW_DIR / "review_instructions.md"
PACKET_DIR = REVIEW_DIR / "packet"
MAX_PART_CHARS = 30_000
DOCS = [   # reading order: what is studied, how it is analysed, decisions, how it is labelled, definitions, formats
    "docs/specification/evaluation_protocol.md",
    "docs/specification/phase3_analysis_plan.md",
    "docs/specification/phase3_decisions.md",
    "docs/specification/run_specification_pre_f1.md",
    "docs/specification/run_specification_pre_f1.json",
    "docs/benchmark/annotation_guide.md",
    "docs/specification/role_taxonomy.md",
    "docs/specification/data_dictionary.md",
    "docs/specification/scoring_policy.md",
    "docs/specification/recommendation_policy.md",
    "pqscan/policy/policy_v1_1.yaml",
    "docs/benchmark/benchmark_schema.json",
    "docs/benchmark/meta_schema.json",
    "docs/benchmark/ai_review_prompt_v1.md",
    "pqscan/bench/packets.py",
]


def norm_text(path: Path) -> str:
    return path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def blocks(root: Path = ROOT) -> tuple[str, list[dict], list[str]]:
    """(instructions, document records, the packet body as lines)."""
    instr = norm_text(root / INSTRUCTIONS.relative_to(ROOT))
    docs, lines = [], []
    for rel in DOCS:
        text = norm_text(root / rel)
        if not text.endswith("\n"):
            text += "\n"
        h = sha256_text(text)
        docs.append({"path": rel, "sha256": h, "chars": len(text)})
        lines.append(f"=== BEGIN DOCUMENT: {rel} (sha256 {h}) ===\n")
        lines.extend(text.splitlines(keepends=True))
        lines.append(f"=== END DOCUMENT: {rel} ===\n\n")
    return instr, docs, lines


def build(root: Path = ROOT) -> tuple[list[str], dict]:
    instr, docs, lines = blocks(root)
    head_room = 400                                   # part header + footer
    bodies, cur = [], ["REVIEW INSTRUCTIONS (fixed)\n\n", instr, "\n"]
    for line in lines:
        if len(line) > MAX_PART_CHARS - head_room:
            raise ValueError("a single line is longer than a part")
        if sum(map(len, cur)) + len(line) > MAX_PART_CHARS - head_room:
            bodies.append(cur)
            cur = []
        cur.append(line)
    bodies.append(cur)
    n = len(bodies)
    parts = []
    for i, body in enumerate(bodies, 1):
        top = f"PART {i} OF {n} — specification review packet (protocol v1.0.4)\n\n"
        if i < n:
            bottom = f"\nEND OF PART {i} OF {n}. Reply only: RECEIVED PART {i} OF {n}\n"
        else:
            bottom = f"\nEND OF PACKET (PART {n} OF {n}). Now produce the review in the OUTPUT FORMAT given in PART 1.\n"
        parts.append(top + "".join(body) + bottom)
    manifest = {
        "packet": "spec-review-v1.0.4",
        "protocol_version": "1.0.4", "annotation_guide_version": "1.1", "analysis_plan_version": "1.0",
        "instructions": {"path": INSTRUCTIONS.relative_to(ROOT).as_posix(), "sha256": sha256_text(instr)},
        "documents": docs,
        "max_part_chars": MAX_PART_CHARS,
        "parts": [{"file": f"part_{i:02d}_of_{n:02d}.txt", "sha256": sha256_text(p), "chars": len(p)}
                  for i, p in enumerate(parts, 1)],
        "note": "Paste the parts in order into ONE fresh isolated session configured as recorded in "
                "docs/benchmark/ai_review_identity.json. Save the verbatim reply and the conversation export.",
    }
    return parts, manifest


def write(root: Path = ROOT) -> dict:
    parts, manifest = build(root)
    out = root / PACKET_DIR.relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("part_*.txt"):
        old.unlink()
    for meta, text in zip(manifest["parts"], parts):
        (out / meta["file"]).write_text(text, encoding="utf-8", newline="\n")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return manifest


def check(root: Path = ROOT) -> list[str]:
    """Problems between the committed packet and a fresh in-memory build (empty list = up to date)."""
    parts, manifest = build(root)
    out = root / PACKET_DIR.relative_to(ROOT)
    problems = []
    try:
        stored = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ["manifest.json missing"]
    if stored != manifest:
        problems.append("manifest differs from a fresh build (a source document or the instructions changed)")
    on_disk = sorted(p.name for p in out.glob("part_*.txt"))
    if on_disk != [m["file"] for m in manifest["parts"]]:
        problems.append(f"part files differ: {on_disk}")
    for meta, text in zip(manifest["parts"], parts):
        f = out / meta["file"]
        if f.exists() and norm_text(f) != text:
            problems.append(f"{meta['file']} differs")
    return problems


def identity_status(root: Path = ROOT) -> str:
    """'recorded' only when the identity record passes pqscan.bench.review.load_identity (V8; guide v1.1 Sec. 6)."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from pqscan.bench import review as R
    p = root / "docs" / "benchmark" / "ai_review_identity.json"
    if not p.exists():
        return "NOT RECORDED: the review must not start until the owner records it (V8)"
    try:
        R.load_identity(p)
    except R.ReviewError as e:
        return f"INVALID: {e}"
    return "recorded"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        problems = check()
        for p in problems:
            print("packet out of date:", p)
        print("AI-review identity:", identity_status())
        return 1 if problems else 0
    m = write()
    print(f"wrote {len(m['parts'])} parts ({sum(p['chars'] for p in m['parts'])} characters) to "
          f"{PACKET_DIR.relative_to(ROOT).as_posix()}/")
    print("AI-review identity:", identity_status())
    return 0


if __name__ == "__main__":
    sys.exit(main())
