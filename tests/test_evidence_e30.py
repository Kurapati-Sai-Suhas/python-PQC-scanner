"""E30 (statistical calibration) is scoped to the calibration's code closure: changes to annotation tooling that the
calibration does not load must not invalidate it, and any change to a file it does load must."""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("calibration_closure", ROOT / "scripts" / "calibration_closure.py")
CC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CC)

ANNOTATION_TOOLING = ("pqscan/bench/annotate.py", "pqscan/bench/loops.py", "pqscan/bench/review.py",
                      "pqscan/bench/packets.py", "pqscan/bench/ledger.py", "pqscan/bench/labels.py",
                      "pqscan/bench/candidates.py")


def _have(commit: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=ROOT, capture_output=True).returncode == 0


def _ok_inputs():
    blobs = {p: f"blob-{i}" for i, p in enumerate(CC.CLOSURE)}
    return dict(traced=set(CC.CLOSURE), calib=dict(blobs), head=dict(blobs), dirty_paths=set(),
                driver_head="drv", driver_ref="drv", driver_dirty=False)


def _passes(r: dict) -> bool:
    return r["closure_traced"] and r["closure_unchanged"] and r["driver_since_ref"]


def test_runtime_trace_equals_declared_closure():
    assert CC.PROCEDURE in CC.CLOSURE and len(CC.CLOSURE) == 9
    assert CC.trace(ROOT) == set(CC.CLOSURE)


def test_annotation_tooling_is_outside_the_closure():
    assert not set(ANNOTATION_TOOLING) & set(CC.CLOSURE)
    assert not set(ANNOTATION_TOOLING) & CC.trace(ROOT)


def test_change_outside_the_closure_passes():
    i = _ok_inputs()
    i["dirty_paths"] = {"pqscan/bench/annotate.py", "pqscan/bench/loops.py"}     # tooling edited, committed or not
    assert _passes(CC.evaluate(**i))


@pytest.mark.parametrize("path", CC.CLOSURE)
def test_any_committed_change_inside_the_closure_fails(path):
    i = _ok_inputs()
    i["head"][path] = "different"
    r = CC.evaluate(**i)
    assert not r["closure_unchanged"] and any(path in p for p in r["problems"])


def test_uncommitted_change_inside_the_closure_fails():
    i = _ok_inputs()
    i["dirty_paths"] = {CC.PROCEDURE}
    assert not CC.evaluate(**i)["closure_unchanged"]


def test_new_import_or_missing_file_fails_the_trace():
    i = _ok_inputs()
    i["traced"] = set(CC.CLOSURE) | {"pqscan/bench/annotate.py"}            # calibration starts loading tooling
    assert not CC.evaluate(**i)["closure_traced"]
    i["traced"] = set(CC.CLOSURE) - {"pqscan/bench/judge.py"}
    assert not CC.evaluate(**i)["closure_traced"]


def test_empty_or_procedure_free_closure_cannot_pass():
    i = _ok_inputs()
    i.update(traced=set(), calib={}, head={})
    assert not _passes(CC.evaluate(**i, closure=()))
    rest = tuple(p for p in CC.CLOSURE if p != CC.PROCEDURE)
    i = _ok_inputs()
    i["traced"] = set(rest)
    assert not CC.evaluate(**i, closure=rest)["closure_traced"]


def test_driver_change_beyond_reference_fails():
    i = _ok_inputs()
    i["driver_head"] = "changed"
    assert not CC.evaluate(**i)["driver_since_ref"]
    i = _ok_inputs()
    i["driver_dirty"] = True
    assert not CC.evaluate(**i)["driver_since_ref"]
    i = _ok_inputs()
    i.update(driver_head="", driver_ref="")                                   # reference commit not found
    assert not CC.evaluate(**i)["driver_since_ref"]


def test_missing_calibration_blob_fails():
    i = _ok_inputs()
    i["calib"][CC.PROCEDURE] = ""
    assert not CC.evaluate(**i)["closure_unchanged"]


@pytest.mark.skipif(not (_have(CC.CALIBRATION_COMMIT) and _have(CC.DRIVER_REF_COMMIT)),
                    reason="calibration commit not in local history (shallow clone); verify_evidence.py still fails hard")
def test_real_repository_closure_and_driver_unchanged():
    r = CC.status(ROOT)
    assert _passes(r), r["problems"]
