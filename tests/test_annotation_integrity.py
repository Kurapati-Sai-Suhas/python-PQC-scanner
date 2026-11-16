"""Annotation-integrity tooling (R4-19 items 3-7): ledger, strict validation, packets, AI records, comparison,
adjudication and the workflow CLI. No real annotation is performed; all labels here are test fixtures."""
from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

import pytest

from pqscan.bench import annotate as AN
from pqscan.bench import candidates as C
from pqscan.bench import ledger as L
from pqscan.bench import packets as P
from pqscan.bench import review as R
from pqscan.bench.labels import LabelError, annotator_added_id, eligibility_of, validate_file, validate_record

CID = "C-0123456789ab"


def site(cid=CID, **kw):
    s = {"site_id": cid, "dataset": "real-dev", "repo": "demo", "commit": "abcdef1", "file": "pkg/keys.py",
         "line_start": 4, "line_end": 4, "library": "pyca", "algorithm": "RSA", "api_call": "rsa.generate_private_key",
         "key_provenance": "generated", "gt_role": "SIGN", "assessability": "DETERMINATE", "eligible": True,
         "hybrid_component": False, "scope": "app", "obvious_from_name": False, "evidence_needed": "downstream-usage",
         "evidence_scope": "function"}
    s.update(kw)
    return s


def meta(cid=CID, kind="primary", **kw):
    m = {"candidate_id": cid, "annotator": "owner", "label_kind": kind, "submitted_utc": "2026-11-16T10:00:00Z",
         "evidence_lines": ["pkg/keys.py:4", "pkg/keys.py:7"], "rationale": "key reaches sign only",
         "ambiguity": "none"}
    if kind in ("primary", "packet_first"):
        m.update(context_used="packet_sufficient", time_seconds=120)
    m.update(kw)
    return m


def env(**kw):
    return {"site": site(**kw.pop("site", {})), "meta": meta(**kw)}


