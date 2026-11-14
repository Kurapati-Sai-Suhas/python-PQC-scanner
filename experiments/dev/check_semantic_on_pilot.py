"""Development check: run Module B on the pilot repositories and print, for every annotated pilot
site, what the semantic layer found (site kind, receiver, provenance, consumer families) next to the
human label. Development repositories only — never run this on the test split.

Usage: python experiments/dev/check_semantic_on_pilot.py <pilot_repos_dir> docs/pilot/h1_pilot_sites.csv [out.csv]
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
from pqscan.semantic.evidence import analyze_source

repos_dir, sites_csv = Path(sys.argv[1]), Path(sys.argv[2])
out_csv = Path(sys.argv[3]) if len(sys.argv) > 3 else None
sites = list(csv.DictReader(open(sites_csv, encoding="utf-8")))
cache: dict[str, list] = {}
rows = []
for s in sites:
    path = repos_dir / s["repo"] / s["file"]
    key = str(path)
    if key not in cache:
        cache[key] = analyze_source(s["file"], path.read_text(encoding="utf-8", errors="replace"))
    lo, hi = int(s["line_start"]), int(s["line_end"])
    hits = [e for e in cache[key] if lo <= e.candidate.location.line <= hi and e.site_kind in ("operation", "key-material", "not-public-key")]
    if not hits:
        rows.append({"site_id": s["site_id"], "gt_role": s["gt_role"], "found": "NO", "kind": "", "op": "", "alg": "", "private": "",
                     "provenances": "", "families": "", "escapes": "", "notes": ""})
        continue
    e = hits[0]
    rows.append({"site_id": s["site_id"], "gt_role": s["gt_role"], "found": "yes", "kind": e.site_kind, "op": e.operation or "",
                 "alg": e.receiver.algorithm, "private": e.receiver.private,
                 "provenances": "|".join(p.value for p in e.receiver.provenances),
                 "families": "|".join(sorted(e.consumers.families)), "escapes": e.consumers.escapes,
                 "notes": "; ".join(e.consumers.escape_notes)[:90]})
w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
w.writeheader(); w.writerows(rows)
if out_csv:
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w2 = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w2.writeheader(); w2.writerows(rows)
