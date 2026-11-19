"""Experiment E command (protocol Sec. 6; F1 item 8). Thin wrapper around pqscan.bench.experiment_e.

    python scripts/run_experiment_e.py --split development --rows rows.jsonl --finals finals.jsonl \
        [--ai ai.jsonl] [--out result.json]

Order after the gates (never before):
  1. F1 freeze (docs/freeze/pretest_freeze.json, tag phase3-pretest-freeze), owner approval required;
  2. the frozen batch runner executes every method once on the test split (sealed outputs);
  3. annotation of the test split and F2 (docs/freeze/label_freeze.json, tag phase3-label-freeze);
  4. this command with --split test.
The driver refuses --split test while either freeze record or tag is missing, and asserts exactly the seven test
repositories (TA17). It reads judged rows and owner-final label records; it never writes labels.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pqscan.bench import experiment_e as E  # noqa: E402


def _jl(p: str | None) -> list[dict]:
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines() if x.strip()] if p else []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--split", required=True, choices=E.ALLOWED_SPLITS)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--finals", required=True)
    ap.add_argument("--ai")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        E.check_gate(a.split)
    except E.GateError as e:
        print("REFUSED:", e, file=sys.stderr)
        return 2
    res = E.analyse(split=a.split, rows=_jl(a.rows), finals=_jl(a.finals), ai_records=_jl(a.ai))
    text = json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8", newline="\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