# ------------------------------------------------------------------ ledger (item 3)
def test_ledger_chain_order_and_tamper_detection(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    f = tmp_path / "primary.jsonl"
    f.write_text("x\n", encoding="utf-8")
    L.append(lp, step="issue", repo="r", phase="DV", batch="B0", candidates=["C-1", "C-2"], utc="2026-11-16T00:00:00Z")
    with pytest.raises(L.LedgerError, match="not allowed"):
        L.append(lp, step="ai_review", repo="r", phase="DV", batch="B0", file=f)          # out of order
    for step in ("primary", "ai_review", "compare", "adjudication"):
        L.append(lp, step=step, repo="r", phase="DV", batch="B0", file=f)
    L.append(lp, step="issue", repo="r", phase="DV", batch="B1", candidates=["C-3"])
    recs = L.read(lp)
    L.verify(recs)
    assert L.issued_ids(recs) == ["C-1", "C-2", "C-3"] and L.open_batch(recs) == ("B1", "issue")
    # tamper: edit one byte of an earlier record
    lines = lp.read_text(encoding="utf-8").splitlines()
    lines[1] = lines[1].replace('"primary"', '"primary "')
    lp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(L.LedgerError):
        L.verify(L.read(lp))


def test_ledger_rejects_reissue_duplicate_steps_wrong_batch_and_deletion(tmp_path):
    lp = tmp_path / "l.jsonl"
    f = tmp_path / "f.txt"
    f.write_text("a", encoding="utf-8")
    L.append(lp, step="issue", repo="r", phase="DV", batch="B0", candidates=["C-1"])
    with pytest.raises(L.LedgerError):
        L.append(lp, step="issue", repo="r", phase="DV", batch="B1", candidates=["C-2"])  # previous batch open
    L.append(lp, step="primary", repo="r", phase="DV", batch="B0", file=f)
    with pytest.raises(L.LedgerError):
        L.append(lp, step="primary", repo="r", phase="DV", batch="B0", file=f)            # duplicate step
    with pytest.raises(L.LedgerError):
        L.append(lp, step="ai_review", repo="r", phase="DV", batch="B9", file=f)          # wrong batch
    for s in ("ai_review", "compare", "adjudication"):
        L.append(lp, step=s, repo="r", phase="DV", batch="B0", file=f)
    with pytest.raises(L.LedgerError, match="issued twice"):
        L.append(lp, step="issue", repo="r", phase="DV", batch="B1", candidates=["C-1"])
    with pytest.raises(L.LedgerError):
        L.append(lp, step="issue", repo="other", phase="DV", batch="B1", candidates=["C-9"])  # one repo per ledger
    lines = lp.read_text(encoding="utf-8").splitlines()
    lp.write_text("\n".join(lines[:1] + lines[2:]) + "\n", encoding="utf-8")          # delete a record
    with pytest.raises(L.LedgerError):
        L.verify(L.read(lp))


def test_ledger_holds_hashes_not_content(tmp_path):
    lp = tmp_path / "l.jsonl"
    f = tmp_path / "primary.jsonl"
    f.write_text(json.dumps(env()) + "\n", encoding="utf-8")
    L.append(lp, step="issue", repo="r", phase="DV", batch="B0", candidates=[CID])
    L.append(lp, step="primary", repo="r", phase="DV", batch="B0", file=f)
    text = lp.read_text(encoding="utf-8")
    assert "SIGN" not in text and "key reaches sign" not in text and L.file_sha256(f) in text
    L.check_file(f, L.read(lp), "primary", "B0")
    f.write_text("changed\n", encoding="utf-8")
    with pytest.raises(L.LedgerError, match="differs"):
        L.check_file(f, L.read(lp), "primary", "B0")


# ------------------------------------------------------------------ strict validation (item 4)
def test_valid_primary_record_passes():
    assert validate_record(env(), "primary") == []


@pytest.mark.parametrize("field,bad", [("eligible", "false"), ("hybrid_component", "no"), ("obvious_from_name", 0)])
def test_booleans_must_be_json_booleans(field, bad):
    assert any(field in e for e in validate_record(env(site={field: bad}), "primary"))


def test_schema_rules_enforced():
    assert validate_record(env(site={"gt_role": "UNKNOWN", "assessability": "INDETERMINATE"}), "primary")  # possible_roles missing
    assert validate_record(env(site={"eligible": False}), "primary")                   # ineligible must be NONE
    assert validate_record(env(context_used="extended"), "primary")                     # context_extra required
    assert validate_record(env(context_used="extended", context_extra=["pkg/a.py:1-9"]), "primary") == []
    assert validate_record(env(evidence_lines=[]), "primary")                           # eligible needs evidence
    assert validate_record(env(unresolved=["gt_role"]), "primary")                      # reason required
    assert validate_record(env(site={"site_id": "C-ffffffffffff"}), "primary")          # ids must match
    assert validate_record(env(kind="final"), "primary")                                 # wrong kind
    assert validate_record({"site": site()}, "primary")                                  # envelope


def test_file_validation_issued_unknown_duplicate_and_annotator_added(tmp_path):
    other = "C-ba9876543210"
    added = annotator_added_id("demo", "pkg/keys.py", 30)
    f = tmp_path / "p.jsonl"
    recs = [env(), env(cid=other, site={"site_id": other}), env(cid=added, site={"site_id": added}, annotator_added=True)]
    f.write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
    assert len(validate_file(f, "primary", issued=[CID, other])) == 3
    with pytest.raises(LabelError, match="not labelled"):
        validate_file(f, "primary", issued=[CID, other, "C-111111111111"])
    with pytest.raises(LabelError, match="unknown candidate"):
        validate_file(f, "primary", issued=[CID])
    f.write_text("".join(json.dumps(r) + "\n" for r in recs + recs[:1]), encoding="utf-8")
    with pytest.raises(LabelError, match="duplicate"):
        validate_file(f, "primary", issued=[CID, other])


def test_eligibility_of_final_records():
    assert eligibility_of(env(kind="final")) is True
    assert eligibility_of(env(kind="final", unresolved=["eligible"], unresolved_reason="x")) == "unresolved"


# ------------------------------------------------------------------ packets (item 5)
SRC = (
    "from cryptography.hazmat.primitives.asymmetric import rsa, padding\n"
    "from cryptography.hazmat.primitives import hashes\n"
    "\n"
    "class Signer:\n"
    "    def __init__(self):\n"
    "        self.k = rsa.generate_private_key(public_exponent=65537, key_size=3072)\n"
    "\n"
    "    def sign(self, d):\n"
    "        return self.k.sign(d, padding.PKCS1v15(), hashes.SHA256())\n"
    "\n"
    "def helper():\n"
    "    return Signer().sign(b'x')\n"
    "\n"
    "def caller():\n"
    "    return helper()\n")


def _repo(tmp_path):
    r = tmp_path / "repo"
    (r / "pkg").mkdir(parents=True)
    (r / "pkg" / "keys.py").write_text(SRC, encoding="utf-8")
    (r / "pkg" / "broken.py").write_text("def (:\n    rsa.generate_private_key()\n", encoding="utf-8")
    (r / "pkg" / "noisy.py").write_text("# generated by semgrep\nfrom cryptography import x\nk = x.load_pem_private_key(b'')\n", encoding="utf-8")
    return r


def test_packet_contains_imports_class_and_marked_line(tmp_path):
    repo = _repo(tmp_path)
    pk = P.build_packet(repo, "pkg/keys.py", 6, CID)
    t = pk["text"]
    assert pk["rule"] == "packet-v1" and len(pk["sha256"]) == 64
    assert "--- Imports ---" in t and "--- Enclosing class ---" in t
    assert ">>  6 |         self.k = rsa.generate_private_key" in t
    assert P.build_packet(repo, "pkg/keys.py", 6, CID) == pk          # deterministic


def test_packet_at_function_level_includes_same_file_callers(tmp_path):
    t = P.build_packet(_repo(tmp_path), "pkg/keys.py", 12, CID)["text"]
    assert "--- Enclosing function ---" in t and "Callers of helper in this file" in t and "def caller" in t


def test_packet_for_unparseable_file_uses_a_window(tmp_path):
    pk = P.build_packet(_repo(tmp_path), "pkg/broken.py", 2, CID)
    assert "--- Line window ---" in pk["text"] and "does not parse" in pk["text"]


def test_forbidden_content_never_added_and_source_tokens_reported(tmp_path):
    repo = _repo(tmp_path)
    for f, ln in (("pkg/keys.py", 6), ("pkg/keys.py", 12), ("pkg/broken.py", 2)):
        pk = P.build_packet(repo, f, ln, CID)
        assert P._forbidden_in(pk["text"]) == [] and pk["warnings"] == []
    noisy = P.build_packet(repo, "pkg/noisy.py", 3, CID)
    assert noisy["warnings"] and "semgrep" in noisy["warnings"][0]            # reported, not edited
    assert "generated by semgrep" in noisy["text"]


def test_forbidden_matching_uses_word_boundaries():
    assert P._forbidden_in("import hypothesis\nv = 'ch2a9f'\n") == []
    assert P._forbidden_in("run PQSCAN then qsafe") == ["pqscan", "qsafe"]


def test_packet_first_is_seeded_deterministic_and_near_rate():
    ids = [C.candidate_id(20261113, "r", f"f{i}.py", 1) for i in range(5000)]
    dv = [P.packet_first(i, "DV") for i in ids]
    assert dv == [P.packet_first(i, "DV") for i in ids]
    assert abs(sum(dv) / len(ids) - P.packet_first_rate("DV")) < 0.02
    assert P.packet_first_rate("DV") * P.PLANNED_CANDIDATES["DV"] >= 50 and P.packet_first_rate("T") == 0.10
    with pytest.raises(ValueError):
        P.packet_first_rate("pilot")


# ------------------------------------------------------------------ AI records, comparison, adjudication (items 6-7)
def _identity(tmp_path):
    p = tmp_path / "ident.json"
    p.write_text(json.dumps({"interface_or_api": "ChatGPT web, Temporary Chat", "model": "TEST-MODEL",
                             "recorded_utc": "2026-11-16T09:00:00Z", "isolation": "temporary chat; memory off"}), encoding="utf-8")
    return p


def test_prompt_refused_without_identity_and_free_of_forbidden_content(tmp_path):
    with pytest.raises(R.ReviewError, match="V8"):
        R.build_prompt([], identity_path=tmp_path / "none.json")
    tmpl = R.prompt_template()
    assert P._forbidden_in(tmpl) == [] and "Step A" in tmpl and "Required evidence" in tmpl
    text, sha = R.build_prompt([{"text": "PACKET"}], identity_path=_identity(tmp_path))
    assert text.endswith("PACKET\n") and sha == R.template_sha256() and len(sha) == 64


def _ai_line(cid=CID, **kw):
    o = {"candidate_id": cid, "status": "ok", "eligible": True, "gt_role": "SIGN", "assessability": "DETERMINATE",
         "hybrid_component": False, "obvious_from_name": False, "evidence_needed": "downstream-usage",
         "key_provenance": "generated", "ambiguity": "none", "evidence_lines": ["pkg/keys.py:4"], "rationale": "r"}
    o.update(kw)
    return json.dumps({k: v for k, v in o.items() if v is not ...})


def test_ai_parser_never_fills_fields(tmp_path):
    ident = json.loads(_identity(tmp_path).read_text())
    packets = [{"candidate_id": CID, "sha256": "a" * 64}, {"candidate_id": "C-ba9876543210", "sha256": "b" * 64}]
    raw = "Here you go:\n" + _ai_line(key_provenance=...) + "\n" + _ai_line("C-ba9876543210", rationale=...) + "\n" + _ai_line("C-zzz")
    res = R.parse_ai_response(raw, packets, ident, datetime_utc="2026-11-16T11:00:00Z", prompt_sha256="c" * 64)
    assert len(res["records"]) == 1
    r = res["records"][0]
    assert "key_provenance" not in r["site"] and r["missing_fields"] == ["key_provenance", "possible_roles"]
    assert r["meta"]["ai"]["packet_sha256"] == "a" * 64 and r["meta"]["ai"]["model"] == "TEST-MODEL"
    assert any("incomplete" in p for p in res["problems"]) and any("unknown candidate" in p for p in res["problems"])
    assert res["absent"] == ["C-ba9876543210"]


def _ai_rec(**kw):
    ident = {"interface_or_api": "x", "model": "m"}
    raw = _ai_line(**kw)
    return R.parse_ai_response(raw, [{"candidate_id": CID, "sha256": "a" * 64}], ident,
                               datetime_utc="2026-11-16T11:00:00Z", prompt_sha256="c" * 64)["records"][0]


def test_compare_counts_insufficient_and_treats_role_sets_as_sets():
    prim = [env(site={"gt_role": "UNKNOWN", "assessability": "INDETERMINATE", "possible_roles": ["SIGN", "PK_DECRYPT"]})]
    ai = [_ai_rec(gt_role="UNKNOWN", assessability="INDETERMINATE", possible_roles=["PK_DECRYPT", "SIGN"],
                  key_provenance="parameter")]
    res = R.compare(prim, ai)
    assert [(d["field"]) for d in res["disagreements"]] == ["key_provenance"]
    assert R.compare(prim, [_ai_rec(status="insufficient_context", gt_role="NONE")])["insufficient_context"] == [CID]
    assert R.compare(prim, [])["not_reviewed"] == [CID]


def _adj(rows):
    return [{"candidate_id": CID, "field": f, "final_value": v, "reason": "checked the consumer", "category": c,
             "context_difference": cd} for f, v, c, cd in rows]


def test_adjudication_rules_and_final_labels():
    prim = [env()]
    dis = R.compare(prim, [_ai_rec(key_provenance="parameter", gt_role="VERIFY")])["disagreements"]
    assert {d["field"] for d in dis} == {"key_provenance", "gt_role"}
    with pytest.raises(R.ReviewError, match="not adjudicated"):
        R.adjudicate(prim, dis, _adj([("gt_role", '"SIGN"', "kept", "false")]))
    with pytest.raises(R.ReviewError, match="must keep"):
        R.adjudicate(prim, dis, _adj([("gt_role", '"VERIFY"', "kept", "false"), ("key_provenance", '"generated"', "kept", "false")]))
    with pytest.raises(R.ReviewError, match="not a disagreement"):
        R.adjudicate(prim, dis, _adj([("gt_role", '"SIGN"', "kept", "false"), ("key_provenance", '"generated"', "kept", "false"),
                                       ("eligible", "true", "kept", "false")]))
    finals = R.adjudicate(prim, dis, _adj([("gt_role", '"SIGN"', "kept", "false"),
                                            ("key_provenance", '"parameter"', "adopted_ai", "true")]))
    assert finals[0]["site"]["key_provenance"] == "parameter" and finals[0]["meta"]["label_kind"] == "final"
    unres = R.adjudicate(prim, dis, _adj([("gt_role", "", "unresolved", "false"), ("key_provenance", '"generated"', "kept", "false")]))
    assert unres[0]["meta"]["unresolved"] == ["gt_role"] and unres[0]["site"]["gt_role"] == "SIGN"
    rep = R.unresolved_report(unres)
    assert rep["with_unresolved_field"] == 1 and rep["flag_over_5_percent"]


# ------------------------------------------------------------------ workflow CLI end-to-end (fixtures only)
def _fake_root(tmp_path):
    root = tmp_path / "root"
    repo = root / ".cache" / "repos" / "development" / "demo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "keys.py").write_text(SRC, encoding="utf-8")
    pool = [{"file": "pkg/keys.py", "line": ln, "scope": "app", "stratum": "S1-app"} for ln in (6, 9, 12)]
    order = C.order_pool(pool, "demo", "abcdef1")
    od = root / "benchmark" / "candidates" / "development"
    od.mkdir(parents=True)
    (od / "order_demo.json").write_text(json.dumps(order), encoding="utf-8")
    (root / "docs" / "benchmark").mkdir(parents=True)
    return root, order


def test_workflow_cli_end_to_end(tmp_path, monkeypatch, capsys):
    root, order = _fake_root(tmp_path)
    monkeypatch.setattr(R, "IDENTITY", _identity(tmp_path))
    run = lambda *args: (AN.main(list(args), root=root), json.loads(capsys.readouterr().out.strip().splitlines()[-1]))[1]
    out = run("issue", "--phase", "DV", "--split", "development", "--repo", "demo")
    assert out["batch"] == "B1" and out["candidates"] == 3 and out["warnings"] == []
    work = root / "benchmark" / "annotation" / "DV" / "demo"
    todo = [json.loads(x) for x in (work / "todo_demo_B1.jsonl").read_text().splitlines()]
    with pytest.raises(SystemExit):                      # cannot issue again while B1 is open
        AN.main(["issue", "--phase", "DV", "--split", "development", "--repo", "demo"], root=root)
    prim = tmp_path / "my_primary.jsonl"
    prim.write_text("".join(json.dumps({"site": site(t["candidate_id"], line_start=t["line"], line_end=t["line"]),
                                        "meta": meta(t["candidate_id"])}) + "\n" for t in todo), encoding="utf-8")
    if any(t["packet_first"] for t in todo):
        pf = tmp_path / "pf.jsonl"
        pf.write_text("".join(json.dumps({"site": site(t["candidate_id"]), "meta": meta(t["candidate_id"], "packet_first")}) + "\n"
                              for t in todo if t["packet_first"]), encoding="utf-8")
        run("primary", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--file", str(pf), "--packet-first")
    assert run("primary", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--file", str(prim))["step"] == "primary"
    assert Path(run("prompt", "--phase", "DV", "--repo", "demo", "--batch", "B1")["prompt"]).exists()
    raw = tmp_path / "raw.txt"
    raw.write_text("\n".join(_ai_line(t["candidate_id"], gt_role="VERIFY" if i == 0 else "SIGN") for i, t in enumerate(todo)), encoding="utf-8")
    assert run("ai", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--response", str(raw), "--utc", "2026-11-16T12:00:00Z")["records"] == 3
    assert run("compare", "--phase", "DV", "--repo", "demo", "--batch", "B1")["disagreements"] == 1
    adj = tmp_path / "adj.csv"
    with adj.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["candidate_id", "field", "final_value", "reason", "category", "context_difference"])
        w.writeheader()
        w.writerow({"candidate_id": todo[0]["candidate_id"], "field": "gt_role", "final_value": '"SIGN"', "reason": "sign call",
                    "category": "kept", "context_difference": "false"})
    assert run("adjudicate", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--adjudication", str(adj))["final_records"] == 3
    st = run("status", "--phase", "DV", "--repo", "demo")
    assert st["last_step"] == "adjudication" and st["issued"] == 3
    L.verify(L.read(root / "benchmark" / "ledger" / "DV" / "ledger_demo.jsonl"))
    # all 3 eligible -> the next issue reports the pool exhausted (only 3 S1 candidates exist)
    assert run("issue", "--phase", "DV", "--split", "development", "--repo", "demo")["stop"].startswith("S1 exhausted")


def test_test_phase_refused_before_f1(tmp_path):
    root, _ = _fake_root(tmp_path)
    with pytest.raises(SystemExit, match="F1"):
        AN.main(["issue", "--phase", "T", "--split", "test", "--repo", "demo"], root=root)
