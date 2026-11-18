"""F03 evidence: multi-call statements in the ACTUAL development/validation candidate pool (source only).

    python scripts/f03_multicall_census.py           # (re)write docs/audit/evidence/f03_multicall_pool.json
    python scripts/f03_multicall_census.py --check   # exit 1 if the committed evidence no longer reproduces

Reads ONLY the location-only candidate orders `benchmark/candidates/<split>/order_<repo>.json` and the pinned DV
source checkouts in `.cache/repos/<split>/<repo>/`. It never opens `pool_sources_*.json` (which tool found a line),
any tool output, any label, or any test-split repository. Calls are listed by API name (pqscan.bench.multicall);
no role or eligibility is decided. The sampling unit, the pool and the orders are not changed (owner decision F03).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pqscan.bench import multicall as M  # noqa: E402

SPLITS = ("development", "validation")
OUT = ROOT / "docs" / "audit" / "evidence" / "f03_multicall_pool.json"


def order_files(root: Path = ROOT) -> list[Path]:
    return [f for s in SPLITS for f in sorted((root / "benchmark" / "candidates" / s).glob("order_*.json"))]


def census(root: Path = ROOT) -> dict:
    counts, multi, orders = Counter(), [], {}
    for of in order_files(root):
        raw = of.read_bytes()
        o = json.loads(raw)
        split = of.parent.name
        orders[of.relative_to(root).as_posix()] = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
        repo = root / ".cache" / "repos" / split / o["repo"]
        head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        if head != o["commit"]:
            raise SystemExit(f"{o['repo']}: checkout {head[:12] or 'missing'} is not the pinned commit {o['commit'][:12]}")
        texts: dict[str, str] = {}
        for stratum, rows in o["strata"].items():
            for r in rows:
                if r["file"] not in texts:
                    texts[r["file"]] = (repo / r["file"]).read_text(encoding="utf-8", errors="replace")
                calls = M.statement_calls(texts[r["file"]], r["line"])
                cat = "no_statement" if calls is None else ("0" if not calls else "1" if len(calls) == 1 else ">=2")
                counts[f"{stratum}|{cat}"] += 1
                if cat == ">=2":
                    multi.append({"repo": o["repo"], "file": r["file"], "line": r["line"], "stratum": stratum,
                                  "calls": [f"{c['kind']}:{c['name']}" for c in calls]})
    return {"evidence": "F03 multi-call candidate statements (source-only census of the DV candidate pool)",
            "reads": "order_*.json (locations) and pinned DV source only; never pool_sources_*, tool outputs or labels",
            "orders_sha256": orders, "pool_candidates": sum(counts.values()),
            "counts": dict(sorted(counts.items())), "multi_call": sorted(multi, key=lambda m: (m["repo"], m["file"], m["line"]))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    res = census()
    if a.check:
        stored = json.loads(OUT.read_text(encoding="utf-8"))
        ok = stored == res
        print("F03 evidence", "reproduces" if ok else "DIFFERS from a fresh census")
        return 0 if ok else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{res['pool_candidates']} pool candidates; {len(res['multi_call'])} multi-call statements -> "
          f"{OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
