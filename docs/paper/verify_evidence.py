"""Recompute every number quoted in docs/paper/ from the raw project files (evidence register, E-ids).

    .venv/Scripts/python docs/paper/verify_evidence.py            # prints values; exit 1 if any check fails
    .venv/Scripts/python docs/paper/verify_evidence.py --write    # also writes docs/paper/evidence/evidence_values.json

Read-only. Reads manifests, candidate orders, synthetic data, pilot files, DV run summaries (execution-level fields
only: run_status, timed_out, file_status_counts; no finding content), the generated acceptance report, the policy
YAML and the final-demo outputs. It never touches test-split repositories (only benchmark/real/manifest.json
metadata) and never prints DV tool findings (annotation guide v1.1 Sec. 2).
"""
from __future__ import annotations

import collections
import csv
import gzip
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
C = collections.Counter
V: dict[str, object] = {}
FAIL: list[str] = []


def put(eid: str, value, expect=None) -> None:
    V[eid] = value
    ok = expect is None or value == expect
    if not ok:
        FAIL.append(f"{eid}: got {value!r}, expected {expect!r}")
    print(f"{'OK ' if ok else 'BAD'} {eid}: {value}")


def jl(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


# --- repository state ---------------------------------------------------------------------------
put("E01.main", git("rev-parse", "main"), "81f561e34997dc56b2728241617cd19785210c85")
put("E01.main_eq_tag", git("rev-parse", "main") == git("rev-list", "-n", "1", "phase2-complete"), True)
put("E01.freeze_tag_absent", git("tag", "--list", "phase3-pretest-freeze") == "", True)
put("E01.freeze_record_absent", not (ROOT / "docs/freeze/pretest_freeze.json").exists(), True)
put("E01.ai_identity_absent", not (ROOT / "docs/benchmark/ai_review_identity.json").exists(), True)
ann = ROOT / "benchmark/annotation"
put("E01.label_files", len([p for p in ann.rglob("*") if p.is_file()]) if ann.exists() else 0, 0)
cache = ROOT / ".cache/repos"
put("E01.local_checkouts", sorted(p.name for p in cache.iterdir()) if cache.exists() else [])

# --- Dataset B manifest (metadata only) ---------------------------------------------------------
man = jl(ROOT / "benchmark/real/manifest.json")
split = {k: len(v) for k, v in man["splits"].items()}
put("E10.split", split, {"development": 4, "validation": 2, "test": 7})
put("E10.repositories", sum(split.values()), 13)
put("E10.frozen", man["frozen"], "2026-11-13")
put("E10.tuning_corpus_in_test", sum(r["in_baseline_corpus"] for r in man["splits"]["test"]), 0)
put("E10.pycryptodome_imports_dv", sum(r["pycryptodome_imports"] for s in ("development", "validation") for r in man["splits"][s]), 2)
put("E10.pyca_imports_dv", sum(r["pyca_imports"] for s in ("development", "validation") for r in man["splits"][s]), 254)
put("E10.pycryptodome_imports_test", {r["repo"]: r["pycryptodome_imports"] for r in man["splits"]["test"] if r["pycryptodome_imports"]})

# --- protocol quotas ----------------------------------------------------------------------------
from pqscan.bench.candidates import QUOTAS  # noqa: E402
put("E11.quotas", QUOTAS, {"test": 30, "development": 25, "validation": 25})
put("E11.planned_primary_sites", 7 * 30 + 4 * 25 + 2 * 25, 360)

# --- DV candidate frames ------------------------------------------------------------------------
tot = C()
for p in sorted((ROOT / "benchmark/candidates").glob("*/order_*.json")):
    o = jl(p)
    assert o["format"] == "pqscan-order/2" and o["protocol"] == "1.0.4"
    tot.update(o["counts"])
put("E12.orders", len(list((ROOT / "benchmark/candidates").glob("*/order_*.json"))), 6)
put("E12.strata", dict(tot), {"S1-app": 920, "S1-nonapp": 1080, "S2": 1503})
put("E12.candidates_total", sum(tot.values()), 3503)

# --- Dataset A (synthetic) ----------------------------------------------------------------------
syn = [json.loads(line) for line in (ROOT / "benchmark/synthetic/sites.jsonl").read_text(encoding="utf-8").splitlines() if line]
sm = jl(ROOT / "benchmark/synthetic/manifest.json")
put("E13.instances", len(syn), 388)
put("E13.base_cases", len({r["base_case"] for r in syn}), 61)
put("E13.by_kind", sm["counts"]["by_kind"], {"key": 182, "neg": 52, "op": 154})
put("E13.split_base_cases", dict(C(sm["split"].values())), {"synthetic-dev": 31, "synthetic-holdout": 30})
put("E13.split_instances", dict(C(sm["split"][r["base_case"]] for r in syn)), {"synthetic-dev": 196, "synthetic-holdout": 192})
put("E13.roles", dict(C(r["gt_role"] for r in syn)), {"SIGN": 140, "NONE": 52, "KEY_MATERIAL_ONLY": 42, "KEY_ESTABLISHMENT": 42,
                                                     "VERIFY": 35, "PK_DECRYPT": 28, "PK_ENCRYPT": 28, "UNKNOWN": 21})
put("E13.libraries", dict(C(r["library"] for r in syn)), {"pyca": 241, "pycryptodome": 127, "unknown": 16, "out-of-scope:ecdsa": 4})
put("E13.eligible", sum(bool(r["eligible"]) for r in syn), 336)
put("E13.validation_subset", sum(1 for _ in open(ROOT / "benchmark/synthetic/validation_subset.csv", encoding="utf-8")) - 1, 78)
put("E13.transformations", dict(C(r["transformation"] for r in syn)))
put("E13.provenance", dict(C(r["key_provenance"] for r in syn)))
put("E13.hybrids", sum(str(r["hybrid_component"]).lower() in ("true", "yes") for r in syn), 0)

# --- pilot (circular development data) ----------------------------------------------------------
pilot = list(csv.DictReader(open(ROOT / "docs/pilot/h1_pilot_sites.csv", encoding="utf-8")))
put("E14.pilot_sites", len(pilot), 31)
put("E14.pilot_repos", sorted({r["repo"] for r in pilot}))
put("E14.pilot_eligible", sum(r["eligible"].strip().lower() in ("yes", "true") for r in pilot), 30)

# --- DV tool runs (execution level only) --------------------------------------------------------
for run, n in (("development/run1", 40), ("validation/run1", 20)):
    p = ROOT / "runs" / run / "batch_summary.json"
    if not p.exists():
        put(f"E20.{run}", "runs/ not present in this checkout (git-ignored)")
        continue
    rs = jl(p)["runs"]
    fs = C()
    for r in rs:
        fs.update(r["file_status_counts"])
    put(f"E20.{run}.ok", f"{sum(r['run_status'] == 'ok' for r in rs)}/{len(rs)}", f"{n}/{n}")
    put(f"E20.{run}.timeouts", sum(r["timed_out"] for r in rs), 0)
    put(f"E20.{run}.file_status", dict(fs))

# --- statistical acceptance (generated report) --------------------------------------------------
acc = jl(ROOT / "docs/implementation/acceptance/statistical_acceptance.json")
put("E30.accepted", acc["accepted"], True)
put("E30.code_commit", acc["commit"], "aa9d6b00697f8f480c1c4be1b62cd3588731b685")
# E30 is scoped to the calibration's code closure (scripts/calibration_closure.py): the files the calibration loads,
# import-traced, byte-identical at the calibration commit, HEAD and in the working tree; plus the driver script.
sys.path.insert(0, str(ROOT / "scripts"))
import calibration_closure as CC  # noqa: E402

put("E30.closure_commit_matches", CC.CALIBRATION_COMMIT == acc["commit"], True)
_cc = CC.status(ROOT)
put("E30.closure_files", len(CC.CLOSURE), 9)
put("E30.closure_traced", _cc["closure_traced"], True)
put("E30.closure_unchanged", _cc["closure_unchanged"], True)
put("E30.driver_since_5d78a06", _cc["driver_since_ref"], True)
for _p in _cc["problems"]:
    print("    E30:", _p)
put("E30.pqscan_changed_since_outside_closure",           # informational: what changed in pqscan/ since calibration
    sorted(set(git("diff", "--name-only", acc["commit"], "HEAD", "--", "pqscan").split()) - set(CC.CLOSURE)))
put("E30.B", acc["B"], 1000)
put("E30.failed_cells", acc["failed_cells"], [])
md = (ROOT / "docs/implementation/acceptance/statistical_acceptance.md").read_text(encoding="utf-8")
rows = {m.group(1): m.group(0) for m in re.finditer(r"^\| (S\d\d|N[+-]\d\.\d\d|C\d|TS\d) \|.*$", md, re.M)}


def cells(rid: str) -> list[float]:
    return [float(x) for x in re.findall(r"\| (0\.\d{4})", rows[rid])]


fixed = [r for r in rows if r.startswith("S") and r != "S16"]
worst = [max(cells(r)[i] for r in fixed) for i in range(3)]
put("E31.typeI_worst_fixed_a3_a2_a", worst, [0.0061, 0.0093, 0.0191])
nk = [r for r in rows if r.startswith("N")]
put("E31.nearkink_worst", [max(cells(r)[i] for r in nk) for i in range(3)], [0.0092, 0.0125, 0.0213])
put("E31.S16_a", cells("S16")[2], 0.0415)
put("E32.fwer_worst", max(cells(r)[0] for r in rows if r.startswith("C")), 0.0125)
ts = [[float(x) for x in re.findall(r"0\.\d{4}", rows[r])[:3]] for r in rows if r.startswith("TS")]  # unstratified a/3, a/2, a
put("E33.two_stratum_unstratified_worst", [max(t[i] for t in ts) for i in range(3)], [0.0025, 0.0040, 0.0114])
put("E33.variant_in_force", acc["variant_in_force"], "unstratified")

# --- policy role mapping ------------------------------------------------------------------------
import yaml  # noqa: E402
pol = yaml.safe_load((ROOT / "pqscan/policy/policy_v1_1.yaml").read_text(encoding="utf-8"))
put("E40.policy_version", pol["version"], "1.1")
put("E40.role_map", pol["roles"], {"SIGN": "SIG", "VERIFY": "SIG", "KEY_ESTABLISHMENT": "KEM", "PK_ENCRYPT": "KEM_DEM",
                                   "PK_DECRYPT": "KEM_DEM", "KEY_MATERIAL_ONLY": "INVENTORY",
                                   "PROTOCOL_CONFIG": "PROTOCOL_REVIEW", "UNKNOWN": "ABSTAIN"})
put("E40.default_threshold", pol["default_tier_threshold"], "T2")
roles_src = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "pqscan/roles").rglob("*.py"))
put("E41.protocol_config_emitted_by_module_C", "PROTOCOL_CONFIG" in roles_src, False)

