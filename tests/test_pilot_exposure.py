"""Owner decision (pilot exposure): the 5 pilot sites shown as worked examples in annotation guide Sec. 7 form a
separately reported subset; the remaining 26 pilot sites stay distinguishable. Locations only; no label is read."""
from __future__ import annotations

import re
from pathlib import Path

from pqscan.bench import loops as LP

ROOT = Path(__file__).resolve().parents[1]


def _guide_examples() -> set[tuple[str, str, int]]:
    g = (ROOT / "docs" / "benchmark" / "annotation_guide.md").read_text(encoding="utf-8")
    start = g.index("## 7. Worked examples")
    sec = g[start:g.index("\n## ", start + 5)]
    return {(r, Path(f).name, int(n)) for r, f, n in re.findall(r"\*\*(\S+) `([\w/.]+\.py):(\d+)`\*\*", sec)}


def test_pinned_subset_matches_the_guide_worked_examples():
    assert _guide_examples() == set(LP.GUIDE_EXPOSED_PILOT) and len(LP.GUIDE_EXPOSED_PILOT) == 5


def test_five_exposed_and_twenty_six_distinguishable():
    exposed = {r: LP.guide_exposed("pilot", r, ROOT) for r in LP.PILOT_REPOS}
    total = {r: {i["candidate_id"] for i in LP.items("pilot", r, ROOT)} for r in LP.PILOT_REPOS}
    assert {r: len(v) for r, v in exposed.items()} == {"paramiko": 3, "python-jose": 2}
    assert all(exposed[r] <= total[r] for r in LP.PILOT_REPOS)
    assert sum(len(total[r] - exposed[r]) for r in LP.PILOT_REPOS) == 26
    assert LP.guide_exposed("synthetic", "synthetic", ROOT) == set()
