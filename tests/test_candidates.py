"""Candidate pool and seeded sequential sampler (protocol v1.0.4 Sec. 2; decisions V2, V5, V6, V11; mismatches M1-M14
of docs/proposals/v1.0.4/rev3/R3_02_reconciliation.md Sec. 3)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

from pqscan.bench import candidates as C
from pqscan.bench.candidates import (SamplerError, annotator_list, build_pool, candidate_id, next_batch, order_pool,
                                     parse_eligibility, quota_for, scope_class, statement_starts)

ROOT = Path(__file__).resolve().parents[1]


def _repo(tmp: Path) -> Path:
    r = tmp / "demo"
    for d in ("pkg", "tests", "examples", "vendor/lib"):
        (r / d).mkdir(parents=True)
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
    (r / "examples" / "demo_sign.py").write_text(
        "from cryptography.hazmat.primitives.asymmetric import ec\nk = ec.generate_private_key(ec.SECP256R1())\n", encoding="utf-8")
    (r / "vendor" / "lib" / "x.py").write_text(
        "from Crypto.PublicKey import RSA\nk = RSA.generate(2048)\n", encoding="utf-8")
    return r


def _run_dir(tmp: Path, repo: Path) -> Path:
    d = tmp / "run"
    d.mkdir()
    findings = [{"file": str(repo / "pkg" / "keys.py"), "line": 5, "migration": "ML-DSA", "algorithm": "RSA", "context": "x"},
                {"file": "pkg/util.py", "line": 4, "migration": "SHA-3", "algorithm": "SHA256", "context": "hash"},
                {"file": "elsewhere/x.py", "line": 1, "migration": "", "algorithm": "RSA", "context": ""}]
    (d / "qsafe_demo.json").write_text(json.dumps({"findings": findings}), encoding="utf-8")
    return d


# ------------------------------------------------------------------ pool, regex, statements (unchanged behaviour)
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
    got = {(c["file"], c["line"]): (c["stratum"], c["scope"]) for c in pool}
    assert got[("pkg/keys.py", 4)] == ("S1-app", "app")        # regex line 4 + qsafe line 5 merged into one statement
    assert ("pkg/keys.py", 5) not in got
    assert got[("pkg/keys.py", 7)] == ("S1-app", "app")
    assert got[("tests/test_keys.py", 3)] == ("S1-nonapp", "test")
    assert got[("examples/demo_sign.py", 2)] == ("S1-nonapp", "example")
    assert got[("vendor/lib/x.py", 2)] == ("S1-nonapp", "vendored")
    assert got[("pkg/util.py", 4)] == ("S2", "app")             # tool-only, non-crypto file
    assert not any(f.startswith("elsewhere") for f, _ in got)
    assert sources["pkg/keys.py:4"] == ["qsafe", "regex"] and sources["pkg/keys.py:7"] == ["regex"]


def test_pool_without_tool_outputs_is_regex_only(tmp_path):
    pool, sources = build_pool(_repo(tmp_path), None, "demo")
    assert pool and all(s == ["regex"] for s in sources.values())


# ------------------------------------------------------------------ M1, M2: scope classes and strata (V5, V11)
@pytest.mark.parametrize("path,cls", [
    ("pkg/a.py", "app"), ("tests/a.py", "test"), ("pkg/testing/a.py", "test"), ("pkg/test/a.py", "test"),
    ("pkg/test_a.py", "test"), ("pkg/a_test.py", "test"), ("pkg/test.py", "test"), ("jwcrypto/tests.py", "test"),
    ("pkg/tests_rsa.py", "test"), ("pkg/tests-rsa.py", "test"), ("pkg/conftest.py", "test"),
    ("examples/a.py", "example"), ("example/a.py", "example"), ("demos/a.py", "example"), ("demo_app/a.py", "example"),
    ("vendor/a.py", "vendored"), ("pkg/_vendor/a.py", "vendored"), ("third_party/x/a.py", "vendored"),
    ("vendor/tests/test_a.py", "vendored"),          # precedence: vendored > test
    ("tests/examples/a.py", "test"),                 # test > example
    ("Tests/a.py", "test"),                          # names compared in lower case
    ("pkg/contest.py", "app"), ("pkg/attestation.py", "app"), ("pkg/latest.py", "app"), ("pkg/testimony/a.py", "app"),
])
def test_scope_classes_and_precedence(path, cls):
    assert scope_class(path) == cls


def test_strata_are_tool_independent():
    assert C.stratum_of("pkg/a.py", True) == "S1-app"
    assert C.stratum_of("tests/a.py", True) == "S1-nonapp"
    assert C.stratum_of("examples/a.py", False) == "S2"


# ------------------------------------------------------------------ M3: opaque IDs
def _order(n_app=200, n_non=100, n_s2=40, name="r"):
    pool = ([{"file": f"a{i}.py", "line": 1, "scope": "app", "stratum": "S1-app"} for i in range(n_app)]
            + [{"file": f"tests/t{i}.py", "line": 1, "scope": "test", "stratum": "S1-nonapp"} for i in range(n_non)]
            + [{"file": f"s{i}.py", "line": 1, "scope": "app", "stratum": "S2"} for i in range(n_s2)])
    return order_pool(pool, name, "abc")


def _stratum(o, cid):
    return next(s for s in C.STRATA if any(c["candidate_id"] == cid for c in o["strata"][s]))


def test_ids_are_opaque_deterministic_and_reveal_nothing():
    o = _order()
    ids = [c["candidate_id"] for s in C.STRATA for c in o["strata"][s]]
    assert all(re.fullmatch(r"C-[0-9a-f]{12}", i) for i in ids) and len(set(ids)) == len(ids)
    assert o["strata"]["S1-app"][0]["candidate_id"] == candidate_id(20261113, "r", o["strata"]["S1-app"][0]["file"], 1)
    assert not any(s in i for i in ids for s in ("S1", "S2", "app", "test", "r-"))
    assert candidate_id(20261113, "r", "a.py", 1) != candidate_id(20261113, "q", "a.py", 1)


def test_id_collision_or_duplicate_pool_entry_stops_the_build(monkeypatch):
    monkeypatch.setattr(C, "candidate_id", lambda seed, repo, f, ln: "C-000000000000")
    with pytest.raises(SamplerError, match="collision"):
        order_pool([{"file": "a.py", "line": 1, "scope": "app", "stratum": "S1-app"},
                    {"file": "b.py", "line": 1, "scope": "app", "stratum": "S1-app"}], "r", "abc")


def test_order_is_seeded_reproducible_and_complete():
    pool = [{"file": f"f{i}.py", "line": 1, "scope": "app", "stratum": "S1-app"} for i in range(50)]
    a, b = order_pool(pool, "r", "abc"), order_pool(list(reversed(pool)), "r", "abc")
    assert a == b and a["format"] == C.ORDER_FORMAT and a["protocol"] == "1.0.4"
    c = order_pool(pool, "r", "abc", seed=1)
    assert [x["file"] for x in c["strata"]["S1-app"]] != [x["file"] for x in a["strata"]["S1-app"]]
    assert sorted(x["file"] for x in a["strata"]["S1-app"]) == sorted(p["file"] for p in pool)
    assert a["counts"] == {"S1-app": 50, "S1-nonapp": 0, "S2": 0} and len(a["pool_sha256"]) == 64


# ------------------------------------------------------------------ sequential issuance helpers
def _run(order, quota, is_eligible):
    issued, labels, batches = [], {}, []
    while True:
        res = next_batch(order, issued, labels, quota)
        if res["stop"]:
            return res, batches, labels
        batches.append((res["batch_kind"], res["batch"]))
        for c in res["batch"]:
            issued.append(c["candidate_id"])
            labels[c["candidate_id"]] = is_eligible(c)


# ------------------------------------------------------------------ M4: B0 separate, once
def test_b0_is_ten_s2_issued_once_before_b1():
    o = _order()
    res = next_batch(o, [], {}, 30)
    assert res["batch_kind"] == "B0" and res["batch"] == o["strata"]["S2"][:10]
    _, batches, _ = _run(o, 30, lambda c: True)
    assert batches[0][0] == "B0" and all(k == "B1+" for k, _ in batches[1:])
    assert all(_stratum(o, c["candidate_id"]) != "S2" for _, b in batches[1:] for c in b)


def test_no_s2_means_no_b0():
    o = _order(n_s2=0)
    assert next_batch(o, [], {}, 30)["batch_kind"] == "B1+"


# ------------------------------------------------------------------ M5, M6, M7, M8: composition and cap
def test_first_b1_is_7_app_and_3_nonapp_in_seeded_order():
    o = _order()
    b0 = [c["candidate_id"] for c in o["strata"]["S2"][:10]]
    res = next_batch(o, b0, {c: False for c in b0}, 30)
    kinds = [_stratum(o, c["candidate_id"]) for c in res["batch"]]
    assert kinds.count("S1-app") == 7 and kinds.count("S1-nonapp") == 3
    assert res["batch"][:7] == o["strata"]["S1-app"][:7]


def test_nonapp_per_batch_is_min_3_and_remaining_cap():
    o = _order()
    _, batches, labels = _run(o, 30, lambda c: _stratum(o, c["candidate_id"]) == "S1-nonapp")   # only non-app eligible
    e_non = 0
    for kind, b in batches[1:]:
        n_non = sum(_stratum(o, c["candidate_id"]) == "S1-nonapp" for c in b)
        assert n_non <= min(3, 10 - e_non)                       # cap = 30 // 3 = 10
        e_non += n_non
    assert e_non == 10                                           # never more eligible non-app than the cap


def test_app_exhausted_fills_from_nonapp_but_never_past_the_remaining_cap():
    o = _order(n_app=3, n_non=100, n_s2=0)
    res = next_batch(o, [], {}, 30)
    kinds = [_stratum(o, c["candidate_id"]) for c in res["batch"]]
    assert kinds.count("S1-app") == 3 and kinds.count("S1-nonapp") == 7     # 7 <= remaining cap 10
    issued = [c["candidate_id"] for c in res["batch"]]
    labels = {c: True for c in issued}                                        # 7 eligible non-app -> remaining cap 3
    res2 = next_batch(o, issued, labels, 30)
    assert len(res2["batch"]) == 3 and all(_stratum(o, c["candidate_id"]) == "S1-nonapp" for c in res2["batch"])


def test_counted_formula_and_quota_stop():
    res, batches, _ = _run(_order(), 30, lambda c: True)
    assert res["stop"] == "quota reached" and res["counted"] == 30
    assert res["nonapp_cap"] == 10 and res["eligible_nonapp"] <= 10
    assert res["counted"] == res["eligible_app"] + min(res["eligible_nonapp"], 10)


@pytest.mark.parametrize("quota,cap", [(30, 10), (25, 8)])
def test_cap_is_quota_floor_third(quota, cap):
    o = _order(n_s2=0)
    assert next_batch(o, [], {}, quota)["nonapp_cap"] == cap


# ------------------------------------------------------------------ M9, M14: shortfalls, unresolved
def test_candidate_cap_and_exhaustion_report_shortfalls():
    res, _, _ = _run(_order(), 30, lambda c: False)
    assert res["stop"].startswith("candidate cap reached") and res["s1_issued"] == 120
    res2, _, _ = _run(_order(n_app=5, n_non=2, n_s2=0), 30, lambda c: False)
    assert res2["stop"].startswith("S1 exhausted")


def test_unresolved_eligibility_counts_as_not_eligible():
    o = _order(n_s2=0)
    first = [c["candidate_id"] for c in next_batch(o, [], {}, 30)["batch"]]
    res = next_batch(o, first, {c: "unresolved" for c in first}, 30)
    assert res["counted"] == 0 and res["unresolved"] == 10


# ------------------------------------------------------------------ M10: quota constant
def test_quota_constant_equals_the_adopted_protocol_table():
    proto = (ROOT / "docs/specification/evaluation_protocol.md").read_text(encoding="utf-8")
    rows = dict(re.findall(r"^\| (test|development|validation) \| \d+ \| (\d+) \|", proto, re.M))
    assert {k: int(v) for k, v in rows.items()} == C.QUOTAS
    assert quota_for("test") == 30 and quota_for("development") == 25
    with pytest.raises(SamplerError):
        quota_for("development", 20)                    # override without a reason
    assert quota_for("development", 20, "owner decision 2026-xx") == 20
    with pytest.raises(SamplerError):
        quota_for("dev")


# ------------------------------------------------------------------ M12, M13: strict inputs
@pytest.mark.parametrize("bad", ["false", "true", 0, 1, None, "yes", "Unresolved"])
def test_eligibility_must_be_json_boolean_or_unresolved(bad):
    with pytest.raises(SamplerError):
        parse_eligibility(bad)
    o = _order(n_s2=0)
    first = [c["candidate_id"] for c in next_batch(o, [], {}, 30)["batch"]]
    with pytest.raises(SamplerError):
        next_batch(o, first, {c: bad for c in first}, 30)


def test_unknown_duplicate_unissued_and_unlabelled_ids_are_rejected():
    o = _order(n_s2=0)
    first = [c["candidate_id"] for c in next_batch(o, [], {}, 30)["batch"]]
    with pytest.raises(SamplerError, match="unknown"):
        next_batch(o, first + ["C-ffffffffffff"], {c: True for c in first}, 30)
    with pytest.raises(SamplerError, match="duplicate"):
        next_batch(o, first + first[:1], {c: True for c in first}, 30)
    with pytest.raises(SamplerError, match="never issued"):
        next_batch(o, first[:5], {c: True for c in first}, 30)
    with pytest.raises(SamplerError, match="no final label"):
        next_batch(o, first, {c: True for c in first[:5]}, 30)


def test_old_order_format_is_refused():
    o = _order()
    o.pop("format")
    with pytest.raises(SamplerError, match="format"):
        next_batch(o, [], {}, 30)


# ------------------------------------------------------------------ stopping depends only on eligibility
def test_stopping_ignores_everything_but_eligibility():
    o = _order(n_s2=0)
    ids = [c["candidate_id"] for c in o["strata"]["S1-app"][:5]]
    assert next_batch(o, ids, {c: True for c in ids}, 30) == next_batch(o, ids, {c: True for c in ids}, 30)


def test_annotator_list_has_locations_only():
    o = _order()
    rows = annotator_list(o, next_batch(o, [], {}, 30)["batch"])
    assert all(set(r) == {"candidate_id", "repo", "commit", "file", "line"} for r in rows)


def test_final_label_reader_handles_envelopes_and_unresolved(tmp_path):
    f = tmp_path / "final.jsonl"
    f.write_text("\n".join(json.dumps(x) for x in [
        {"site": {"eligible": True}, "meta": {"candidate_id": "C-1"}},
        {"site": {"eligible": False}, "meta": {"candidate_id": "C-2", "unresolved": ["eligible"]}},
        {"candidate_id": "C-3", "eligible": "false"}]) + "\n", encoding="utf-8")
    got = C.read_final_eligibility(f)
    assert got == {"C-1": True, "C-2": "unresolved", "C-3": "false"}        # raw: "false" is refused later (M12)
    with pytest.raises(SamplerError):
        parse_eligibility(got["C-3"])


# ------------------------------------------------------------------ CLI
def test_cli_build_and_next(tmp_path, capsys):
    repo = _repo(tmp_path)
    out = tmp_path / "cand"
    assert C.main(["build", "--repo", str(repo), "--name", "demo", "--commit", "abc", "--run-dir", str(_run_dir(tmp_path, repo)),
                   "--out", str(out)]) == 0
    assert (out / "order_demo.json").exists() and (out / "pool_sources_demo.json").exists()
    assert C.main(["next", "--order", str(out / "order_demo.json"), "--split", "test", "--out", str(tmp_path / "b.jsonl")]) == 0
    status = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert status["batch_size"] > 0 and status["stop"] is None and status["quota"] == 30
    rows = [json.loads(l) for l in (tmp_path / "b.jsonl").read_text().splitlines()]
    assert rows and "stratum" not in rows[0] and "scope" not in rows[0]
    with pytest.raises(SamplerError):
        C.main(["next", "--order", str(out / "order_demo.json"), "--split", "test", "--quota-override", "5"])


# ------------------------------------------------------------------ committed development/validation orders
ORDERS = sorted((ROOT / "benchmark" / "candidates").glob("[dv]*/order_*.json"))


@pytest.mark.parametrize("path", ORDERS, ids=lambda p: p.stem)
def test_committed_orders_are_v2_opaque_and_scope_consistent(path):
    o = json.loads(path.read_text(encoding="utf-8"))
    assert o["format"] == C.ORDER_FORMAT and o["protocol"] == "1.0.4" and o["seed"] == 20261113
    ids = [c["candidate_id"] for s in C.STRATA for c in o["strata"][s]]
    assert len(ids) == len(set(ids)) and all(re.fullmatch(r"C-[0-9a-f]{12}", i) for i in ids)
    for s in ("S1-app", "S1-nonapp"):
        for c in o["strata"][s]:
            assert (scope_class(c["file"]) == "app") == (s == "S1-app") and c["scope"] == scope_class(c["file"])
            assert c["candidate_id"] == candidate_id(o["seed"], o["repo"], c["file"], c["line"])
    assert o["counts"] == {s: len(o["strata"][s]) for s in C.STRATA}


def test_six_dv_orders_exist():
    assert len(ORDERS) == 6


@pytest.mark.skipif(not (ROOT / ".cache/repos/validation/latchset__jwcrypto").exists(), reason="pinned checkout not present")
def test_rebuild_reproduces_committed_order(tmp_path):
    m = json.loads((ROOT / "benchmark/real/manifest.json").read_text(encoding="utf-8"))
    commit = next(r["commit"] for r in m["splits"]["validation"] if r["repo"] == "latchset/jwcrypto")
    run = ROOT / "runs/validation/run1"
    assert C.main(["build", "--repo", str(ROOT / ".cache/repos/validation/latchset__jwcrypto"), "--name", "latchset__jwcrypto",
                   "--commit", commit, "--run-dir", str(run) if run.exists() else str(tmp_path), "--out", str(tmp_path)]) == 0
    if run.exists():
        assert (tmp_path / "order_latchset__jwcrypto.json").read_bytes() == \
            (ROOT / "benchmark/candidates/validation/order_latchset__jwcrypto.json").read_bytes()
