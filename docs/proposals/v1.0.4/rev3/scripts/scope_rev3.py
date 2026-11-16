"""Proposed scope classifier (rev3) applied to DEVELOPMENT/VALIDATION sources only (never the test split).

Precedence: vendored > test > example > app (a vendored copy of a library's tests is still vendored code;
tests that live under examples/ are tests). PROPOSED; not production code.

    .venv/Scripts/python docs/proposals/v1.0.4/rev3/scripts/scope_rev3.py <project_root>
"""
from __future__ import annotations
import collections, json, re, sys
from pathlib import Path

VENDORED = re.compile(r"(^|/)(vendor|_vendor|third_party)(/|$)")
TEST = re.compile(r"(^|/)(test|tests|testing)(/|$)|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)tests?\.py$|(^|/)tests_[^/]*\.py$|(^|/)tests-[^/]*\.py$|(^|/)conftest\.py$")
EXAMPLE = re.compile(r"(^|/)(examples?|demos?[^/]*)(/|$)")


def classify(rel: str) -> tuple[str, list[str]]:
    hits = [k for k, rx in (("vendored", VENDORED), ("test", TEST), ("example", EXAMPLE)) if rx.search(rel)]
    return (hits[0] if hits else "app"), hits


def main(root: Path) -> None:
    out, multi = collections.Counter(), []
    s1_by_class = collections.Counter()
    for split in ("development", "validation"):
        for repo in sorted((root / ".cache/repos" / split).iterdir()):
            for p in repo.rglob("*.py"):
                if ".git" in p.parts:
                    continue
                rel = p.relative_to(repo).as_posix()
                cls, hits = classify(rel)
                out[(repo.name, cls)] += 1
                if len(hits) > 1:
                    multi.append((repo.name, rel, hits, cls))
            order = json.loads((root / "benchmark/candidates" / split / f"order_{repo.name}.json").read_text(encoding="utf-8"))
            for st in ("S1-app", "S1-test"):
                for c in order["strata"][st]:
                    s1_by_class[(repo.name, classify(c["file"])[0])] += 1
    print("files per (repository, class):", dict(sorted(out.items())))
    print("paths matching more than one class:", len(multi), multi[:10])
    print("current S1 candidates re-classified under the rev3 rule:", dict(sorted(s1_by_class.items())))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
