"""Pilot and synthetic validation loops (pqscan/bench/loops.py; annotate phases `pilot` and `synthetic`).

No real annotation is performed: every label here is a test fixture written to a temporary root. The real pilot and
synthetic item lists are only read (locations), never labelled. Checks: location-only issuance, synthetic blinding
(opaque names, neutralised generator header, unchanged line numbers), ledger integrity, the reference comparison gate,
and that the DV / T workflows keep their safeguards.
"""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pytest

from pqscan.bench import annotate as AN
from pqscan.bench import ledger as L
from pqscan.bench import loops as LP
from pqscan.bench import packets as P
from pqscan.bench import review as R

ROOT = Path(__file__).resolve().parents[1]
ITEM_KEYS = {"candidate_id", "repo", "commit", "file", "line"}
PILOT_COMMIT = "0e9ccb91e0f9a68f2587233d523ad7fe46e730fe"


def _base_cases() -> list[str]:
    return sorted(json.loads((ROOT / "benchmark/synthetic/manifest.json").read_text(encoding="utf-8"))["split"])


def _identity(tmp_path):
    p = tmp_path / "ident.json"
    p.write_text(json.dumps({"interface_or_api": "TEST interface", "model": "TEST-MODEL",
                             "recorded_utc": "2026-11-18T09:00:00Z", "isolation": "test fixture"}), encoding="utf-8")
    return p


def _syn_root(tmp_path) -> Path:
    root = tmp_path / "root"
    dst = root / "benchmark" / "synthetic"
    dst.mkdir(parents=True)
    for f in ("manifest.json", "sites.jsonl", "validation_subset.csv"):
        shutil.copy(ROOT / "benchmark/synthetic" / f, dst / f)
    shutil.copytree(ROOT / "benchmark/synthetic/cases", dst / "cases")
    return root


