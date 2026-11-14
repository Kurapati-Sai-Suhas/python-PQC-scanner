"""Pipeline (A+B+C+D) and Module E exports on a fixture project: schema validity, semantic links,
no secrets, determinism, transparent failures and safe traversal."""
from __future__ import annotations
import json, os, shutil
from pathlib import Path
import pytest
from pqscan.cli import main
from pqscan.export import to_cbom, to_sarif, to_json, validate_cbom
from pqscan.pipeline import scan, scope_of

PROJECT = Path(__file__).parent / "fixtures" / "project"


@pytest.fixture(scope="module")
def result():
    return scan(PROJECT)


def by_site(res, file, needle):
    lines = (PROJECT / file).read_text(encoding="utf-8").splitlines()
    line = next(i for i, l in enumerate(lines, 1) if needle in l)
    hits = [f for f in res.findings if f.evidence.candidate.location.file == file and f.evidence.candidate.location.line == line]
    assert hits, f"no finding at {file}:{line}"
    return hits[0]


def test_roles_and_recommendations_end_to_end(result):
    assert by_site(result, "app/keys.py", "self.key.sign(").recommendation.target_class == "SIG"
    assert by_site(result, "app/keys.py", "self.priv.exchange(").recommendation.target_class == "KEM"
    enc = by_site(result, "app/keys.py", "pub.encrypt(")
    assert enc.recommendation.target_class == "KEM_DEM" and "redesign" in enc.recommendation.rationale.lower()
    unk = by_site(result, "app/keys.py", "key.sign(data)")
    assert unk.recommendation.action == "ABSTAIN" and unk.decision.tier.value == "T0"


def test_semgrep_joined_and_status_recorded(result):
    assert result.semgrep_status == "ok"
    keygen = by_site(result, "app/keys.py", "rsa.generate_private_key(")
    assert "pqscan.pyca.rsa.keygen" in keygen.semgrep_rules


def test_parse_failure_is_an_execution_failure_not_an_abstention(result):
    assert any(e["file"] == "app/broken.py" for e in result.errors)
    assert not any(f.evidence.candidate.location.file == "app/broken.py" for f in result.findings)


def test_scope_attribution(result):
    assert by_site(result, "tests/test_dummy.py", "k.sign(").scope == "test"
    assert scope_of("pkg/_vendor/x.py") == "vendored" and scope_of("examples/a.py") == "example" and scope_of("pkg/a.py") == "app"


def test_exclude_tests_option():
    res = scan(PROJECT, include_tests=False, run_semgrep_rules=False)
    assert not any(f.scope == "test" for f in res.findings)


def test_cbom_validates_against_cyclonedx_1_6(result):
    bom = to_cbom(result)
    assert validate_cbom(bom) == []
    assert bom["specVersion"] == "1.6" and all(c["type"] == "cryptographic-asset" for c in bom["components"])


def test_cbom_semantic_links(result):
    bom = to_cbom(result)
    comps = {c["bom-ref"]: c for c in bom["components"]}
    sign = by_site(result, "app/keys.py", "self.key.sign(")
    keygen = by_site(result, "app/keys.py", "rsa.generate_private_key(")
    sref = f"pqscan:site:app/keys.py:{sign.evidence.candidate.location.line}:{sign.evidence.candidate.location.col}"
    kref = f"pqscan:site:app/keys.py:{keygen.evidence.candidate.location.line}:{keygen.evidence.candidate.location.col}"
    dep = next(d for d in bom["dependencies"] if d["ref"] == sref)
    assert kref in dep["dependsOn"]
    props = {p["name"]: p["value"] for p in comps[sref]["properties"]}
    assert props["pqscan:role"] == "SIGN" and props["pqscan:targetClass"] == "SIG" and props["pqscan:padding"] == "PSS"
    ap = comps[sref]["cryptoProperties"]["algorithmProperties"]
    assert ap["primitive"] == "signature" and ap["cryptoFunctions"] == ["sign"] and ap["padding"] == "other"
    km = comps[kref]["cryptoProperties"]
    assert km["assetType"] == "related-crypto-material" and km["relatedCryptoMaterialProperties"]["type"] == "private-key"
    assert km["relatedCryptoMaterialProperties"]["size"] == 3072
    ex = comps[f"pqscan:site:app/keys.py:{by_site(result, 'app/keys.py', 'self.priv.exchange(').evidence.candidate.location.line}:"
               f"{by_site(result, 'app/keys.py', 'self.priv.exchange(').evidence.candidate.location.col}"]
    assert ex["name"] == "ECDH" and ex["cryptoProperties"]["algorithmProperties"]["primitive"] == "key-agree"
    assert ex["cryptoProperties"]["algorithmProperties"]["curve"] == "SECP384R1"


def test_no_secrets_or_source_in_any_output(result):
    for doc in (to_cbom(result), to_sarif(result), to_json(result)):
        text = json.dumps(doc, default=str)
        assert "BEGIN PRIVATE KEY" not in text and "testonly" not in text


def test_cbom_is_deterministic():
    a, b = to_cbom(scan(PROJECT)), to_cbom(scan(PROJECT))
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert "timestamp" not in a["metadata"]


def test_sarif_structure(result):
    s = to_sarif(result)
    assert s["version"] == "2.1.0" and len(s["runs"][0]["results"]) == len(result.findings)
    assert s["runs"][0]["invocations"][0]["executionSuccessful"] is False  # broken.py recorded


