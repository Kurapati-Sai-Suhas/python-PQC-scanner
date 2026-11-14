"""Candidate pool and seeded sequential sampler (owner decisions D2 = O2, D3a; protocol v1.0.3)."""
from __future__ import annotations
import json, sys
from pathlib import Path
import pytest
from pqscan.bench import candidates as C
from pqscan.bench.candidates import build_pool, next_batch, order_pool, annotator_list, statement_starts

ROOT = Path(__file__).resolve().parents[1]


def _repo(tmp: Path) -> Path:
    r = tmp / "demo"
    (r / "pkg").mkdir(parents=True)
    (r / "tests").mkdir()
    (r / "pkg" / "keys.py").write_text(
        "from cryptography.hazmat.primitives.asymmetric import rsa, padding\n"
        "from cryptography.hazmat.primitives import hashes\n"
        "def make():\n"
        "    k = rsa.generate_private_key(\n"
        "        public_exponent=65537,\n"
        "        key_size=3072)\n"
        "    return k.sign(b'x', padding.PKCS1v15(), hashes.SHA256())\n", encoding="utf-8")
    (r / "pkg" / "util.py").write_text("import hashlib\n\ndef h(d):\n    return hashlib.sha256(d).hexdigest()\n", encoding="utf-8")
    (r / "tests" / "test_keys.py").write_text(
        "from cryptography.hazmat.primitives.asymmetric import ec\n"
        "def test_k():\n    ec.generate_private_key(ec.SECP256R1())\n", encoding="utf-8")
    return r


def _run_dir(tmp: Path, repo: Path) -> Path:
    d = tmp / "run"
    d.mkdir()
    # a qsafe report: one finding on line 5 of the multi-line keygen statement, one on the non-crypto file,
    # one on a file outside the repository (ignored)
    findings = [{"file": str(repo / "pkg" / "keys.py"), "line": 5, "migration": "ML-DSA", "algorithm": "RSA", "context": "x"},
                {"file": "pkg/util.py", "line": 4, "migration": "SHA-3", "algorithm": "SHA256", "context": "hash"},
                {"file": "elsewhere/x.py", "line": 1, "migration": "", "algorithm": "RSA", "context": ""}]
    (d / "qsafe_demo.json").write_text(json.dumps({"findings": findings}), encoding="utf-8")
    return d


def test_regex_is_identical_to_qualification_regex():
    sys.path.insert(0, str(ROOT / "experiments" / "bench"))
    import verify_candidates as v
    assert v.REGEX.pattern == C.REGEX.pattern and v.PYCA.pattern == C.PYCA.pattern
    assert v.PYCRYPTODOME.pattern == C.PYCRYPTODOME.pattern


def test_statement_dedupe_maps_multiline_calls_to_their_start():
    starts = statement_starts("x = f(\n  1,\n  2)\nif x:\n    y = 1\n")
    assert starts[1] == starts[2] == starts[3] == 1 and starts[4] == 4 and starts[5] == 5
    assert statement_starts("def (:\n") == {}


def test_pool_is_the_union_with_strata_and_sources_kept_apart(tmp_path):
    repo = _repo(tmp_path)
    pool, sources = build_pool(repo, _run_dir(tmp_path, repo), "demo")
    got = {(c["file"], c["line"]): c["stratum"] for c in pool}
    assert got[("pkg/keys.py", 4)] == "S1-app"          # regex line 4 + qsafe line 5 merged into one statement
    assert ("pkg/keys.py", 5) not in got
    assert got[("pkg/keys.py", 7)] == "S1-app"          # regex only: no tool reported it
    assert got[("tests/test_keys.py", 3)] == "S1-test"
    assert got[("pkg/util.py", 4)] == "S2"              # tool-only, non-crypto file
    assert not any(f.startswith("elsewhere") for f, _ in got)
    assert sources["pkg/keys.py:4"] == ["qsafe", "regex"] and sources["pkg/keys.py:7"] == ["regex"]
    assert all(set(c) == {"file", "line", "stratum"} for c in pool)


def test_pool_without_tool_outputs_is_regex_only(tmp_path):
    pool, sources = build_pool(_repo(tmp_path), None, "demo")
    assert pool and all(s == ["regex"] for s in sources.values())


def test_order_is_seeded_reproducible_and_complete(tmp_path):
    pool = [{"file": f"f{i}.py", "line": 1, "stratum": "S1-app"} for i in range(50)]
    a, b = order_pool(pool, "r", "abc"), order_pool(list(reversed(pool)), "r", "abc")
    assert a == b                                        # independent of input order
    c = order_pool(pool, "r", "abc", seed=1)
    assert [x["file"] for x in c["strata"]["S1-app"]] != [x["file"] for x in a["strata"]["S1-app"]]
    assert sorted(x["file"] for x in a["strata"]["S1-app"]) == sorted(p["file"] for p in pool)
    assert a["strata"]["S1-app"][0]["candidate_id"] == "C-r-S1-app-0001" and len(a["pool_sha256"]) == 64


