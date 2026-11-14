"""Synthetic benchmark generator (checklist B3). The generated code is only parsed, never imported or executed."""
from __future__ import annotations
import ast, csv, hashlib, json
from pathlib import Path
import jsonschema
import pytest
from pqscan.bench import synth
from pqscan.bench.synth import BASE_CASES, EVIDENCE_CHANGE, NEGATIVE_OPERATORS, OPERATORS, generate

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "docs/benchmark/benchmark_schema.json").read_text(encoding="utf-8"))
INVARIANT_FIELDS = ("gt_role", "assessability", "possible_roles", "secondary_roles", "eligible", "hybrid_component")


@pytest.fixture(scope="module")
def ds(tmp_path_factory):
    out = tmp_path_factory.mktemp("synthetic")
    manifest = generate(out)
    records = [json.loads(l) for l in (out / "sites.jsonl").read_text(encoding="utf-8").splitlines()]
    return out, manifest, records


def _tree(path: Path) -> dict[str, bytes]:
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}


def test_generation_is_deterministic(ds, tmp_path):
    out, _, _ = ds
    generate(tmp_path / "again")
    assert _tree(out) == _tree(tmp_path / "again")


def test_seed_changes_identifiers_but_never_labels(ds, tmp_path):
    out, _, records = ds
    generate(tmp_path / "other", seed=7)
    other = [json.loads(l) for l in (tmp_path / "other/sites.jsonl").read_text(encoding="utf-8").splitlines()]
    strip = lambda r: {k: v for k, v in r.items() if k not in ("line_start", "line_end")}  # noqa: E731
    assert [strip(r) for r in records] == [strip(r) for r in other]
    assert _tree(out) != _tree(tmp_path / "other")


def test_size_and_coverage(ds):
    _, manifest, records = ds
    assert 55 <= manifest["counts"]["base_cases"] <= 65
    pos = [b for b in BASE_CASES if b.kind != "neg"]
    neg = [b for b in BASE_CASES if b.kind == "neg"]
    assert len(records) == len(pos) * (len(OPERATORS) + 1) + len(neg) * len(NEGATIVE_OPERATORS)
    assert {r["gt_role"] for r in records} == {"SIGN", "VERIFY", "KEY_ESTABLISHMENT", "PK_ENCRYPT", "PK_DECRYPT",
                                                 "KEY_MATERIAL_ONLY", "UNKNOWN", "NONE"}
    assert {r["library"] for r in records if r["eligible"]} == {"pyca", "pycryptodome"}
    assert {r["transformation"] for r in records} == set(OPERATORS) | {EVIDENCE_CHANGE}
    assert len({b.id for b in BASE_CASES}) == len(BASE_CASES)
    assert len({r["site_id"] for r in records}) == len(records)


def test_every_record_is_valid_against_the_frozen_schema(ds):
    _, _, records = ds
    v = jsonschema.Draft202012Validator(SCHEMA)
    for r in records:
        errs = list(v.iter_errors(r))
        assert not errs, (r["site_id"], [e.message for e in errs])


def test_every_case_is_valid_python_and_imports_only_known_modules(ds):
    out, _, records = ds
    allowed = {"cryptography", "Crypto", "ecdsa"}
    for r in records:
        tree = ast.parse((out / r["file"]).read_text(encoding="utf-8"))
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom):
                assert n.module.split(".")[0] in allowed, (r["file"], n.module)
            assert not isinstance(n, ast.Import), r["file"]


