"""Evaluate external tools and pqscan arms on a set of labelled sites.

    python -m pqscan.bench.run --sites <sites.csv> --repos <dir with one folder per repo>
           [--tool NAME=<dir with NAME_<repo>.* outputs> ...] --out <dir>

Writes `judgments.csv` (one row per site x method, all dimensions kept separate) and `summary.md`.
"""
from __future__ import annotations
import argparse, collections, csv
from pathlib import Path
from ..baselines.adapters import ADAPTERS, findings_in_window
from ..baselines.simple import ARMS as SIMPLE_ARMS, decide
from ..semantic.evidence import analyze_source
from .judge import combine_texts, judge, dropin_wording, expected_class, strict_judgment
from .stats import wilson
from .fileprobe import file_condition
import json, re

TOOL_FILES = {"pqcheck": "pqcheck_policy_{repo}.sarif", "pqc-audit": "pqcaudit_{repo}.cbom.json", "PostQuant": "postquant_{repo}.json",
              "qsafe": "qsafe_{repo}.json", "QSA-regex": "qsa_{repo}.json", "pqblocks-scan": "pqblocks_{repo}.sarif"}


def load_sites(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(open(path, encoding="utf-8")))


MANIFEST = Path(__file__).resolve().parents[2] / "benchmark" / "baselines_manifest.json"


def failure_profile(tool: str) -> dict:
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))["tools"][tool].get("file_failure_profile") or {}
    except (OSError, KeyError, ValueError):
        return {}


def logged_failures(raw_dir: Path, tool: str, repo: str) -> list[str]:
    """Files a tool itself reported as failed in its run log (normalised to forward slashes)."""
    prof = failure_profile(tool)
    pattern = prof.get("error_log")
    log = raw_dir / (TOOL_FILES[tool].split("{repo}")[0] + f"{repo}.log")
    if not pattern or not log.exists():
        return []
    rx = re.compile(pattern, re.M)
    return [m.group("path").replace("\\", "/") for m in rx.finditer(log.read_text(encoding="utf-8", errors="replace"))]


def judge_external(sites: list[dict], raw_dir: Path, tool: str, repos_dir: Path | None = None) -> list[dict]:
    """Judge one external tool. Silence on a file the tool is known to fail on (its measured failure
    profile, applied to the file's condition, or its own error log) is EXECUTION_FAILURE, never MISSED."""
    rows = []
    cache: dict[str, list] = {}
    prof = failure_profile(tool)
    for s in sites:
        f = raw_dir / TOOL_FILES[tool].format(repo=s["repo"])
        cond = file_condition(repos_dir / s["repo"] / s["file"]) if repos_dir else "unknown"
        if not f.exists():
            why = f"no report for {s['repo']}"
            if cond in prof.get("whole_run_fails_on", []):
                why += f" (the tool aborts its whole run on {cond} files)"
            rows.append(_row(s, tool, "EXECUTION_FAILURE", "NONE", "", why)); continue
        if str(f) not in cache:
            cache[str(f)] = ADAPTERS[tool](f)
        hits = findings_in_window(cache[str(f)], s["file"], int(s["line_start"]), int(s["line_end"]))
        if not hits:
            failed = logged_failures(raw_dir, tool, s["repo"])
            if any(x == s["file"] or x.endswith("/" + s["file"]) for x in failed):
                rows.append(_row(s, tool, "EXECUTION_FAILURE", "NONE", "", "file listed as failed in the tool's log")); continue
            if cond in prof.get("silently_skips", []):
                rows.append(_row(s, tool, "EXECUTION_FAILURE", "NONE", "", f"tool silently skips {cond} files")); continue
        action, rec_class = combine_texts([h.text for h in hits])
        text = " || ".join(sorted({f"{h.rule}: {h.text[:90]}" for h in hits}))
        rows.append(_row(s, tool, action, rec_class, "", text,
                         dropin=bool(hits) and expected_class(s) == "KEM" and rec_class == "KEM" and any(dropin_wording(h.text) for h in hits)))
    return rows