def test_size_limit_skips_large_files(tmp_path):
    big = tmp_path / "big.py"
    big.write_text("from cryptography.hazmat.primitives.asymmetric import rsa\n" + "#" * 5000 + "\n", encoding="utf-8")
    res = scan(tmp_path, max_bytes=1000, run_semgrep_rules=False)
    assert res.files_skipped and "larger than" in res.files_skipped[0]["reason"]


def test_symlink_outside_root_is_not_followed(tmp_path):
    outside = tmp_path / "outside"; outside.mkdir()
    (outside / "secret.py").write_text("from cryptography.hazmat.primitives.asymmetric import rsa\nk = rsa.generate_private_key(65537, 2048)\n")
    root = tmp_path / "root"; root.mkdir()
    try:
        os.symlink(outside / "secret.py", root / "link.py")
        os.symlink(outside, root / "linkdir", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this system")
    res = scan(root, run_semgrep_rules=False)
    assert res.findings == [] and any(s["file"] == "link.py" for s in res.files_skipped)


def test_cli_formats(tmp_path, capsys):
    out = tmp_path / "bom.json"
    assert main(["scan", str(PROJECT), "--format", "cbom", "-o", str(out)]) == 0
    assert validate_cbom(json.loads(out.read_text(encoding="utf-8"))) == []
    assert main(["scan", str(PROJECT), "--format", "summary", "--no-semgrep"]) == 0
    assert "policy 1.1" in capsys.readouterr().out
    assert main(["scan", str(tmp_path / "missing")]) == 2


def test_cli_threshold_and_arm(capsys):
    assert main(["scan", str(PROJECT), "--format", "json", "--tier-threshold", "T3", "--arm", "method-only", "--no-semgrep"]) == 0
    doc = json.loads(capsys.readouterr().out)
    assert doc["tier_threshold"] == "T3" and doc["arm"] == "method-only"
    assert all(f["recommendation"]["action"] == "ABSTAIN" for f in doc["findings"])


@pytest.mark.skipif(os.name != "nt", reason="directory junctions are a Windows feature")
def test_windows_junction_outside_root_is_not_followed(tmp_path):
    import subprocess
    outside = tmp_path / "outside"; outside.mkdir()
    (outside / "secret.py").write_text("from cryptography.hazmat.primitives.asymmetric import rsa\nk = rsa.generate_private_key(65537, 2048)\n")
    root = tmp_path / "root"; root.mkdir()
    r = subprocess.run(["cmd", "/c", "mklink", "/J", str(root / "junction"), str(outside)], capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("mklink /J failed: " + r.stderr.strip()[:100])
    res = scan(root, run_semgrep_rules=False)
    assert res.findings == [] and res.files_scanned == 0


def test_out_of_scope_libraries_are_reported_not_ignored(result):
    libs = {(u["file"], u["library"]) for u in result.unsupported}
    assert ("app/legacy.py", "python-rsa") in libs and ("app/legacy.py", "python-ecdsa") in libs
    assert not any(f.evidence.candidate.location.file == "app/legacy.py" for f in result.findings)
    assert to_json(result)["unsupported"]


def test_sarif_validates_against_official_schema(result):
    from jsonschema import Draft4Validator
    schema = json.loads((Path(__file__).resolve().parents[1] / "pqscan/export/schemas/sarif-2.1.0.json").read_text(encoding="utf-8"))
    errors = list(Draft4Validator(schema).iter_errors(to_sarif(result)))
    assert errors == [], [e.message for e in errors[:3]]


# ---------------------------------------------------------------- review findings 3, 4, 9
def test_timeout_stops_only_the_slow_file(tmp_path):
    import time
    src = "from cryptography.hazmat.primitives.asymmetric import rsa\nk = rsa.generate_private_key(65537, 2048)\n"
    for name in ("a_slow.py", "b.py", "c.py"):
        (tmp_path / name).write_text(src, encoding="utf-8")
    t0 = time.monotonic()
    res = scan(tmp_path, run_semgrep_rules=False, file_timeout_s=3.0, analyzer="tests.slow_analyzer:analyze")
    elapsed = time.monotonic() - t0
    assert [e["file"] for e in res.errors] == ["a_slow.py"] and "exceeded" in res.errors[0]["error"]
    assert {f.evidence.candidate.location.file for f in res.findings} == {"b.py", "c.py"}
    assert elapsed < 25, f"slow file was not stopped (took {elapsed:.1f}s)"


@pytest.mark.skipif(os.name != "nt", reason="directory junctions are a Windows feature")
def test_semgrep_does_not_follow_a_junction_out_of_the_root(tmp_path):
    import subprocess
    outside = tmp_path / "outside"; outside.mkdir()
    (outside / "secret_mod.py").write_text("from cryptography.hazmat.primitives.asymmetric import rsa\nk = rsa.generate_private_key(65537, 2048)\n")
    root = tmp_path / "root"; root.mkdir()
    (root / "app.py").write_text("x = 1\n")
    r = subprocess.run(["cmd", "/c", "mklink", "/J", str(root / "link"), str(outside)], capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("mklink /J failed")
    res = scan(root)
    text = json.dumps(to_json(res), default=str)
    assert res.semgrep_status.startswith("ok") and "secret_mod" not in text and str(outside) not in text


def test_semgrep_scans_tests_directories_when_tests_are_included(result):
    hit = by_site(result, "tests/test_dummy.py", "ec.generate_private_key(")
    assert "pqscan.pyca.ec.keygen" in hit.semgrep_rules


def test_no_string_literal_from_source_reaches_any_output():
    res = scan(PROJECT)
    assert any(f.evidence.candidate.location.file == "app/literals.py" for f in res.findings)
    for doc in (to_cbom(res), to_sarif(res), to_json(res)):
        assert "QX7" not in json.dumps(doc, default=str)