def test_site_line_holds_the_labelled_construct(ds):
    out, _, records = ds
    by_id = {b.id: b for b in BASE_CASES}
    for r in records:
        b = by_id[r["base_case"]]
        lines = (out / r["file"]).read_text(encoding="utf-8").splitlines()
        line = lines[r["line_start"] - 1]
        assert r["line_start"] == r["line_end"]
        if b.kind == "neg":
            assert line.strip().startswith(("r0 = ", "#")), (r["site_id"], line)
            continue
        calls = {n.func.attr for n in ast.walk(ast.parse(line.strip().removeprefix("return ")))
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        if b.kind == "key":
            assert calls & {"generate_private_key", "generate", "import_key", "load_pem_private_key"}, (r["site_id"], line)
        else:
            assert r["method"] in calls, (r["site_id"], line)


def test_semantics_preserving_operators_keep_the_labels(ds):
    _, _, records = ds
    for b in BASE_CASES:
        rs = [r for r in records if r["base_case"] == b.id and r["transformation"] != EVIDENCE_CHANGE]
        for f in INVARIANT_FIELDS:
            assert len({json.dumps(r.get(f)) for r in rs}) == 1, (b.id, f)


def test_loaded_key_changes_provenance_only(ds):
    _, _, records = ds
    for b in BASE_CASES:
        if b.kind == "neg":
            assert not any(r["base_case"] == b.id and r["transformation"] == EVIDENCE_CHANGE for r in records)
            continue
        ident = next(r for r in records if r["base_case"] == b.id and r["transformation"] == "identity")
        loaded = next(r for r in records if r["base_case"] == b.id and r["transformation"] == EVIDENCE_CHANGE)
        assert loaded["key_provenance"] == "loaded-PEM" and ident["key_provenance"] == "generated"
        assert all(loaded.get(f) == ident.get(f) for f in INVARIANT_FIELDS), b.id


def test_labels_follow_the_taxonomy_rules(ds):
    _, _, records = ds
    for r in records:
        if r["gt_role"] == "UNKNOWN":                 # rule 2
            assert r["assessability"] == "INDETERMINATE" and len(r["possible_roles"]) == 2
            assert r["evidence_scope"] == "runtime-value"
        if not r["eligible"]:                          # rule 8
            assert r["gt_role"] == "NONE" and r["key_provenance"] == "n/a"
        if r["base_case"].endswith("-export"):         # rule 3
            assert r["gt_role"] == "KEY_MATERIAL_ONLY" and r["assessability"] == "DETERMINATE"
        if r["base_case"].endswith("-signverify"):     # rule 1, rule 9
            assert r["gt_role"] == "SIGN" and r["secondary_roles"] == ["VERIFY"]
        if "-op-" in r["base_case"]:                   # rule 4
            assert r["obvious_from_name"] is True and r["evidence_needed"] == "none"
        if r["transformation"] == "class-method" and "-op-" in r["base_case"]:
            assert r["key_provenance"] == "attribute" and r["ultimate_provenance"] == ["generated"]


def test_split_is_by_base_case_and_balanced(ds):
    _, manifest, _ = ds
    split = manifest["split"]
    assert set(split) == {b.id for b in BASE_CASES}
    for kind in ("key", "op", "neg"):
        vals = [split[b.id] for b in BASE_CASES if b.kind == kind]
        assert abs(vals.count("synthetic-dev") - vals.count("synthetic-holdout")) <= 1
    for p in manifest["instances"]:
        assert p["split"] == split[p["base_case"]]       # no variant of a held-out base case leaks into dev


def test_validation_subset_is_blind_stratified_and_deterministic(ds, tmp_path):
    out, manifest, records = ds
    rows = list(csv.DictReader((out / "validation_subset.csv").open(encoding="utf-8")))
    assert set(rows[0]) == {"site_id", "file", "line_start", "line_end"}     # no labels
    ids = {r["site_id"] for r in records}
    assert all(r["site_id"] in ids for r in rows)
    ops = {next(x["transformation"] for x in records if x["site_id"] == r["site_id"]) for r in rows}
    assert ops == set(OPERATORS) | {EVIDENCE_CHANGE}
    assert 0.18 <= len(rows) / len(records) <= 0.22
    assert manifest["validation_subset"]["size"] == len(rows)


def test_manifest_hashes_match_files(ds):
    out, manifest, _ = ds
    for p in manifest["instances"]:
        assert hashlib.sha256((out / p["file"]).read_bytes()).hexdigest() == p["sha256"]
    assert manifest["generator_sha256"] == synth.generator_hash()


def test_cli_writes_dataset(tmp_path, capsys):
    assert synth.main(["--out", str(tmp_path / "d")]) == 0
    assert "instances" in capsys.readouterr().out
    assert (tmp_path / "d/sites.jsonl").exists()
