"""Generate the blind pilot-label review form from docs/pilot/h1_pilot_sites.csv.

The form lists only the site location (repo, commit, file, lines, API call). The existing labels are
withheld so that the human reviewer labels independently; agreement is computed afterwards with
`pqscan.bench.stats` (Cohen's kappa per field).

Usage: python scripts/make_review_forms.py
"""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "docs/pilot/h1_pilot_sites.csv"
MANIFEST = ROOT / "docs/pilot/pilot_manifest.json"
OUT = ROOT / "docs/review/forms/pilot_label_review_blind.csv"
LOCATION = ["site_id", "repo", "commit", "file", "line_start", "line_end", "api_call"]
REVIEWER = ["eligible", "gt_role", "assessability", "possible_roles", "key_provenance", "hybrid_component",
            "confidence_1to3", "time_seconds", "justification"]


def main() -> None:
    commits = {k: v["commit"] for k, v in json.loads(MANIFEST.read_text(encoding="utf-8"))["pilot_repositories"].items()}
    with SITES.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(LOCATION + REVIEWER)
        for r in rows:
            w.writerow([r["site_id"], r["repo"], commits[r["repo"]], r["file"], r["line_start"], r["line_end"],
                        r["api_call"]] + [""] * len(REVIEWER))
    print(f"wrote {OUT.relative_to(ROOT)} ({len(rows)} sites)")


if __name__ == "__main__":
    main()
