"""Reconcile a real batch-runner run with the published H1 pilot judgments (development check, not a result).

    python experiments/dev/reconcile_runner_with_pilot.py <run_dir> <repos_dir> <out_md>

The pilot sites (docs/pilot/h1_pilot_sites.csv) are in paramiko 5.1.0 and python-jose 3.5.0 at the same
commits as the development split. The runner names repositories by directory (`paramiko__paramiko`,
`mpdavis__python-jose`), the pilot by short name, so outputs and logs are mapped to the short names in a
temporary directory. Each external tool is then judged with the packaged judge and compared with the
published pilot table (`docs/pilot/h1_pilot_joined.csv`). Run records are summarised for exit status,
time and per-file status.
"""
from __future__ import annotations
import csv, json, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pqscan.bench.run import TOOL_FILES, judge_external  # noqa: E402

NAMES = {"paramiko__paramiko": "paramiko", "mpdavis__python-jose": "python-jose"}
PILOT_TOOLS = ("pqcheck", "pqc-audit", "PostQuant", "qsafe", "QSA-regex")


def main(run_dir: Path, repos_dir: Path, out_md: Path) -> int:
    sites = list(csv.DictReader(open(ROOT / "docs/pilot/h1_pilot_sites.csv", encoding="utf-8")))
    published = {(r["tool"], r["site_id"]): (r["judgment"], r["harm_category"])
                 for r in csv.DictReader(open(ROOT / "docs/pilot/h1_pilot_joined.csv", encoding="utf-8"))}
    lines = ["# Batch runner: first real run, reconciled with the pilot (development check)", "",
             f"Run directory: `{run_dir.as_posix()}`. Not a result: the pilot repositories are development repositories.", "",
             "## Run records", "", "| Method | Repository | Status | Exit | Timed out | Seconds | File status |", "|---|---|---|---|---|---|---|"]
    summary = json.loads((run_dir / "batch_summary.json").read_text(encoding="utf-8"))
    for r in summary["runs"]:
        lines.append(f"| {r['method']} | {r['repo']} | {r['run_status']} | {r['exit_code']} | {r['timed_out']} | {r['elapsed_s']} | {r['file_status_counts']} |")
    lines += ["", f"Not run: {', '.join(summary['not_run'])}.", "", "## Judgments on the 31 pilot sites vs. the published pilot table", "",
              "| Tool | Sites | Same as published | Different | Execution failures |", "|---|---|---|---|---|"]
    diffs_all = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_raw, tmp_repos = Path(tmp) / "raw", Path(tmp) / "repos"
        tmp_raw.mkdir()
        tmp_repos.mkdir()
        for long, short in NAMES.items():
            for f in run_dir.glob(f"*{long}*"):
                shutil.copy(f, tmp_raw / f.name.replace(long, short))
            shutil.copytree(repos_dir / long, tmp_repos / short, ignore=shutil.ignore_patterns(".git"))
        for tool in PILOT_TOOLS + ("pqblocks-scan",):
            rows = judge_external(sites, tmp_raw, tool, tmp_repos)
            got = {r["site_id"]: (r["judgment"], r["harm_category"]) for r in rows}
            if tool in PILOT_TOOLS:
                diffs = {k: (published[(tool, k)], v) for k, v in got.items() if published[(tool, k)] != v}
                diffs_all += [(tool, k, a, b) for k, (a, b) in diffs.items()]
                same = len(got) - len(diffs)
                lines.append(f"| {tool} | {len(got)} | {same} | {len(diffs)} | {sum(v[0] == 'EXECUTION_FAILURE' for v in got.values())} |")
            else:
                lines.append(f"| {tool} (not in the published pilot table) | {len(got)} | n/a | n/a | {sum(v[0] == 'EXECUTION_FAILURE' for v in got.values())} |")
    if diffs_all:
        lines += ["", "Differences (tool, site, published, now):", ""] + [f"- {t} {s}: {a} -> {b}" for t, s, a, b in diffs_all]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if diffs_all else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))