def _pilot_root(tmp_path) -> Path:
    root = tmp_path / "root"
    (root / "docs" / "pilot").mkdir(parents=True)
    (root / "docs/pilot/pilot_manifest.json").write_text(json.dumps(
        {"pilot_repositories": {"paramiko": {"url": "https://example.invalid/p", "commit": PILOT_COMMIT}}}), encoding="utf-8")
    header = (ROOT / "docs/pilot/h1_pilot_sites.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
    rows = [{"site_id": "P01", "repo": "paramiko", "file": "pkg/keys.py", "line_start": "5", "line_end": "5",
             "eligible": "yes", "gt_role": "SIGN", "assessability": "DETERMINATE", "possible_roles": "",
             "hybrid_component": "no", "obvious_from_name": "no", "evidence_needed": "downstream-usage",
             "key_provenance": "generated"},
            {"site_id": "P02", "repo": "paramiko", "file": "pkg/keys.py", "line_start": "6", "line_end": "6",
             "eligible": "yes", "gt_role": "SIGN", "assessability": "DETERMINATE", "possible_roles": "",
             "hybrid_component": "no", "obvious_from_name": "yes", "evidence_needed": "none", "key_provenance": "generated"}]
    with (root / "docs/pilot/h1_pilot_sites.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in header})
    src = root / ".cache" / "repos" / "paramiko" / "pkg"
    src.mkdir(parents=True)
    (src / "keys.py").write_text("from cryptography.hazmat.primitives.asymmetric import rsa, padding\n"
                                 "from cryptography.hazmat.primitives import hashes\n\n"
                                 "def make(data):\n"
                                 "    k = rsa.generate_private_key(public_exponent=65537, key_size=3072)\n"
                                 "    return k.sign(data, padding.PKCS1v15(), hashes.SHA256())\n", encoding="utf-8")
    return root


def _label(t, dataset, file=None, **kw):
    s = {"site_id": t["candidate_id"], "dataset": dataset, "repo": t["repo"], "commit": t["commit"],
         "file": file or t["file"], "line_start": t["line"], "line_end": t["line"], "library": "pyca", "algorithm": "RSA",
         "api_call": "rsa.generate_private_key", "key_provenance": "generated", "gt_role": "SIGN",
         "assessability": "DETERMINATE", "eligible": True, "hybrid_component": False, "scope": "app",
         "obvious_from_name": False, "evidence_needed": "downstream-usage", "evidence_scope": "function"}
    s.update(kw)
    m = {"candidate_id": t["candidate_id"], "annotator": "owner", "label_kind": "primary",
         "submitted_utc": "2026-11-18T10:00:00Z", "evidence_lines": [f"{s['file']}:{t['line']}"], "rationale": "fixture",
         "ambiguity": "none", "context_used": "packet_sufficient", "time_seconds": 60}
    return {"site": s, "meta": m}


def _ai_line(cid, **kw):
    o = {"candidate_id": cid, "status": "ok", "eligible": True, "gt_role": "SIGN", "assessability": "DETERMINATE",
         "hybrid_component": False, "obvious_from_name": False, "evidence_needed": "downstream-usage",
         "key_provenance": "generated", "ambiguity": "none", "evidence_lines": ["x:1"], "rationale": "r"}
    o.update(kw)
    return json.dumps(o)


# ------------------------------------------------------------------ item lists (real data, read only)
def test_real_item_lists_are_location_only_and_opaque():
    pil = LP.items("pilot", "paramiko", ROOT) + LP.items("pilot", "python-jose", ROOT)
    syn = LP.items("synthetic", "synthetic", ROOT)
    assert (len(pil), len(syn)) == (31, 78)
    assert all(set(i) == ITEM_KEYS for i in pil + syn)
    assert all(P.is_candidate_id(i["candidate_id"]) for i in pil + syn)
    assert len({i["candidate_id"] for i in pil + syn}) == 109
    names = _base_cases()
    for i in syn:                                         # nothing in a synthetic item reveals its base case
        assert i["file"] == f"items/{i['candidate_id']}.py" and i["commit"].startswith("generator-")
        assert not any(n in json.dumps(i) for n in names)
    assert syn == LP.items("synthetic", "synthetic", ROOT)          # deterministic order


def test_item_lists_refuse_unknown_repositories_and_phases():
    with pytest.raises(LP.LoopError):
        LP.items("pilot", "pyjwt", ROOT)
    with pytest.raises(LP.LoopError):
        LP.items("synthetic", "paramiko", ROOT)
    with pytest.raises(LP.LoopError):
        LP.items("DV", "paramiko__paramiko", ROOT)


def test_blinded_copies_change_only_line_one(tmp_path):
    names = _base_cases()
    src = LP._synthetic_source(ROOT)
    for cid, f in src.items():
        dest = tmp_path / f"{cid}.py"
        LP.blind_copy(f, dest)
        a, b = f.read_text(encoding="utf-8").split("\n"), dest.read_text(encoding="utf-8").split("\n")
        assert len(a) == len(b) and a[1:] == b[1:] and b[0] == LP.BLIND_HEADER
        text = dest.read_text(encoding="utf-8")
        assert "Synthetic case" not in text and "generator" not in text and P._forbidden_in(text) == []
        assert not any(n in text for n in names)
    bad = tmp_path / "bad.py"
    bad.write_text('"""something else"""\nx = 1\n', encoding="utf-8")
    with pytest.raises(LP.LoopError):
        LP.blind_copy(bad, tmp_path / "out.py")


# ------------------------------------------------------------------ synthetic loop through the CLI
def test_synthetic_issue_is_blinded_and_ledgered(tmp_path, capsys):
    root = _syn_root(tmp_path)
    run = lambda *args: (AN.main(list(args), root=root), json.loads(capsys.readouterr().out.strip().splitlines()[-1]))[1]
    out = run("issue", "--phase", "synthetic", "--repo", "synthetic")
    assert out["batch"] == "B1" and out["candidates"] == 10 and out["items_total"] == 78 and out["packet_first"] == 0
    work = root / "benchmark/annotation/synthetic/synthetic"
    todo = [json.loads(x) for x in (work / "todo_synthetic_B1.jsonl").read_text(encoding="utf-8").splitlines()]
    packets = json.loads((work / "packets_synthetic_B1.json").read_text(encoding="utf-8"))
    names = _base_cases()
    for t, pk in zip(todo, packets):
        assert set(t) == ITEM_KEYS | {"packet_first"} and (work / t["file"]).exists()
        assert not any(n in pk["text"] for n in names) and "Synthetic case" not in pk["text"]
        assert P._forbidden_in(pk["text"]) == []
    assert not (work / "sites.jsonl").exists() and not any(work.glob("reference*"))
    recs = L.read(root / "benchmark/ledger/synthetic/ledger_synthetic.jsonl")
    L.verify(recs)
    assert recs[0]["phase"] == "synthetic" and recs[0]["step"] == "issue"
    with pytest.raises(SystemExit):                                     # B1 still open
        AN.main(["issue", "--phase", "synthetic", "--repo", "synthetic"], root=root)
    with pytest.raises(SystemExit, match="split"):
        AN.main(["issue", "--phase", "synthetic", "--repo", "synthetic", "--split", "development"], root=root)


# ------------------------------------------------------------------ pilot loop end to end + reference gate
def test_pilot_loop_end_to_end_and_reference_gate(tmp_path, monkeypatch, capsys):
    root = _pilot_root(tmp_path)
    monkeypatch.setattr(R, "IDENTITY", _identity(tmp_path))
    run = lambda *args: (AN.main(list(args), root=root), json.loads(capsys.readouterr().out.strip().splitlines()[-1]))[1]
    assert run("issue", "--phase", "pilot", "--repo", "paramiko")["candidates"] == 2
    with pytest.raises(SystemExit, match="not finished"):               # reference closed during the loop
        AN.main(["reference", "--phase", "pilot", "--repo", "paramiko"], root=root)
    work = root / "benchmark/annotation/pilot/paramiko"
    todo = [json.loads(x) for x in (work / "todo_paramiko_B1.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(set(t) == ITEM_KEYS | {"packet_first"} for t in todo)
    prim = tmp_path / "prim.jsonl"
    prim.write_text("".join(json.dumps(_label(t, "pilot")) + "\n" for t in todo), encoding="utf-8")
    with pytest.raises(SystemExit, match="packet-first"):
        AN.main(["primary", "--phase", "pilot", "--repo", "paramiko", "--batch", "B1", "--file", str(prim), "--packet-first"], root=root)
    assert run("primary", "--phase", "pilot", "--repo", "paramiko", "--batch", "B1", "--file", str(prim))["step"] == "primary"
    assert Path(run("prompt", "--phase", "pilot", "--repo", "paramiko", "--batch", "B1")["prompt"]).exists()
    raw = tmp_path / "raw.txt"
    raw.write_text("\n".join(_ai_line(t["candidate_id"]) for t in todo), encoding="utf-8")
    assert run("ai", "--phase", "pilot", "--repo", "paramiko", "--batch", "B1", "--response", str(raw),
               "--utc", "2026-11-18T12:00:00Z")["records"] == 2
    assert run("compare", "--phase", "pilot", "--repo", "paramiko", "--batch", "B1")["disagreements"] == 0
    adj = tmp_path / "adj.csv"
    adj.write_text("candidate_id,field,final_value,reason,category,context_difference\n", encoding="utf-8")
    assert run("adjudicate", "--phase", "pilot", "--repo", "paramiko", "--batch", "B1", "--adjudication", str(adj))["final_records"] == 2
    assert run("issue", "--phase", "pilot", "--repo", "paramiko")["stop"] == "all items issued"
    ref = run("reference", "--phase", "pilot", "--repo", "paramiko")
    # the fixture finals match reference row P01; row P02 differs in obvious_from_name ('yes') and evidence_needed ('none')
    assert ref["compared"] == 2 and ref["disagreements"] == 2 and ref["no_reference"] == 0
    with (work / ref["file"]).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert sorted(r["field"] for r in rows) == ["evidence_needed", "obvious_from_name"]
    assert {r["reference"] for r in rows} == {"true", '"none"'} and all(r["decision"] == "" for r in rows)
    L.verify(L.read(root / "benchmark/ledger/pilot/ledger_paramiko.jsonl"))
    assert L.read(root / "benchmark/ledger/pilot/ledger_paramiko.jsonl")[-1]["step"] == "note"


# ------------------------------------------------------------------ reference labels and DV/T safeguards
def test_reference_labels_normalised():
    syn = LP.reference_labels("synthetic", "synthetic", ROOT)
    assert len(syn) == 78 and all(isinstance(v["possible_roles"], list) for v in syn.values())
    assert all(isinstance(v["eligible"], bool) for v in syn.values())
    pil = LP.reference_labels("pilot", "paramiko", ROOT)
    assert len(pil) == 17 and all(v["eligible"] in (True, False) for v in pil.values())
    assert LP.normalise("obvious_from_name", "n/a") is None and LP.normalise("possible_roles", "B|A") == ["A", "B"]


def test_dv_and_t_safeguards_unchanged(tmp_path):
    with pytest.raises(SystemExit, match="split"):                     # DV still needs its split
        AN.main(["issue", "--phase", "DV", "--repo", "demo"], root=tmp_path)
    with pytest.raises(SystemExit, match="F1"):                        # T still refused before F1
        AN.main(["issue", "--phase", "T", "--split", "test", "--repo", "demo"], root=tmp_path)
    with pytest.raises(SystemExit, match="pilot and synthetic"):        # no reference step outside the loops
        AN.main(["reference", "--phase", "DV", "--repo", "demo"], root=tmp_path)
    assert set(P.PLANNED_CANDIDATES) == {"DV", "T"}                     # packet-first scope unchanged
