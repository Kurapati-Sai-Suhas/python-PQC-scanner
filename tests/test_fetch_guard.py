"""scripts/fetch_pinned.py refuses --include-test until stage F1 exists (protocol v1.0.4: freeze record committed
and the commit tagged phase3-pretest-freeze before any test-split repository is fetched)."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("fetch_pinned", ROOT / "scripts" / "fetch_pinned.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _repo(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "-c", "user.email=t@example.invalid", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    return tmp_path


def test_blocked_without_freeze_record(tmp_path):
    assert "pretest_freeze.json" in _load().held_out_blocker(_repo(tmp_path))


def test_blocked_with_record_but_no_tag(tmp_path):
    root = _repo(tmp_path)
    (root / "docs" / "freeze").mkdir(parents=True)
    (root / "docs" / "freeze" / "pretest_freeze.json").write_text("{}", encoding="utf-8")
    assert "phase3-pretest-freeze" in _load().held_out_blocker(root)


def test_allowed_with_record_and_tag(tmp_path):
    root = _repo(tmp_path)
    (root / "docs" / "freeze").mkdir(parents=True)
    (root / "docs" / "freeze" / "pretest_freeze.json").write_text("{}", encoding="utf-8")
    _git(root, "tag", "phase3-pretest-freeze")
    assert _load().held_out_blocker(root) is None


def test_this_repository_is_blocked_now():
    # no F1 yet: the guard must refuse in the real checkout
    assert _load().held_out_blocker() is not None


def test_main_refuses_before_any_clone(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setattr(mod, "held_out_blocker", lambda project=None: "stage F1 not complete")
    monkeypatch.setattr(mod, "clone_at", lambda *a, **k: pytest.fail("clone attempted"))
    monkeypatch.setattr(sys, "argv", ["fetch_pinned.py", "repos", str(tmp_path / "dest"), "--include-test"])
    with pytest.raises(SystemExit, match="refusing --include-test"):
        mod.main()
    assert not (tmp_path / "dest").exists()
