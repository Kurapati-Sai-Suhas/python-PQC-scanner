"""One-day dataset audit: every number in docs/audit/one_day_dataset_audit.md comes from this script (read-only).

    .venv/Scripts/python docs/audit/dataset_audit.py            # prints the audit tables as JSON
    .venv/Scripts/python docs/audit/dataset_audit.py --write    # also writes docs/audit/dataset_audit_values.json

Reads only: benchmark/real/manifest.json (metadata of all 13 repositories; no test-repository content),
benchmark/candidates/*/order_*.json, benchmark/synthetic/*, docs/pilot/h1_pilot_sites.csv,
benchmark/baselines_manifest.json, the annotation schemas and the existence of label / ledger / freeze files.
It never opens the git-ignored pool_sources_*.json files (they record which tools found each candidate, i.e. tool
output that annotation guide v1.1 Sec. 2 keeps away from the owner before labelling).
"""
from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pqscan.bench.candidates import QUOTAS, scope_class  # noqa: E402

C = collections.Counter


def jl(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


out: dict = {}

# ---------------------------------------------------------------- Dataset B manifest (metadata only)
man = jl(ROOT / "benchmark/real/manifest.json")
repos = {}
for split, rs in man["splits"].items():
    for r in rs:
        repos[r["repo"]] = {"split": split, **{k: r.get(k) for k in ("commit", "license", "stars", "py_files", "regex_candidates",
                                                                    "pyca_imports", "pycryptodome_imports", "in_baseline_corpus")}}
out["B_manifest"] = {
    "frozen": man["frozen"], "split_counts": dict(C(v["split"] for v in repos.values())),
    "per_split_sums": {s: {k: sum(v[k] or 0 for v in repos.values() if v["split"] == s)
                           for k in ("py_files", "regex_candidates", "pyca_imports", "pycryptodome_imports")}
                       for s in ("development", "validation", "test")},
    "pycryptodome_share_of_crypto_imports": {s: round(sum(v["pycryptodome_imports"] for v in repos.values() if v["split"] == s)
                                                      / max(1, sum(v["pycryptodome_imports"] + v["pyca_imports"] for v in repos.values() if v["split"] == s)), 4)
                                             for s in ("development", "validation", "test")},
    "repos_with_any_pycryptodome": {s: [k for k, v in repos.items() if v["split"] == s and v["pycryptodome_imports"]]
                                    for s in ("development", "validation", "test")},
    "licences": dict(C(v["license"] for v in repos.values())),
    "open_conditions": man["open_conditions"],
}

# ---------------------------------------------------------------- DV candidate orders
orders = {}
for p in sorted((ROOT / "benchmark/candidates").glob("*/order_*.json")):
    o = jl(p)
    entries = [(st, e) for st, es in o["strata"].items() for e in es]
    ids = [e["candidate_id"] for _, e in entries]
    locs = [(e["file"], e["line"]) for _, e in entries]
    scope_recomputed_mismatch = sum(1 for _, e in entries if scope_class(e["file"]) != e["scope"])
    orders[o["repo"]] = {
        "split": p.parent.name, "strata": o["counts"], "total": len(entries),
        "scope": dict(C(e["scope"] for _, e in entries)),
        "scope_by_stratum": {st: dict(C(e["scope"] for s2, e in entries if s2 == st)) for st in o["strata"]},
        "files": len({e["file"] for _, e in entries}),
        "duplicate_ids": len(ids) - len(set(ids)), "duplicate_locations": len(locs) - len(set(locs)),
        "scope_class_mismatch": scope_recomputed_mismatch,
        "missing_fields": sum(1 for _, e in entries if not all(k in e for k in ("candidate_id", "file", "line", "scope"))),
        "quota": QUOTAS[p.parent.name], "nonapp_cap": QUOTAS[p.parent.name] // 3,
    }
tot = C()
for v in orders.values():
    tot.update(v["strata"])
out["DV_orders"] = {"per_repo": orders, "strata_total": dict(tot), "candidates_total": sum(tot.values()),
                    "scope_total": dict(sum((C(v["scope"]) for v in orders.values()), C()))}

# ---------------------------------------------------------------- Dataset A (synthetic)
syn = [json.loads(l) for l in (ROOT / "benchmark/synthetic/sites.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
sm = jl(ROOT / "benchmark/synthetic/manifest.json")
schema = jl(ROOT / "docs/benchmark/benchmark_schema.json")
req = schema.get("required", [])
kind = {i["base_case"]: i["kind"] for i in sm["instances"]}
out["A_synthetic"] = {
    "instances": len(syn), "base_cases": len({r["base_case"] for r in syn}),
    "base_cases_by_kind": dict(C(kind.values())), "instances_by_kind": sm["counts"]["by_kind"],
    "split_instances": dict(C(sm["split"][r["base_case"]] for r in syn)),
    "library": dict(C(r["library"] for r in syn)), "algorithm": dict(C(r["algorithm"] for r in syn)),
    "role": dict(C(r["gt_role"] for r in syn)), "role_by_library": {lib: dict(C(r["gt_role"] for r in syn if r["library"] == lib))
                                                                    for lib in ("pyca", "pycryptodome")},
    "eligible": sum(bool(r["eligible"]) for r in syn), "scope": dict(C(r["scope"] for r in syn)),
    "assessability": dict(C(r["assessability"] for r in syn)), "provenance": dict(C(r["key_provenance"] for r in syn)),
    "evidence_scope": dict(C(r["evidence_scope"] for r in syn)), "transformation": dict(C(r["transformation"] for r in syn)),
    "hybrid_components": sum(str(r["hybrid_component"]).lower() in ("true", "yes") for r in syn),
    "duplicate_site_ids": len(syn) - len({r["site_id"] for r in syn}),
    "duplicate_files": len(syn) - len({r["file"] for r in syn}),
    "schema_required_fields": req,
    "records_missing_required": sum(1 for r in syn if any(k not in r for k in req)),
    "validation_subset": sum(1 for _ in open(ROOT / "benchmark/synthetic/validation_subset.csv", encoding="utf-8")) - 1,
    "label_status": "by construction (generator v1.0); 78-instance blind validation subset not yet labelled",
}

# ---------------------------------------------------------------- pilot
pilot = list(csv.DictReader(open(ROOT / "docs/pilot/h1_pilot_sites.csv", encoding="utf-8")))
el = [r for r in pilot if r["eligible"].strip().lower() in ("yes", "true")]
out["pilot"] = {
    "sites": len(pilot), "repos": dict(C(r["repo"] for r in pilot)), "eligible": len(el),
    "library": dict(C(r["library"] for r in pilot)), "algorithm": dict(C(r["algorithm"] for r in pilot)),
    "role": dict(C(r["gt_role"] for r in pilot)), "assessability": dict(C(r["assessability"] for r in pilot)),
    "provenance": dict(C(r["key_provenance"] for r in pilot)), "evidence_scope": dict(C(r["evidence_scope"] for r in pilot)),
    "obvious_from_name_among_eligible": dict(C(r["obvious_from_name"] for r in el)),
    "label_status": "developer labels from Phases 1-2; Module B was debugged on these sites (circular); not owner-final under guide v1.1",
}

# ---------------------------------------------------------------- labels, ledger, freeze, schemas, baselines
ann = ROOT / "benchmark/annotation"
out["labels_and_gates"] = {
    "owner_label_files": len([p for p in ann.rglob("*") if p.is_file()]) if ann.exists() else 0,
    "ledger_dir_exists": (ROOT / "benchmark/ledger").exists(),
    "ai_review_identity_exists": (ROOT / "docs/benchmark/ai_review_identity.json").exists(),
    "freeze_record_exists": (ROOT / "docs/freeze/pretest_freeze.json").exists(),
    "test_candidate_frames_built": any((ROOT / "benchmark/candidates/test").glob("order_*.json")) if (ROOT / "benchmark/candidates/test").exists() else False,
    "label_schema_fields": list(schema.get("properties", {}).keys()),
    "meta_schema_fields": list(jl(ROOT / "docs/benchmark/meta_schema.json").get("properties", {}).keys()),
}
bm = jl(ROOT / "benchmark/baselines_manifest.json")
out["baselines"] = {"pinned_tools": list(bm["tools"]), "not_runnable": bm.get("not_runnable", {})}
out["plan"] = {"quotas": QUOTAS, "planned_primary_eligible": {"test": 7 * 30, "development": 4 * 25, "validation": 2 * 25, "total": 360},
               "minimums": {"dataset_B": 300, "test": 150}, "owner_final_eligible_available": 0}

if "--write" in sys.argv:
    (ROOT / "docs/audit/dataset_audit_values.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                             encoding="utf-8", newline="\n")
print(json.dumps(out, indent=1, ensure_ascii=False))
