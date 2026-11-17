"""scripts/phase3_acceptance.py must not start a run, or rewrite the committed acceptance report, on --help or an
unknown argument (found 2026-11-17: `--help` re-aggregated the checkpoint cache and rewrote the report's commit
and run-time fields)."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "implementation" / "acceptance" / "statistical_acceptance.json"


def _load():
    spec = importlib.util.spec_from_file_location("phase3_acceptance", ROOT / "scripts" / "phase3_acceptance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("argv,code", [(["--help"], 0), (["-h"], 0), (["--bogus"], 2), (["--quick", "--x"], 2)])
def test_non_run_arguments_exit_without_touching_the_report(argv, code, monkeypatch):
    mod = _load()
    before = REPORT.read_bytes()
    monkeypatch.setattr(mod, "run_checkpointed", lambda *a, **k: pytest.fail("a run was started"))
    with pytest.raises(SystemExit) as e:
        mod.main(argv)
    assert e.value.code == code
    assert REPORT.read_bytes() == before
