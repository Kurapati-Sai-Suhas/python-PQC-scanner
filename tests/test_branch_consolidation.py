"""Branch consolidation into main (owner decision, 19 Nov 2026; docs/audit/branch_consolidation.md).

The original main baseline stays pinned exactly by two annotated tags, and the checked-out history contains it, is
merge-free since it, and contains the approved pre-consolidation head: nothing was rewritten or lost. Skipped where a
clone lacks the tags or the history (shallow clones); docs/paper/verify_evidence.py checks the same on `main`."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "81f561e34997dc56b2728241617cd19785210c85"
PRE_CONSOLIDATION_HEAD = "9cc87d518e5051e9224c16b7f5c8bcfabeeca83c"
TAG = "pre-consolidation-main-81f561e"


def git(*a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)


def _have(ref: str) -> bool:
    return git("rev-parse", "--verify", "--quiet", ref).returncode == 0


pytestmark = pytest.mark.skipif(not (_have(f"{TAG}^{{commit}}") and _have(f"{PRE_CONSOLIDATION_HEAD}^{{commit}}")),
                                reason="baseline tag or pre-consolidation history not present in this clone")


def test_baseline_tag_is_annotated_and_exact():
    assert git("cat-file", "-t", f"refs/tags/{TAG}").stdout.strip() == "tag"
    assert git("rev-parse", f"{TAG}^{{commit}}").stdout.strip() == BASELINE
    assert git("rev-list", "-n", "1", "phase2-complete").stdout.strip() == BASELINE


def test_history_contains_baseline_and_approved_head_without_merges():
    assert git("merge-base", "--is-ancestor", BASELINE, "HEAD").returncode == 0
    assert git("merge-base", "--is-ancestor", PRE_CONSOLIDATION_HEAD, "HEAD").returncode == 0
    assert git("rev-list", "--merges", "--count", f"{BASELINE}..HEAD").stdout.strip() == "0"


def test_consolidation_record_names_both_commits_and_the_tag():
    text = (ROOT / "docs" / "audit" / "branch_consolidation.md").read_text(encoding="utf-8")
    assert BASELINE in text and PRE_CONSOLIDATION_HEAD in text and TAG in text