# --- demonstrations -----------------------------------------------------------------------------
fx = jl(ROOT / "docs/demo/outputs/02_scan.json")
put("E50.fixture_sites", len(fx["findings"]), 23)
put("E50.fixture_actions", dict(C(f["recommendation"]["action"] for f in fx["findings"])))
put("E50.fixture_roles", dict(C(f["decision"]["role"] for f in fx["findings"])))
real = ROOT / "docs/final/demo/outputs/real"
for name, gzipped, exp in (("cryptography-47.0.0", False, 13), ("pycryptodome-4.4.0", True, 1214)):
    p = real / (f"{name}_scan.json" + (".gz" if gzipped else ""))
    d = json.loads(gzip.decompress(p.read_bytes()) if gzipped else p.read_text(encoding="utf-8"))
    F = d["findings"]
    put(f"E51.{name}.files_scanned", d["files_scanned"])
    put(f"E51.{name}.execution_failures", len(d["execution_failures"]), 0)
    put(f"E51.{name}.sites", len(F), exp)
    put(f"E51.{name}.actions", dict(C(f["recommendation"]["action"] for f in F)))
    put(f"E51.{name}.classes", dict(C(f["recommendation"]["target_class"] for f in F)))
    put(f"E51.{name}.excluded", len(d["excluded"]))
    put(f"E51.{name}.semgrep_only", len(d["semgrep_only"]))
    put(f"E51.{name}.semantic_only_sites", sum(1 for f in F if not f["semgrep_rules"]))
    bad = [f for f in F if f["recommendation"]["action"] != "ABSTAIN"
           and pol["roles"].get(f["decision"]["role"]) != f["recommendation"]["target_class"]]
    put(f"E52.{name}.non_abstain_class_mismatch", len(bad), 0)
    odd = [f for f in F if f["recommendation"]["action"] == "ABSTAIN"
           and not (f["decision"]["role"] == "UNKNOWN" or f["decision"]["tier"] in ("T0", "T1"))]
    put(f"E52.{name}.abstain_without_unknown_or_low_tier", len(odd), 0)
    low = [f for f in F if f["recommendation"]["action"] == "RECOMMEND" and f["decision"]["tier"] in ("T0", "T1")]
    put(f"E52.{name}.recommend_below_T2", len(low), 0)