def judge_ours(sites: list[dict], repos_dir: Path, arms=SIMPLE_ARMS) -> list[dict]:
    rows = []
    cache: dict[str, list] = {}
    for s in sites:
        path = repos_dir / s["repo"] / s["file"]
        if str(path) not in cache:
            try:
                cache[str(path)] = analyze_source(s["file"], path.read_text(encoding="utf-8", errors="replace"))
            except OSError as e:
                cache[str(path)] = e
        evs = cache[str(path)]
        for arm in arms:
            if isinstance(evs, Exception):
                rows.append(_row(s, f"pqscan:{arm}", "EXECUTION_FAILURE", "NONE", "", "file could not be read")); continue
            if any(e.site_kind == "parse-error" for e in evs):
                # data_dictionary Sec. 2: an execution failure is never counted as MISSED
                rows.append(_row(s, f"pqscan:{arm}", "EXECUTION_FAILURE", "NONE", "", "file could not be parsed")); continue
            hits = [e for e in evs if int(s["line_start"]) <= e.candidate.location.line <= int(s["line_end"])
                    and e.site_kind in ("operation", "key-material")]
            if not hits:
                rows.append(_row(s, f"pqscan:{arm}", "NO_FINDING", "NONE", "", "")); continue
            hit = _best_hit(hits, s)
            action, rec_class, tier, text = decide(hit, arm)
            rows.append(_row(s, f"pqscan:{arm}", action, rec_class, tier, "",
                             dropin=expected_class(s) == "KEM" and rec_class == "KEM" and dropin_wording(text)))
    return rows


def _best_hit(hits: list, site: dict):
    """Several analysed sites on the labelled line(s): prefer the one whose operation or API matches the
    labelled method, then the earliest column. The choice is recorded by the caller's row, not guessed."""
    method = (site.get("method") or "").strip()
    if method:
        for h in sorted(hits, key=lambda e: e.candidate.location.col):
            if h.operation == method or h.candidate.api.endswith("." + method) or h.candidate.api == method:
                return h
    return sorted(hits, key=lambda e: e.candidate.location.col)[0]


def _row(s: dict, method: str, action: str, rec_class: str, tier: str, text: str, dropin: bool = False) -> dict:
    j = judge(s, action, rec_class)
    js = strict_judgment(j, dropin)
    return {"site_id": s["site_id"], "repo": s["repo"], "method": method, "gt_role": s["gt_role"], "assessability": s["assessability"],
            "eligible": s["eligible"], "hybrid_component": s.get("hybrid_component", ""), "expected_class": expected_class(s),
            "tool_action": action, "rec_class": rec_class, "tier": tier, "judgment": j.judgment, "harm_category": j.harm,
            "judgment_strict": js.judgment, "harm_category_strict": js.harm,
            "dropin_wording": dropin, "tool_text": text}


def summarise(rows: list[dict]) -> str:
    methods = list(dict.fromkeys(r["method"] for r in rows))
    lines = ["Rates use n_exec (eligible sites where the method ran); execution failures are excluded from every rate and reported separately.", "",
             "| Method | n | Exec. failure | n_exec | Correct | Harmful | Undecided | Unjustified | Abstained/unassessable | Detected only | Missed | Coverage | Harmful rate (95% CI) | Drop-in wording | Harmful, strict scoring |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in methods:
        r = [x for x in rows if x["method"] == m and str(x["eligible"]).lower() in ("yes", "true")]
        c = collections.Counter(x["judgment"] for x in r)
        n = len(r)
        n_exec = n - c["EXECUTION_FAILURE"]
        cov = sum(x["tool_action"] == "RECOMMEND" for x in r)
        lo, hi = wilson(c["INCORRECT"], n_exec) if n_exec else (float("nan"), float("nan"))
        lines.append(f"| {m} | {n} | {c['EXECUTION_FAILURE']} | {n_exec} | {c['CORRECT']} | {c['INCORRECT']} | {c['UNDECIDED']} | {c['UNJUSTIFIED']} | "
                     f"{c['UNASSESSABLE']} | {c['DETECTED_ONLY']} | {c['MISSED']} | {cov}/{n_exec} | "
                     f"{c['INCORRECT']}/{n_exec} ({lo:.2f}–{hi:.2f}) | {sum(bool(x['dropin_wording']) for x in r)} | "
                     f"{sum(x['judgment_strict'] == 'INCORRECT' for x in r)}/{n_exec} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pqscan-bench")
    ap.add_argument("--sites", type=Path, required=True)
    ap.add_argument("--repos", type=Path, help="directory containing one folder per repository (for pqscan arms)")
    ap.add_argument("--tool-outputs", type=Path, help="directory with raw outputs of external tools")
    ap.add_argument("--tools", default=",".join(TOOL_FILES), help="comma-separated external tools to judge")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    sites = load_sites(a.sites)
    rows: list[dict] = []
    if a.tool_outputs:
        for t in [x for x in a.tools.split(",") if x]:
            rows += judge_external(sites, a.tool_outputs, t, a.repos)
    if a.repos:
        rows += judge_ours(sites, a.repos)
    a.out.mkdir(parents=True, exist_ok=True)
    with open(a.out / "judgments.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    (a.out / "summary.md").write_text(summarise(rows) + "\n", encoding="utf-8")
    print(summarise(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
