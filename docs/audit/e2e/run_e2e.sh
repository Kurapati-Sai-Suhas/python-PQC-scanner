#!/usr/bin/env bash
# Fresh-environment end-to-end check of pqscan (docs/audit/software_readiness.md).
#
#   bash docs/audit/e2e/run_e2e.sh <work-dir>          # from the repository root (Git Bash or Linux)
#
# 1. Clones the committed HEAD of this repository into <work-dir>/clone (no working-tree changes leak in).
# 2. Installs exactly as README.md says: `uv venv .venv --python 3.12` + `uv pip install -e ".[bench,dev]"`.
# 3. Runs the full production test suite inside that environment.
# 4. Runs the CLI on: the lecturer-demo fixture and the worked example (compared byte-for-byte with the committed
#    outputs), all export formats (CBOM/SARIF validated with the fresh environment's libraries), a hybrid fixture,
#    a robustness fixture (syntax error, null byte, latin-1, Python 2, out-of-scope libraries, symmetric only),
#    a non-existent path, and two identical CBOM runs (determinism).
# Only synthetic fixtures are scanned. No benchmark repository is touched.
set -u
SRC=$(pwd)
W=$(mkdir -p "$1" && cd "$1" && pwd)
LOG="$W/e2e_transcript.txt"; : > "$LOG"
step(){ echo "### $(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
rc(){ echo "### exit=$1" | tee -a "$LOG"; }
# same <label> <a> <b>: byte-identical, or identical once CRLF/LF line endings are normalised (pqscan writes the
# platform newline; a fresh clone may check committed files out with LF), or different
same(){ if cmp -s "$2" "$3"; then echo "IDENTICAL (byte) $1" | tee -a "$LOG";
        elif cmp -s <(tr -d '\015' < "$2") <(tr -d '\015' < "$3"); then echo "IDENTICAL except line endings $1" | tee -a "$LOG";
        else echo "DIFFERENT $1" | tee -a "$LOG"; fi; }

step "clone committed HEAD"
rm -rf "$W/clone"; git clone -q "$SRC" "$W/clone" >>"$LOG" 2>&1; rc $?
cd "$W/clone"; git rev-parse HEAD | tee -a "$LOG"

step "install per README: uv venv .venv --python 3.12"
uv venv .venv --python 3.12 >>"$LOG" 2>&1; rc $?
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
step "install per README: uv pip install -e .[bench,dev]"
uv pip install --python "$PY" -e ".[bench,dev]" >>"$LOG" 2>&1; rc $?
PQ=.venv/Scripts/pqscan.exe; [ -x "$PQ" ] || PQ=.venv/bin/pqscan     # resolved after install (entry point exists now)
echo "pqscan entry point: $PQ" | tee -a "$LOG"
"$PY" --version >>"$LOG" 2>&1; "$PQ" --version >>"$LOG" 2>&1; .venv/Scripts/semgrep --version >>"$LOG" 2>&1 || .venv/bin/semgrep --version >>"$LOG" 2>&1
export PYTHONIOENCODING=utf-8
OUT="$W/out"; rm -rf "$OUT"; mkdir -p "$OUT"

step "full production test suite in the fresh environment"
"$PY" -m pytest -p no:cacheprovider -o addopts="" -q -rs tests > "$OUT/pytest.txt" 2>&1; rc $?
grep -E "SKIPPED|passed|failed" "$OUT/pytest.txt" | tail -4 | tee -a "$LOG"

step "demo fixture: summary (compare with committed docs/demo/outputs/01_summary.txt)"
"$PQ" scan docs/demo/demo_repo > "$OUT/demo_summary.txt" 2>>"$LOG"; rc $?
same "demo summary vs committed 01_summary.txt" "$OUT/demo_summary.txt" docs/demo/outputs/01_summary.txt
for f in json cbom sarif; do
  step "demo fixture: --format $f"; "$PQ" scan docs/demo/demo_repo --format $f -o "$OUT/demo.$f" >>"$LOG" 2>&1; rc $?
done
"$PQ" scan docs/demo/demo_repo --format cbom -o "$OUT/demo_run2.cbom" >>"$LOG" 2>&1
cmp -s "$OUT/demo.cbom" "$OUT/demo_run2.cbom" && echo "CBOM deterministic (two runs byte-identical)" | tee -a "$LOG" || echo "CBOM NOT deterministic" | tee -a "$LOG"
same "demo CBOM vs committed 03_cbom.json" "$OUT/demo.cbom" docs/demo/outputs/03_cbom.json

step "worked example (compare with committed docs/paper/example/output_summary.txt)"
( cd docs/paper/example && "../../../$PQ" scan . > "$OUT/example_summary.txt" 2>>"$LOG" ); rc $?
same "worked example vs committed output_summary.txt" "$OUT/example_summary.txt" docs/paper/example/output_summary.txt

step "synthetic fixtures"
"$PY" "$SRC/docs/audit/e2e/make_fixtures.py" "$W/fixtures" >>"$LOG" 2>&1; rc $?
step "hybrid fixture"
"$PQ" scan "$W/fixtures/hybrid" > "$OUT/hybrid_summary.txt" 2>>"$LOG"; rc $?
"$PQ" scan "$W/fixtures/hybrid" --format json -o "$OUT/hybrid.json" >>"$LOG" 2>&1
step "robustness fixture"
"$PQ" scan "$W/fixtures/robustness" > "$OUT/robustness_summary.txt" 2>>"$LOG"; rc $?
"$PQ" scan "$W/fixtures/robustness" --format json -o "$OUT/robustness.json" >>"$LOG" 2>&1
"$PQ" scan "$W/fixtures/robustness" --format cbom -o "$OUT/robustness.cbom" >>"$LOG" 2>&1; rc $?
step "non-existent path (expect input error, exit 2)"
"$PQ" scan "$W/does_not_exist" > "$OUT/missing.txt" 2>&1; rc $?

step "schema validation with the fresh environment"
"$PY" - "$OUT" >>"$LOG" 2>&1 <<'EOF'
import json, sys, jsonschema
from pathlib import Path
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator
out = Path(sys.argv[1])
sarif_schema = json.loads(Path("pqscan/export/schemas/sarif-2.1.0.json").read_text(encoding="utf-8"))
for name in ("demo.cbom", "robustness.cbom"):
    err = JsonStrictValidator(SchemaVersion.V1_6).validate_str((out / name).read_text(encoding="utf-8"))
    print(name, "CycloneDX 1.6 strict:", "VALID" if err is None else f"INVALID {err}")
errs = list(jsonschema.Draft4Validator(sarif_schema).iter_errors(json.loads((out / "demo.sarif").read_text(encoding="utf-8"))))
print("demo.sarif SARIF 2.1.0:", "VALID" if not errs else f"INVALID {errs[0].message}")
EOF
rc $?
step DONE
