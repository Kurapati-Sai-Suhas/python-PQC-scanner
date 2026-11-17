#!/usr/bin/env bash
# Final demonstration: fresh-environment rebuild + real-code scan (docs/final/final_project_demo.md).
#
#   bash docs/final/demo/run_final_demo.sh <work-dir>      # run from the repository root (Git Bash or Linux)
#
# 1. Builds a NEW venv in <work-dir>/venv from `git archive HEAD` (not the working tree) and installs pqscan with
#    its pinned dependencies (Semgrep 1.185.0).
# 2. Re-runs the seven lecturer-demo commands on docs/demo/demo_repo into <work-dir>/out_synth and compares
#    each output byte-for-byte with the committed docs/demo/outputs.
# 3. Copies the .py files of the INSTALLED cryptography and pycryptodome packages from <source-python>'s
#    site-packages (default: the project venv) into <work-dir>/real. Nothing is downloaded. Neither package is a
#    benchmark repository. It then scans each one to summary, JSON, CycloneDX 1.6 CBOM (twice, for
#    determinism) and SARIF in <work-dir>/out_real.
# Benchmark repositories (development, validation, test) are never touched. Nothing here writes to runs/ or benchmark/.
# The recorded run (docs/final/demo/RUN_LOG.md) used these steps with absolute scratch paths.
set -u
W=$(mkdir -p "$1" && cd "$1" && pwd); R=$(pwd); SRCPY=${2:-$R/.venv/Scripts/python}
[ -x "$SRCPY" ] || SRCPY=$R/.venv/bin/python
mkdir -p "$W/snap" "$W/out_synth" "$W/out_real" "$W/real"; T=$W/transcript.txt; : > "$T"
log(){ echo "### $(date -u +%FT%TZ) $*" >> "$T"; }
run(){ log "$*"; local t0=$(date +%s); "$@" >> "$T" 2>&1; echo "### exit=$? wall=$(( $(date +%s)-t0 ))s" >> "$T"; }

git rev-parse HEAD > "$W/head.txt"
git archive HEAD pqscan pyproject.toml README.md | tar -x -C "$W/snap"
"$SRCPY" -I - "$W/real" <<'EOF'
import hashlib, json, shutil, site, sys, sysconfig
from pathlib import Path
dst = Path(sys.argv[1]); sp = Path(sysconfig.get_paths()["purelib"])
man = {}
for pkg, dist in (("cryptography", "cryptography"), ("Crypto", "pycryptodome")):
    from importlib.metadata import version
    name = f"{dist}-{version(dist)}"; files = sorted((sp / pkg).rglob("*.py")); h = hashlib.sha256()
    for p in files:
        rel = p.relative_to(sp); q = dst / name / rel; q.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, q)
        h.update(rel.as_posix().encode() + b"\0" + p.read_bytes().replace(b"\r\n", b"\n"))
    man[name] = {"py_files": len(files), "tree_sha256": h.hexdigest()}
(dst / "source_manifest.json").write_text(json.dumps(man, indent=1)); print(man)
EOF

PY=${PYTHON312:-py -3.12}
run $PY -m venv "$W/venv"
V=$W/venv/Scripts; [ -d "$V" ] || V=$W/venv/bin
run "$V/python" -m pip install --upgrade pip -q
run "$V/python" -m pip install -q "$W/snap"
run "$V/python" --version; run "$V/pqscan" --version; run "$V/semgrep" --version
run "$V/python" -I -c "import pqscan; print(pqscan.__file__)"
run "$V/python" -m pip freeze
export PYTHONIOENCODING=utf-8

# 2. lecturer-demo reproduction
log "pqscan scan docs/demo/demo_repo";  "$V/pqscan" scan docs/demo/demo_repo > "$W/out_synth/01_summary.txt" 2>>"$T"; echo "### exit=$?" >> "$T"
run "$V/pqscan" scan docs/demo/demo_repo --format json  -o "$W/out_synth/02_scan.json"
run "$V/pqscan" scan docs/demo/demo_repo --format cbom  -o "$W/out_synth/03_cbom.json"
run "$V/pqscan" scan docs/demo/demo_repo --format sarif -o "$W/out_synth/04_scan.sarif"
log "T3";          "$V/pqscan" scan docs/demo/demo_repo --tier-threshold T3 > "$W/out_synth/05_summary_threshold_T3.txt" 2>>"$T"; echo "### exit=$?" >> "$T"
log "method-only"; "$V/pqscan" scan docs/demo/demo_repo --arm method-only  > "$W/out_synth/06_summary_arm_method-only.txt" 2>>"$T"; echo "### exit=$?" >> "$T"
log "no-semgrep";  "$V/pqscan" scan docs/demo/demo_repo --no-semgrep       > "$W/out_synth/07_summary_no-semgrep.txt" 2>>"$T"; echo "### exit=$?" >> "$T"
for f in 01_summary.txt 02_scan.json 03_cbom.json 04_scan.sarif 05_summary_threshold_T3.txt 06_summary_arm_method-only.txt 07_summary_no-semgrep.txt; do
  cmp -s "docs/demo/outputs/$f" "$W/out_synth/$f" && echo "IDENTICAL $f" || echo "DIFFERENT $f"
done | tee "$W/out_synth/compare.txt"

# 3. real-code demonstration (relative paths in the outputs)
cd "$W/real"
for P in $(ls -d cryptography-* pycryptodome-*); do
  log "summary $P"; t0=$(date +%s); "$V/pqscan" scan "$P" > "$W/out_real/${P}_summary.txt" 2>>"$T"; echo "### exit=$? wall=$(( $(date +%s)-t0 ))s" >> "$T"
  run "$V/pqscan" scan "$P" --format json  -o "$W/out_real/${P}_scan.json"
  run "$V/pqscan" scan "$P" --format cbom  -o "$W/out_real/${P}_cbom.json"
  run "$V/pqscan" scan "$P" --format cbom  -o "$W/out_real/${P}_cbom_run2.json"
  run "$V/pqscan" scan "$P" --format sarif -o "$W/out_real/${P}_scan.sarif"
  cmp -s "$W/out_real/${P}_cbom.json" "$W/out_real/${P}_cbom_run2.json" && echo "CBOM deterministic: $P" | tee -a "$T"
done
log DONE
