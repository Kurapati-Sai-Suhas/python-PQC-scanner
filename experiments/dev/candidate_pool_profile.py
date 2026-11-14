"""Profile the annotation candidate pool on DEVELOPMENT repositories only (planning aid for decision D2).

    python experiments/dev/candidate_pool_profile.py <dev_repos_dir> <run_dir> <out_md>

For each development repository it builds the candidate pool described in docs/benchmark/repository_split.md
Sec. 3 (union of the regex over-approximation, every baseline's findings and pqscan Module A / Semgrep),
deduplicated by (file, line), and reports its size, how many candidates come only from the tool-independent
regex (that is, sites every evaluated tool missed), the library and test-path mix, and how many of the 31
pilot sites the regex and the tool union each cover. It reads no test-split repository and computes no
correctness figure. The regex is the one used for repository qualification (experiments/bench/verify_candidates.py).
"""
from __future__ import annotations
import csv, json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pqscan.baselines.adapters import ADAPTERS  # noqa: E402
from pqscan.bench.run import TOOL_FILES  # noqa: E402

sys.path.insert(0, str(ROOT / "experiments" / "bench"))
from verify_candidates import PYCA, PYCRYPTODOME, REGEX  # noqa: E402

TEST_PATH = re.compile(r"(^|/)(tests?|testing)(/|$)|(^|/)test_[^/]*\.py$|_test\.py$")
PILOT_REPO = {"paramiko__paramiko": "paramiko", "mpdavis__python-jose": "python-jose"}


def regex_candidates(repo: Path) -> tuple[set[tuple[str, int]], dict[str, str]]:
    cands, lib = set(), {}
    for p in sorted(repo.rglob("*.py")):
        if ".git" in p.parts:
            continue
        rel = p.relative_to(repo).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        pyca, pcd = bool(PYCA.search(text)), bool(PYCRYPTODOME.search(text))
        lib[rel] = "both" if pyca and pcd else "pyca" if pyca else "pycryptodome" if pcd else "none"
        if not (pyca or pcd):
            continue                                   # same restriction as qualification: crypto-importing files
        for i, line in enumerate(text.splitlines(), 1):
            if REGEX.search(line):
                cands.add((rel, i))
    return cands, lib


def tool_candidates(repo: Path, run_dir: Path, name: str) -> set[tuple[str, int]]:
    root = repo.resolve().as_posix().rstrip("/") + "/"
    out = set()
    for tool, pattern in TOOL_FILES.items():
        f = run_dir / pattern.format(repo=name)
        if f.exists():
            for x in ADAPTERS[tool](f):
                path = x.file.replace("\\", "/")
                path = path[len(root):] if path.startswith(root) else path.lstrip("./")
                out.add((path, int(x.line)))
    d = json.loads((run_dir / f"pqscan_full_{name}.json").read_text(encoding="utf-8"))
    for f in d["findings"]:
        loc = f["evidence"]["location"]
        out.add((loc["file"], int(loc["line"])))
    for f in d["semgrep_only"]:
        out.add((f["file"], int(f["line"])))
    return out


def main(repos_dir: Path, run_dir: Path, out_md: Path) -> None:
    pilot = list(csv.DictReader(open(ROOT / "docs/pilot/h1_pilot_sites.csv", encoding="utf-8")))
    rows, tot = [], Counter()
    for repo in sorted(p for p in repos_dir.iterdir() if p.is_dir()):
        name = repo.name
        rx, lib = regex_candidates(repo)
        tl = tool_candidates(repo, run_dir, name)
        union = rx | tl
        c = Counter()
        c["union"], c["regex"], c["tools"] = len(union), len(rx), len(tl)
        c["regex_only"], c["tools_only"], c["both"] = len(rx - tl), len(tl - rx), len(rx & tl)
        c["test_path"] = sum(bool(TEST_PATH.search(f)) for f, _ in union)
        for f, _ in union:
            c["lib_" + lib.get(f, "none")] += 1
        if name in PILOT_REPO:
            ps = [s for s in pilot if s["repo"] == PILOT_REPO[name]]
            def hit(cset, s):
                return any(f == s["file"] and int(s["line_start"]) <= ln <= int(s["line_end"]) for f, ln in cset)
            c["pilot_sites"] = len(ps)
            c["pilot_in_regex"] = sum(hit(rx, s) for s in ps)
            c["pilot_in_tools"] = sum(hit(tl, s) for s in ps)
            c["pilot_in_union"] = sum(hit(union, s) for s in ps)
        rows.append((name, c))
        tot.update(c)
    keys = ["union", "regex", "tools", "both", "regex_only", "tools_only", "test_path", "lib_pyca", "lib_pycryptodome", "lib_both", "lib_none"]
    lines = ["# Candidate-pool profile, development repositories only (planning aid for D2)", "",
             "Unit: distinct (file, line) candidates. `regex_only` = candidates no evaluated tool reported; `tools_only` = reported by a tool but not matched by the regex; `lib_*` = crypto library imported by the file. No correctness figure is computed.", "",
             "| Repository | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
    for name, c in rows + [("TOTAL", tot)]:
        lines.append(f"| {name} | " + " | ".join(str(c[k]) for k in keys) + " |")
    lines += ["", "Pilot sites (31; paramiko and python-jose) inside each candidate source:", "",
              f"- regex: {tot['pilot_in_regex']} of {tot['pilot_sites']}", f"- tool union: {tot['pilot_in_tools']} of {tot['pilot_sites']}",
              f"- full union: {tot['pilot_in_union']} of {tot['pilot_sites']}"]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
