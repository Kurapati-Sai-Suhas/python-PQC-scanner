"""Descriptive side-by-side of every method on the SYNTHETIC lecturer-demo fixture (no labels, no scoring).

    .venv/Scripts/python -m pqscan.bench.batch --tools-dir .cache/baselines --repos-dir <dir containing demo_repo/> \
        --out <out> --pqscan-arms "full,method+args+recv,method+args,method-only"
    .venv/Scripts/python docs/final/demo/baselines/side_by_side.py <out> <dir containing demo_repo/>

For each site that pqscan's full arm reports, it shows:
- pqscan's role, tier and decision under each arm (from the batch outputs);
- the two simple algorithm-name mappings B1-algorithm and B1-dual (pqscan/baselines/simple.py `decide`, on the same
  evidence);
- each pinned external tool's action and target class, using the benchmark harness's own adapters and
  `combine_texts` on findings at that line.

The fixture has no human labels, so nothing is judged correct or incorrect. The table shows what each method SAYS.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from pqscan.baselines.adapters import ADAPTERS, findings_in_window  # noqa: E402
from pqscan.baselines.simple import decide  # noqa: E402
from pqscan.bench.judge import combine_texts  # noqa: E402
from pqscan.bench.run import TOOL_FILES  # noqa: E402
from pqscan.semantic.evidence import analyze_source  # noqa: E402

out, repos = Path(sys.argv[1]), Path(sys.argv[2])
REPO = "demo_repo"
ARMS = ["full", "method+args+recv", "method+args", "method-only"]
TOOLS = ["pqcheck", "pqc-audit", "PostQuant", "qsafe", "QSA-regex", "pqblocks-scan"]


def arm_findings(arm: str) -> dict:
    d = json.loads((out / f"pqscan_{arm}_{REPO}.json").read_text(encoding="utf-8"))
    res = {}
    for f in d["findings"]:
        loc = f["evidence"]["location"]
        key = (Path(loc["file"]).name, loc["line"])
        res[key] = (f["decision"]["role"], f["decision"]["tier"], f["recommendation"]["action"], f["recommendation"]["target_class"])
    return res, d.get("tier_threshold")


arms = {a: arm_findings(a) for a in ARMS}
full, thr = arms["full"]
tool_findings = {}
for t in TOOLS:
    p = out / TOOL_FILES[t].format(repo=REPO)
    tool_findings[t] = ADAPTERS[t](p) if p.exists() else None
ev_cache = {}

rows = []
for (fname, line), (role, tier, action, cls) in sorted(full.items()):
    path = repos / REPO / fname
    if fname not in ev_cache:
        ev_cache[fname] = analyze_source(fname, path.read_text(encoding="utf-8"))
    evs = [e for e in ev_cache[fname] if e.candidate.location.line == line and e.site_kind in ("operation", "key-material")]
    b1 = {}
    for arm in ("B1-algorithm", "B1-dual"):
        b1[arm] = decide(evs[0], arm)[1] if evs else "—"
    row = {"site": f"{fname}:{line}", "pqscan role (full)": role,
           **{f"pqscan {a}": (lambda v: f"{v[2]} {v[3]} ({v[1]})" if v else "no finding")(arms[a][0].get((fname, line))) for a in ARMS},
           "B1-algorithm": b1["B1-algorithm"], "B1-dual": b1["B1-dual"]}
    for t in TOOLS:
        if tool_findings[t] is None:
            row[t] = "no report"
            continue
        hits = findings_in_window(tool_findings[t], fname, line, line)
        act, rc = combine_texts([h.text for h in hits])
        row[t] = "—" if act == "NO_FINDING" else (rc if act == "RECOMMEND" else "flag only")
    rows.append(row)

cols = list(rows[0])
print(f"Threshold of the pqscan arms in this run: {thr}. Cells for external tools and B1: the recommended class "
      f"(SIG = signature family, KEM = KEM family, DUAL = both offered, PQC_ALREADY, 'flag only' = finding without a "
      f"target, '—' = no finding at that line).\n")
print("| " + " | ".join(cols) + " |")
print("|" + "---|" * len(cols))
for r in rows:
    print("| " + " | ".join(str(r[c]) for c in cols) + " |")
summary = {t: sum(1 for r in rows if r[t] not in ("—", "no report")) for t in TOOLS}
print("\nSites (of %d) at which each external tool reported anything: %s" % (len(rows), json.dumps(summary)))
