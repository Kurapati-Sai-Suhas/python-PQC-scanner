"""Recompute docs/final/demo/outputs/real/real_stats.json from the two committed *_scan.json files (read-only counts).

    .venv/Scripts/python docs/final/demo/make_real_stats.py           # rewrite real_stats.json
    .venv/Scripts/python docs/final/demo/make_real_stats.py --check   # exit 1 if it differs from a fresh computation

Added in revision r5 (19 Nov 2026). The script that produced the original file was not committed; this one was
validated by reproducing the archived pre-r5 file byte-for-byte from the archived pre-r5 outputs.
"""
from __future__ import annotations

import collections
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL = HERE / "outputs" / "real"
C = collections.Counter


def load(path: Path) -> dict:
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def stats(d: dict) -> dict:
    F = d["findings"]
    rec = [f for f in F if f["recommendation"]["action"] == "RECOMMEND"]
    generic = [f for f in F if f["semgrep_rules"] and all(r.startswith("pqscan.common.") for r in f["semgrep_rules"])]
    return {
        "files_scanned": d["files_scanned"], "files_skipped": len(d["files_skipped"]),
        "execution_failures": len(d["execution_failures"]), "semgrep_status": d["semgrep_status"],
        "semgrep_errors": d["semgrep_errors"] if isinstance(d["semgrep_errors"], int) else len(d["semgrep_errors"]),
        "sites": len(F), "unique_files": len({f["evidence"]["location"]["file"] for f in F}),
        "excluded": len(d["excluded"]), "semgrep_only": len(d["semgrep_only"]), "unsupported": len(d["unsupported"]),
        "sites_with_semgrep_rule": sum(1 for f in F if f["semgrep_rules"]),
        "sites_semantic_only": sum(1 for f in F if not f["semgrep_rules"]),
        "sites_only_generic_semgrep_rule": len(generic),
        "action": dict(C(f["recommendation"]["action"] for f in F)),
        "target_class": dict(C(f["recommendation"]["target_class"] for f in F)),
        "role": dict(C(f["decision"]["role"] for f in F)),
        "tier": dict(C(f["decision"]["tier"] for f in F)),
        "algorithm": dict(C(f["decision"]["algorithm"] for f in F)),
        "receiver_library": dict(C((f["evidence"].get("receiver") or {}).get("library") or "unresolved" for f in F)),
        "site_kind": dict(C(f["evidence"]["kind"] for f in F)),
        "scope": dict(C(f["scope"] for f in F)),
        "role_x_class": dict(C(f'{f["decision"]["role"]}->{f["recommendation"]["target_class"]}' for f in F)),
        "tier_x_action": dict(C(f'{f["decision"]["tier"]}:{f["recommendation"]["action"]}' for f in F)),
        "abstain_reason": dict(C(f["recommendation"].get("abstain_reason") for f in F
                                 if f["recommendation"]["action"] == "ABSTAIN")),
        "excluded_kind": dict(C(e.get("kind") for e in d["excluded"])),
        "recommend_by_scope": dict(C(f["scope"] for f in rec)),
        "recommend_in_selftest": sum(1 for f in rec if "SelfTest" in f["evidence"]["location"]["file"]),
    }


def build(real: Path = REAL) -> str:
    out = {}
    for name in ("cryptography-47.0.0", "pycryptodome-4.4.0"):
        p = real / f"{name}_scan.json"
        out[name] = stats(load(p if p.exists() else p.with_name(p.name + ".gz")))
    return json.dumps(out, indent=1)                       # the original file has no trailing newline


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    real = Path(args[args.index("--real") + 1]) if "--real" in args else REAL
    text = build(real)
    target = real / "real_stats.json"
    if "--check" in args:
        same = target.read_bytes().replace(b"\r\n", b"\n") == text.encode("utf-8")
        print("real_stats.json reproduces" if same else "real_stats.json differs")
        return 0 if same else 1
    target.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