def _order(n_app=200, n_test=100, n_s2=40):
    pool = ([{"file": f"a{i}.py", "line": 1, "stratum": "S1-app"} for i in range(n_app)]
            + [{"file": f"tests/t{i}.py", "line": 1, "stratum": "S1-test"} for i in range(n_test)]
            + [{"file": f"s{i}.py", "line": 1, "stratum": "S2"} for i in range(n_s2)])
    return order_pool(pool, "r", "abc")


def _run(order, quota, is_eligible):
    labels, batches = {}, []
    while True:
        res = next_batch(order, labels, quota)
        if res["stop"]:
            return res, batches, labels
        batches.append(res["batch"])
        for c in res["batch"]:
            labels[c["candidate_id"]] = is_eligible(c)


def test_first_batch_is_7_app_3_test_plus_10_fixed_s2():
    o = _order()
    res = next_batch(o, {}, 30)
    kinds = [c["candidate_id"].split("-")[2] + "-" + c["candidate_id"].split("-")[3] for c in res["batch"]]
    assert kinds.count("S1-app") == 7 and kinds.count("S1-test") == 3 and kinds.count("S2-0001"[:2]) == 0
    assert sum(c["candidate_id"].startswith("C-r-S2-") for c in res["batch"]) == 10
    assert res["batch"][:7] == o["strata"]["S1-app"][:7]           # follows the seeded order exactly


def test_stops_at_quota_and_test_path_cap_is_respected():
    res, batches, labels = _run(_order(), 30, lambda c: True)     # everything eligible
    assert res["stop"] == "quota reached" and res["counted"] == 30
    assert (res["eligible_app"], res["eligible_test"]) == (21, 9)        # three 7 + 3 batches
    assert res["test_cap"] == 10 and res["eligible_test"] <= res["test_cap"]
    assert all("S2" not in c["candidate_id"] for b in batches[1:] for c in b)   # S2 only in the first batch


def test_test_path_draws_stop_after_cap():
    res, batches, labels = _run(_order(), 30, lambda c: "S1-test" in c["candidate_id"] or int(c["candidate_id"][-4:]) % 3 == 0)
    test_issued = [cid for cid in labels if "S1-test" in cid]
    # once 10 eligible test-path sites exist, no further test-path candidate is issued
    elig = 0
    for b in batches:
        assert elig < 10 or not any("S1-test" in c["candidate_id"] for c in b)
        elig += sum("S1-test" in c["candidate_id"] for c in b)
    assert len(test_issued) >= 10


def test_candidate_cap_and_exhaustion_report_shortfalls():
    res, batches, labels = _run(_order(), 30, lambda c: False)    # nothing eligible
    assert res["stop"].startswith("candidate cap reached") and res["s1_issued"] == 120
    res2, _, _ = _run(_order(n_app=5, n_test=2, n_s2=0), 30, lambda c: False)
    assert res2["stop"].startswith("S1 exhausted")


def test_stopping_ignores_everything_but_eligibility():
    o = _order()
    a = next_batch(o, {c["candidate_id"]: True for c in o["strata"]["S1-app"][:5]}, 30)
    b = next_batch(o, {c["candidate_id"]: True for c in o["strata"]["S1-app"][:5]}, 30)
    assert a == b


def test_annotator_list_has_locations_only():
    o = _order()
    rows = annotator_list(o, next_batch(o, {}, 30)["batch"])
    assert all(set(r) == {"candidate_id", "repo", "commit", "file", "line"} for r in rows)


def test_cli_build_and_next(tmp_path, capsys):
    repo = _repo(tmp_path)
    out = tmp_path / "cand"
    assert C.main(["build", "--repo", str(repo), "--name", "demo", "--commit", "abc", "--run-dir", str(_run_dir(tmp_path, repo)),
                   "--out", str(out)]) == 0
    assert (out / "order_demo.json").exists() and (out / "pool_sources_demo.json").exists()
    assert C.main(["next", "--order", str(out / "order_demo.json"), "--quota", "30", "--out", str(tmp_path / "b.jsonl")]) == 0
    status = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert status["batch_size"] > 0 and status["stop"] is None
    rows = [json.loads(l) for l in (tmp_path / "b.jsonl").read_text().splitlines()]
    assert rows and "stratum" not in rows[0]
