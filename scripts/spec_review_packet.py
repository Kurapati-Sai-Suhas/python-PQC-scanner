"""Specification-review packets for the isolated ChatGPT reviews (protocol Sec. 3: "The specification review is
'ChatGPT review with owner sign-off'").

    python scripts/spec_review_packet.py                    # (re)write the current packet (v1.0.5, second review)
    python scripts/spec_review_packet.py --review v1.0.4    # (re)write the first-review packet (historical record)
    python scripts/spec_review_packet.py --check            # exit 1 if any committed packet no longer reproduces

A packet = the fixed instructions of that review followed by the specification documents, each with its SHA-256
(LF-normalised, as in scripts/adoption_record.py), split at line boundaries into numbered parts of at most
MAX_PART_CHARS characters for pasting into one fresh isolated chat. Deterministic: no timestamps, no commit id, no
identity values (those belong in the owner's review record).

The v1.0.4 packet is the record of what the first review saw. Documents corrected since then are read from their
byte-identical archive copies (docs/specification/archive/v1.0.4/), and the pre-F1 run specification from git at the
commit the first packet was built from, so that packet keeps reproducing exactly.
This script prepares packets only. It never contacts any AI service and never starts a review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_PART_CHARS = 30_000
ARCHIVE_V104 = "docs/specification/archive/v1.0.4"
ARCHIVE_V105 = "docs/specification/archive/v1.0.5"   # texts the second review saw, for files changed after it (G05)
V104_PACKET_COMMIT = "547ce08"     # the commit the first-review packet was built from

DOCS_V104 = [   # reading order: what is studied, how it is analysed, decisions, how it is labelled, definitions, formats
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
DOCS_V105 = [
    "docs/review/spec_review_v1.0.5/decision_status.md",          # what is adopted, what is pending (read first)
    "docs/specification/evaluation_protocol.md",
    "docs/specification/evaluation_protocol_v1.0.3.md",           # F16: normative for H1, H3, H4 (as interpreted)
    "docs/specification/phase3_analysis_plan.md",
    "docs/specification/phase3_decisions.md",
    "docs/specification/run_specification_pre_f1.md",
    "docs/specification/run_specification_pre_f1.json",
    "docs/specification/amendment_v1.0.5.md",
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
    "pqscan/bench/candidates.py",                                 # sampling rule as implemented (V6)
    "pqscan/bench/frame_audit.py",                                # F18
    "pqscan/bench/multicall.py",                                  # F03
]
REVIEWS = {
    "v1.0.4": {"dir": "docs/review/spec_review_v1.0.4", "protocol": "1.0.4", "guide": "1.1", "plan": "1.0",
               "docs": DOCS_V104, "packet": "spec-review-v1.0.4"},
    "v1.0.5": {"dir": "docs/review/spec_review_v1.0.5", "protocol": "1.0.5", "guide": "1.2", "plan": "1.0.1",
               "docs": DOCS_V105, "packet": "spec-review-v1.0.5"},
}
CURRENT = "v1.0.5"


def norm_bytes(b: bytes) -> str:
    return b.replace(b"\r\n", b"\n").decode("utf-8")


def norm_text(path: Path) -> str:
    return norm_bytes(path.read_bytes())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_doc(review: str, rel: str, root: Path) -> str:
    """The text of `rel` as that review saw it."""
    if review == "v1.0.5":
        arch = root / ARCHIVE_V105 / Path(rel).name           # basenames in DOCS_V105 are unique
        if arch.exists():
            return norm_text(arch)
    if review == "v1.0.4":
        arch = root / ARCHIVE_V104 / Path(rel).name           # basenames in DOCS_V104 are unique
        if arch.exists():
            return norm_text(arch)
        if rel.startswith("docs/specification/run_specification_pre_f1"):
            r = subprocess.run(["git", "show", f"{V104_PACKET_COMMIT}:{rel}"], cwd=root, capture_output=True)
            if r.returncode == 0:
                return norm_bytes(r.stdout)
    return norm_text(root / rel)


def blocks(review: str, root: Path = ROOT) -> tuple[str, list[dict], list[str]]:
    cfg = REVIEWS[review]
    instr = norm_text(root / cfg["dir"] / "review_instructions.md")
    docs, lines = [], []
    for rel in cfg["docs"]:
        text = read_doc(review, rel, root)
        if not text.endswith("\n"):
            text += "\n"
        h = sha256_text(text)
        docs.append({"path": rel, "sha256": h, "chars": len(text)})
        lines.append(f"=== BEGIN DOCUMENT: {rel} (sha256 {h}) ===\n")
        lines.extend(text.splitlines(keepends=True))
        lines.append(f"=== END DOCUMENT: {rel} ===\n\n")
    return instr, docs, lines


def build(review: str = CURRENT, root: Path = ROOT) -> tuple[list[str], dict]:
    cfg = REVIEWS[review]
    instr, docs, lines = blocks(review, root)
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
        top = f"PART {i} OF {n} — specification review packet (protocol v{cfg['protocol']})\n\n"
        if i < n:
            bottom = f"\nEND OF PART {i} OF {n}. Reply only: RECEIVED PART {i} OF {n}\n"
        else:
            bottom = f"\nEND OF PACKET (PART {n} OF {n}). Now produce the review in the OUTPUT FORMAT given in PART 1.\n"
        parts.append(top + "".join(body) + bottom)
    manifest = {
        "packet": cfg["packet"],
        "protocol_version": cfg["protocol"], "annotation_guide_version": cfg["guide"], "analysis_plan_version": cfg["plan"],
        "instructions": {"path": f"{cfg['dir']}/review_instructions.md", "sha256": sha256_text(instr)},
        "documents": docs,
        "max_part_chars": MAX_PART_CHARS,
        "parts": [{"file": f"part_{i:02d}_of_{n:02d}.txt", "sha256": sha256_text(p), "chars": len(p)}
                  for i, p in enumerate(parts, 1)],
        "note": "Paste the parts in order into ONE fresh isolated session configured as recorded in "
                "docs/benchmark/ai_review_identity.json. Save the verbatim reply and the conversation export.",
    }
    return parts, manifest


def packet_dir(review: str, root: Path = ROOT) -> Path:
    return root / REVIEWS[review]["dir"] / "packet"


def write(review: str = CURRENT, root: Path = ROOT) -> dict:
    parts, manifest = build(review, root)
    out = packet_dir(review, root)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("part_*.txt"):
        old.unlink()
    for meta, text in zip(manifest["parts"], parts):
        (out / meta["file"]).write_text(text, encoding="utf-8", newline="\n")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return manifest


def check(review: str = CURRENT, root: Path = ROOT) -> list[str]:
    """Problems between a committed packet and a fresh in-memory build (empty list = up to date)."""
    parts, manifest = build(review, root)
    out = packet_dir(review, root)
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
    """'recorded' only when the identity record passes pqscan.bench.review.load_identity (V8; guide Sec. 6)."""
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
    ap.add_argument("--review", choices=sorted(REVIEWS), default=CURRENT)
    a = ap.parse_args(argv)
    if a.check:
        bad = 0
        for review in sorted(REVIEWS):
            problems = check(review)
            for p in problems:
                print(f"{review} packet out of date: {p}")
            bad += bool(problems)
        print("AI-review identity:", identity_status())
        return 1 if bad else 0
    m = write(a.review)
    print(f"wrote {len(m['parts'])} parts ({sum(p['chars'] for p in m['parts'])} characters) to "
          f"{packet_dir(a.review).relative_to(ROOT).as_posix()}/")
    print("AI-review identity:", identity_status())
    return 0


if __name__ == "__main__":
    sys.exit(main())
