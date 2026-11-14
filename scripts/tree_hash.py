"""Reproducible SHA-256 fingerprint of the frozen source tree (used when no git tag exists).

    python scripts/tree_hash.py            # prints the hash and writes nothing
    python scripts/tree_hash.py --manifest docs/implementation/freeze_manifest.json

The hash covers every file under the listed paths (sorted, POSIX paths, line endings normalised to
LF so a Windows/Linux checkout gives the same value). Caches and virtual environments are excluded.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ["pqscan", "tests", "scripts", "experiments", "benchmark", "docs/specification", "pyproject.toml", "README.md"]
EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", ".venv", ".git"}
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".toml", ".txt", ".csv", ".cfg"}


def files() -> list[Path]:
    out = []
    for inc in INCLUDE:
        p = ROOT / inc
        if p.is_file():
            out.append(p)
        elif p.is_dir():
            out += [f for f in p.rglob("*") if f.is_file() and not (set(f.relative_to(ROOT).parts) & EXCLUDE_PARTS)
                    and ".egg-info" not in str(f)]
    return sorted(out, key=lambda f: f.relative_to(ROOT).as_posix())


def digest(f: Path) -> str:
    data = f.read_bytes()
    if f.suffix in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path)
    a = ap.parse_args()
    entries = [(f.relative_to(ROOT).as_posix(), digest(f)) for f in files()]
    tree = hashlib.sha256("".join(f"{h}  {p}\n" for p, h in entries).encode()).hexdigest()
    print(f"tree sha256 {tree} over {len(entries)} files")
    if a.manifest:
        a.manifest.parent.mkdir(parents=True, exist_ok=True)
        a.manifest.write_text(json.dumps({"created_utc": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
                                          "tree_sha256": tree, "files": dict(entries)}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
