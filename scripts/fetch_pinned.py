"""Re-create every external input from pinned commits (reproducibility, NFR5).

    python scripts/fetch_pinned.py repos     <dest>   # pilot + benchmark repositories (dev/val ONLY by default)
    python scripts/fetch_pinned.py baselines <dest>   # external scanners, each in its own venv / node build

Test-split repositories are fetched only with --include-test, to keep the held-out set unopened
until the Phase 3 freeze. Nothing fetched is imported or executed by pqscan; baseline tools run
only inside their own environments.
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def clone_at(url: str, commit: str, dest: Path) -> None:
    """Clone `url` and check out exactly `commit` (full or abbreviated SHA)."""
    if not (dest / ".git").exists():
        dest.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "-q"], dest)
        run(["git", "remote", "add", "origin", url], dest)
    try:
        run(["git", "fetch", "-q", "--depth", "1", "origin", commit], dest)
        run(["git", "checkout", "-q", "--detach", "FETCH_HEAD"], dest)
    except subprocess.CalledProcessError:
        # abbreviated SHAs cannot be fetched directly; fall back to a full fetch
        run(["git", "fetch", "-q", "origin"], dest)
        run(["git", "checkout", "-q", "--detach", commit], dest)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dest, text=True).strip()
    if not head.startswith(commit):
        raise SystemExit(f"{url}: HEAD {head} does not match pinned {commit}")
    print(f"   {dest.name} @ {head[:12]}")


def fetch_repos(dest: Path, include_test: bool) -> None:
    pilot = json.loads((PROJECT / "docs/pilot/pilot_manifest.json").read_text(encoding="utf-8"))
    for name, r in pilot["pilot_repositories"].items():
        clone_at(r["url"], r["commit"], dest / name)
    real = json.loads((PROJECT / "benchmark/real/manifest.json").read_text(encoding="utf-8"))
    for split, repos in real["splits"].items():
        if split == "test" and not include_test:
            print(f"skipping {len(repos)} test-split repositories (use --include-test after the Phase 3 freeze)")
            continue
        for r in repos:
            clone_at(r["url"], r["commit"], dest / split / r["repo"].replace("/", "__"))


def fetch_baselines(dest: Path) -> None:
    m = json.loads((PROJECT / "benchmark/baselines_manifest.json").read_text(encoding="utf-8"))
    uv = shutil.which("uv")
    for name, t in m["tools"].items():
        d = dest / name
        clone_at(t["url"], t["commit"], d)
        if t["kind"] == "python":
            if not uv:
                raise SystemExit("uv is required to build baseline environments")
            run([uv, "venv", "-q", "--clear", "--python", "3.12", str(d / ".venv")])
            py = d / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            if t.get("install"):
                run([uv, "pip", "install", "-q", "--python", str(py), *t["install"]], d)
            if t.get("install_packages"):
                run([uv, "pip", "install", "-q", "--python", str(py), *t["install_packages"]], d)
        elif t["kind"] == "node":
            npm = shutil.which("npm") or shutil.which("npm.cmd")
            if not npm:
                raise SystemExit("npm is required to build PostQuant")
            run([npm, "ci", "--ignore-scripts"], d)
            run([npm, "run", "build"], d)
    for k, v in m.get("not_runnable", {}).items():
        print(f"not runnable: {k}: {v}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["repos", "baselines"])
    ap.add_argument("dest", type=Path)
    ap.add_argument("--include-test", action="store_true")
    a = ap.parse_args()
    a.dest = a.dest.resolve()          # tool installs run with cwd=<tool dir>; relative venv paths would break
    a.dest.mkdir(parents=True, exist_ok=True)
    fetch_repos(a.dest, a.include_test) if a.what == "repos" else fetch_baselines(a.dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
