"""Owner decisions of 19 Nov 2026 (docs/audit/owner_decisions_g02_g03_g08_g10.md): G02 nullable obvious_from_name
(schema v1.1, Dataset A generator 1.1, pilot migration), G03 units with the F03 rule retained, G08 frozen H4 set."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from pqscan.baselines.adapters import ADAPTERS
from pqscan.baselines.simple import ARMS, H2_ARMS
from pqscan.bench import fa, h4, synth
from pqscan.bench import labels as LB

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "docs/benchmark/benchmark_schema.json").read_text(encoding="utf-8"))
V = Draft202012Validator(SCHEMA)
SITES = [json.loads(x) for x in (ROOT / "benchmark/synthetic/sites.jsonl").read_text(encoding="utf-8").splitlines() if x]
OLD = [json.loads(x) for x in (ROOT / "benchmark/synthetic/archive/generator-1.0/sites.jsonl").read_text(encoding="utf-8").splitlines() if x]
SPEC = json.loads((ROOT / "docs/specification/run_specification_pre_f1.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ G02
def _rec(**kw):
    base = dict(SITES[0])
    base.update(kw)
    return base


def test_g02_schema_requires_null_on_ineligible_and_boolean_on_eligible():
    neg = next(r for r in SITES if not r["eligible"])
    pos = next(r for r in SITES if r["eligible"])
    assert not list(V.iter_errors(neg)) and neg["obvious_from_name"] is None
    assert not list(V.iter_errors(pos)) and isinstance(pos["obvious_from_name"], bool)
    assert list(V.iter_errors(dict(neg, obvious_from_name=False)))             # false is no longer "not applicable"
    assert list(V.iter_errors(dict(pos, obvious_from_name=None)))              # eligible needs a boolean
    assert list(V.iter_errors(dict(pos, obvious_from_name="n/a")))             # never coerced
    assert SCHEMA["title"].endswith("(v1.2)")             # v1.1 (G02), then v1.2 (TA19, revision r5)


def test_g02_dataset_a_fully_valid_and_only_the_contract_field_migrated():
    assert len(SITES) == 388 and all(not list(V.iter_errors(r)) for r in SITES)
    assert [r["site_id"] for r in SITES] == [r["site_id"] for r in OLD]
    for new, old in zip(SITES, OLD):
        changed = {k for k in set(new) | set(old) if new.get(k) != old.get(k)}
        assert changed <= {"commit", "obvious_from_name"}, (new["site_id"], changed)
        if "obvious_from_name" in changed:
            assert old["eligible"] is False and old["obvious_from_name"] is False and new["obvious_from_name"] is None
    assert sum(1 for r in SITES if not r["eligible"]) == 52
    assert {r["obvious_from_name"] for r in SITES if not r["eligible"]} == {None}
    m = json.loads((ROOT / "benchmark/synthetic/manifest.json").read_text(encoding="utf-8"))
    assert m["generator_version"] == synth.GENERATOR_VERSION == "1.1" and m["generator_sha256"] == synth.generator_hash()


def test_g02_pilot_record_migrated_and_original_preserved():
    rows = list(csv.DictReader((ROOT / "docs/pilot/h1_pilot_sites.csv").open(encoding="utf-8")))
    old = list(csv.DictReader((ROOT / "docs/pilot/archive/h1_pilot_sites_pre_g02.csv").open(encoding="utf-8")))
    assert len(rows) == len(old) == 31
    for n, o in zip(rows, old):
        diff = {k for k in n if n[k] != o[k]}
        assert diff <= {"obvious_from_name"}
        if diff:
            assert o["obvious_from_name"] == "n/a" and n["obvious_from_name"] == "null" and o["eligible"].lower() == "no"
    assert not any(r["obvious_from_name"] == "n/a" for r in rows)


def test_g02_label_validator_accepts_null_only_where_not_applicable():
    from pqscan.bench.loops import normalise
    assert normalise("obvious_from_name", "null") is None and normalise("obvious_from_name", None) is None
    full, _meta, partial = LB._validators()
    assert partial.schema["properties"]["obvious_from_name"] == {"type": ["boolean", "null"]}


@pytest.mark.parametrize("path,needle", [
    ("docs/specification/role_taxonomy.md", "`obvious_from_name = null`"),
    ("docs/benchmark/annotation_guide.md", "`site.obvious_from_name` is a JSON boolean on an eligible record and `null`"),
    ("docs/specification/data_dictionary.md", "| `obvious_from_name` | bool or null |"),
    ("docs/benchmark/ai_review_prompt_v1.md", '"obvious_from_name": true or false (null when eligible is false)'),
])
def test_g02_documents_consistent(path, needle):
    assert needle in (ROOT / path).read_text(encoding="utf-8")


# ------------------------------------------------------------------ G03
def test_g03_units_defined_and_f03_rule_retained():
    g = (ROOT / "docs/benchmark/annotation_guide.md").read_text(encoding="utf-8")
    units = g[g.index("**Units (r3, owner decision G03"):]
    for term in ("*candidate-discovery unit*", "*sampling unit*", "*primary annotated site*", "*analysis unit*",
                 "`also-call: <api_call> @<line>:<column>`", "at most 8 of the 3,503", "never expanded retrospectively"):
        assert term in units, term
    ev = json.loads((ROOT / "docs/audit/evidence/f03_multicall_pool.json").read_text(encoding="utf-8"))
    assert ev["pool_candidates"] == 3503 and len(ev["multi_call"]) == 8


# ------------------------------------------------------------------ G08
def test_g08_registry_json_and_code_agree():
    inv = SPEC["interpretations"]["H-6 (H4)"]["tool_inventory_G08"]
    assert tuple(inv["decision_set_part1"]) == h4.PART1_BASELINES == tuple(SPEC["families"]["F-A"]["baselines"])
    assert h4.PROPOSED_ANALYSER == fa.SYSTEM == inv["proposed_analyser"]
    externals = [b for b in h4.PART1_BASELINES if not b.startswith("pqscan:")]
    assert set(externals) == set(ADAPTERS)
    arms = {f"pqscan:{a}" for a in set(ARMS) | set(H2_ARMS)}
    assert set(inv["pqscan_arm_roles"]) == arms and len(arms) == 7
    assert set(h4.T0_COMPARATORS_SEPARATE).isdisjoint(h4.PART1_BASELINES)
    assert set(h4.DESCRIPTIVE_ONLY).isdisjoint(h4.PART1_BASELINES)
    manifest = json.loads((ROOT / "benchmark/baselines_manifest.json").read_text(encoding="utf-8"))
    assert set(h4.EXCLUDED) == set(manifest["not_runnable"]) == set(inv["not_runnable"])
    assert any(d["id"] == "OD-2026-11-19" and d["by"] == "owner" for d in SPEC["decisions"])
