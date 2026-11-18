"""The code closure of the pre-F1 statistical calibration (evidence register E30).

The calibration (`scripts/phase3_acceptance.py`, run on commit CALIBRATION_COMMIT) loads exactly the files in CLOSURE.
E30 claims that this closure is byte-identical today, not that all of `pqscan/` is: annotation tooling in the same
package (`pqscan/bench/annotate.py`, `loops.py`, ...) is not loaded by the calibration and may change.

Three checks, all of which must hold:
  closure_traced     a fresh interpreter that imports the driver loads exactly CLOSURE (repository files only),
                     so a new import that pulls in another file fails here;
  closure_unchanged  every CLOSURE file is identical at CALIBRATION_COMMIT and at HEAD, and has no uncommitted change;
  driver_since_ref   the driver at HEAD is identical to DRIVER_REF_COMMIT (its only change after the calibration
                     commit is command-line handling: --help or an unknown argument stops before any computation),
                     and has no uncommitted change.

    python scripts/calibration_closure.py      # prints the three results; exit 1 if any fails
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_COMMIT = "aa9d6b00697f8f480c1c4be1b62cd3588731b685"
DRIVER = "scripts/phase3_acceptance.py"
DRIVER_REF_COMMIT = "5d78a06"
CLOSURE = (
    "pqscan/__init__.py",
    "pqscan/bench/__init__.py",
    "pqscan/bench/h2.py",          # the procedure under test
    "pqscan/bench/stats.py",
    "pqscan/bench/judge.py",
    "docs/proposals/v1.0.4/rev4/scripts/calib_matching_v4.py",   # planning-model simulator (archived)
    "docs/proposals/v1.0.4/rev4/scripts/calib_nearkink_v4.py",
    "docs/proposals/v1.0.4/rev4/scripts/sim_family_v12pp.py",
    "docs/proposals/v1.0.4/rev4/scripts/matching_ref_v4.py",
)
PROCEDURE = "pqscan/bench/h2.py"

_TRACE = r"""
import importlib.util, json, pathlib, sys
root = pathlib.Path(sys.argv[1]).resolve()
driver = (root / sys.argv[2]).resolve()
before = set(sys.modules)
spec = importlib.util.spec_from_file_location("_calibration_driver_trace", driver)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
out = set()
for name, m in list(sys.modules.items()):
    f = getattr(m, "__file__", None)
    if name in before or not f:
        continue
    p = pathlib.Path(f).resolve()
    try:
        rel = p.relative_to(root)
    except ValueError:
        continue
    if rel.parts and rel.parts[0] in (".venv", "venv") or p == driver:
        continue
    out.add(rel.as_posix())
print(json.dumps(sorted(out)))
"""


def trace(root: Path = ROOT) -> set[str]:
    """Repository files loaded by importing the driver in a fresh interpreter (the driver itself excluded)."""
    r = subprocess.run([sys.executable, "-c", _TRACE, str(root), DRIVER], capture_output=True, text=True, cwd=root)
    if r.returncode != 0:
        raise RuntimeError(f"closure trace failed: {r.stderr.strip()[-500:]}")
    return set(json.loads(r.stdout.strip().splitlines()[-1]))


def _git(root: Path, *a: str) -> str:
    return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout.strip()


def blob(root: Path, commit: str, path: str) -> str:
    """Git blob id of `path` at `commit`; '' if the commit or the path does not exist."""
    return _git(root, "rev-parse", "--verify", "--quiet", f"{commit}:{path}")


def dirty(root: Path, paths) -> set[str]:
    out = _git(root, "status", "--porcelain", "--", *paths)
    return {line[3:].strip().strip('"') for line in out.splitlines() if line.strip()}


def evaluate(traced: set[str], calib: dict[str, str], head: dict[str, str], dirty_paths: set[str],
             driver_head: str, driver_ref: str, driver_dirty: bool, closure=CLOSURE) -> dict:
    """Pure decision function (unit-tested). Returns the three results and the reasons for any failure."""
    closure = tuple(closure)
    problems = []
    traced_ok = bool(closure) and PROCEDURE in closure and set(traced) == set(closure)
    if not traced_ok:
        problems += [f"loaded but not declared: {p}" for p in sorted(set(traced) - set(closure))]
        problems += [f"declared but not loaded: {p}" for p in sorted(set(closure) - set(traced))]
        if PROCEDURE not in closure:
            problems.append(f"the closure does not contain the procedure under test {PROCEDURE}")
    changed = [p for p in closure if not calib.get(p) or calib.get(p) != head.get(p)]
    unc = sorted(set(closure) & set(dirty_paths))
    problems += [f"changed since the calibration commit: {p}" for p in changed]
    problems += [f"uncommitted change: {p}" for p in unc]
    driver_ok = bool(driver_ref) and driver_head == driver_ref and not driver_dirty
    if not driver_ok:
        problems.append(f"{DRIVER} differs from {DRIVER_REF_COMMIT} or has an uncommitted change")
    return {"closure_traced": traced_ok, "closure_unchanged": bool(closure) and not changed and not unc,
            "driver_since_ref": driver_ok, "problems": problems}


def status(root: Path = ROOT) -> dict:
    return evaluate(
        traced=trace(root),
        calib={p: blob(root, CALIBRATION_COMMIT, p) for p in CLOSURE},
        head={p: blob(root, "HEAD", p) for p in CLOSURE},
        dirty_paths=dirty(root, CLOSURE),
        driver_head=blob(root, "HEAD", DRIVER),
        driver_ref=blob(root, DRIVER_REF_COMMIT, DRIVER),
        driver_dirty=bool(dirty(root, [DRIVER])),
    )


def main() -> int:
    s = status()
    for k in ("closure_traced", "closure_unchanged", "driver_since_ref"):
        print(f"{'OK ' if s[k] else 'BAD'} {k}: {s[k]}")
    for p in s["problems"]:
        print("  ", p)
    return 0 if all(s[k] for k in ("closure_traced", "closure_unchanged", "driver_since_ref")) else 1


if __name__ == "__main__":
    sys.exit(main())