val = (ROOT / "docs/final/demo/outputs/validation.txt").read_text(encoding="utf-8")
put("E53.schema_valid", f"{val.count(': VALID')}/{len(val.strip().splitlines())}", "6/6")

# --- pre-F1 corrections of 18 Nov 2026 (owner decision register v1.0.5) ------------------------------
fa1 = jl(ROOT / "docs/implementation/acceptance/fa_type1.json")
put("E63.fa_type1_all_pass", fa1["all_pass"], True)
put("E63.single_R", sorted({v["R"] for v in fa1["single"].values()}), [20000])
put("E63.family_R", sorted({v["R"] for v in fa1["family"].values()}), [10000])
put("E63.max_single_rate", round(max(v["rejection_rate"] for v in fa1["single"].values()), 4), 0.0089)
put("E63.max_family_fwer", round(max(v["fwer_null_baselines"] for v in fa1["family"].values()), 4), 0.0047)
f03 = jl(ROOT / "docs/audit/evidence/f03_multicall_pool.json")
put("E64.pool_candidates", f03["pool_candidates"], 3503)
put("E64.multi_call_candidates", len(f03["multi_call"]), 8)
put("E65.protocol_version", (ROOT / "docs/specification/evaluation_protocol.md").read_text(encoding="utf-8").splitlines()[0],
    "# Evaluation protocol (v1.0.5, pre-registered)")
rec105 = jl(ROOT / "docs/specification/adoption_record_v1.0.5.json")
put("E65.adoption_record", rec105["protocol_version"], "1.0.5")

if "--write" in sys.argv:
    out = ROOT / "docs/paper/evidence/evidence_values.json"
    out.write_text(json.dumps({"head": git("rev-parse", "HEAD"), "values": V, "failures": FAIL}, indent=1, default=str) + "\n",
                   encoding="utf-8", newline="\n")
    print("wrote", out.relative_to(ROOT))
print(f"\n{len(V)} values, {len(FAIL)} failed checks")
sys.exit(1 if FAIL else 0)
