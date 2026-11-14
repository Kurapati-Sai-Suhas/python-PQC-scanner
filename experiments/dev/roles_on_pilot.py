"""Development check for Module C: predicted role and tier per ablation arm on the annotated pilot
sites. Development repositories only (paramiko, python-jose); the numbers are NOT evidence of
final performance and must never be reported as results.

Usage: python experiments/dev/roles_on_pilot.py <pilot_repos_dir> docs/pilot/h1_pilot_sites.csv <out.csv> <out.md>
"""
from __future__ import annotations
import collections, csv, sys
from pathlib import Path
from pqscan.roles import classify, ARMS
from pqscan.semantic.evidence import analyze_source

repos_dir, sites_csv, out_csv, out_md = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
sites = [s for s in csv.DictReader(open(sites_csv, encoding="utf-8")) if s["eligible"] == "yes"]
cache: dict[str, list] = {}
rows = []
for s in sites:
    path = repos_dir / s["repo"] / s["file"]
    if str(path) not in cache:
        cache[str(path)] = analyze_source(s["file"], path.read_text(encoding="utf-8", errors="replace"))
    lo, hi = int(s["line_start"]), int(s["line_end"])
    hits = [e for e in cache[str(path)] if lo <= e.candidate.location.line <= hi and e.site_kind in ("operation", "key-material")]
    row = {"site_id": s["site_id"], "gt_role": s["gt_role"], "assessability": s["assessability"]}
    for arm in ARMS:
        if not hits:
            row[f"{arm}:role"], row[f"{arm}:tier"] = "NO_SITE", ""
            continue
        d = classify(hits[0], arm)
        row[f"{arm}:role"], row[f"{arm}:tier"] = (d.role.value if d.role else "EXCLUDED"), d.tier.value
    rows.append(row)

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

lines = ["# Module C on the pilot sites (development data — not a result)", "",
         "Exact-role agreement with the human label, per arm (UNKNOWN agrees with an UNKNOWN label).", "",
         "| Arm | Exact role match | Role predicted UNKNOWN | Tier counts |", "|---|---|---|---|"]
for arm in ARMS:
    match = sum(r[f"{arm}:role"] == r["gt_role"] for r in rows)
    unk = sum(r[f"{arm}:role"] == "UNKNOWN" for r in rows)
    tiers = collections.Counter(r[f"{arm}:tier"] for r in rows)
    lines.append(f"| {arm} | {match}/{len(rows)} | {unk} | " + ", ".join(f"{k}={v}" for k, v in sorted(tiers.items())) + " |")
lines += ["", "| Site | Label | " + " | ".join(ARMS) + " |", "|---|---|" + "---|" * len(ARMS)]
for r in rows:
    lines.append(f"| {r['site_id']} | {r['gt_role']} | " + " | ".join(f"{r[a + ':role']} ({r[a + ':tier']})" for a in ARMS) + " |")
out_md.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
