"""Second-review findings G05 (forbidden-token coverage of every registered hypothesis/comparison identifier) and G06
(the AI-response step is fail-closed: no response is accepted for a batch with forbidden content unless the prompt
gate's decision is recorded, and a response naming an excluded candidate is rejected). Exercised through the real CLI
command path (pqscan.bench.annotate.main). All values are test values."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from pqscan.bench import annotate as AN
from pqscan.bench import ledger as L
from pqscan.bench import packets as P
from pqscan.bench import review as R

REGISTERED = ["H1a", "H1b", "H2a", "H2b", "H2-1", "H2-2", "H2-3", "H2-4", "H2-S", "F-A", "F-B"]


# ------------------------------------------------------------------ G05
@pytest.mark.parametrize("label", REGISTERED)
@pytest.mark.parametrize("form", ["{}", "{}", "({})", "# see {}.", 'x = "{}"', "{}: result", "family {}, Holm"])
def test_every_registered_identifier_is_detected(label, form):
    for variant in (label, label.lower(), label.upper()):
        assert P._forbidden_in(form.format(variant)) == [label.lower()], variant


@pytest.mark.parametrize("text", ["<h1>Title</h1>", "h1 = hashlib.sha1()", "H3 and H4 in prose", "sha1a", "h2-10",
                                  "self-assessment", "chf-a", "buf-b", "x_h2a", "h1ab", "H2", "fa = 1", "f_a"])
def test_ordinary_code_is_not_flagged(text):
    assert P._forbidden_in(text) == []


def test_registered_identifiers_listed_and_template_stays_clean():
    assert set(P.HYPOTHESIS_IDS) == {x.lower() for x in REGISTERED}
    assert set(P.HYPOTHESIS_IDS) <= set(P.FORBIDDEN)
    assert P._forbidden_in(R.prompt_template()) == []


# ------------------------------------------------------------------ G06 (real command path)
CLEAN = {"candidate_id": "C-0000000000a1", "rule": "packet-v1", "file": "a.py", "line": 1, "warnings": [],
         "text": "1: k = rsa.generate_private_key(65537, 3072)\n", "sha256": "a" * 64}
NOISY = {"candidate_id": "C-0000000000b2", "rule": "packet-v1", "file": "b.py", "line": 2, "warnings": ["x"],
         "text": "1: # benchmark notes: H2-1 comparison\n2: k.sign(m)\n", "sha256": "b" * 64}


def _ai_line(cid: str) -> str:
    return json.dumps({"candidate_id": cid, "status": "ok", "eligible": True, "gt_role": "SIGN",
                       "assessability": "DETERMINATE", "hybrid_component": False, "obvious_from_name": False,
                       "evidence_needed": "downstream-usage", "key_provenance": "generated", "ambiguity": "none",
                       "evidence_lines": ["a.py:1"], "rationale": "r"})


@pytest.fixture
def batch(tmp_path, monkeypatch):
    ident = tmp_path / "ident.json"
    ident.write_text(json.dumps({"interface_or_api": "TEST interface", "model": "TEST-MODEL",
                                 "recorded_utc": "2026-11-16T09:00:00Z",
                                 "isolation": {"fresh_temporary_chat_per_batch": "yes"} | {k: "off" for k in R.ISOLATION_OFF}}),
                     encoding="utf-8")
    monkeypatch.setattr(R, "IDENTITY", ident)
    root = tmp_path / "root"
    p = AN.paths("DV", "demo", root)
    p["work"].mkdir(parents=True)
    (p["work"] / "packets_demo_B1.json").write_text(json.dumps([CLEAN, NOISY]), encoding="utf-8")
    prim = p["work"] / "primary_demo_B1.jsonl"
    prim.write_text("{}\n", encoding="utf-8")
    L.append(p["ledger"], step="issue", repo="demo", phase="DV", batch="B1",
             candidates=[CLEAN["candidate_id"], NOISY["candidate_id"]])
    L.append(p["ledger"], step="primary", repo="demo", phase="DV", batch="B1", file=prim)
    return root, p, tmp_path


def _run(root, *args):
    return AN.main(list(args), root=root)


def _decision(tmp_path, verdict, evidence=""):
    f = tmp_path / f"decision_{verdict}.csv"
    with f.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=AN.DECISION_COLUMNS)
        w.writeheader()
        w.writerow({"candidate_id": NOISY["candidate_id"], "token": "h2-1", "verdict": verdict, "evidence": evidence})
    return f


def test_ai_step_refused_when_no_decision_was_recorded(batch):
    root, p, tmp = batch
    raw = tmp / "raw.txt"
    raw.write_text(_ai_line(CLEAN["candidate_id"]) + "\n" + _ai_line(NOISY["candidate_id"]), encoding="utf-8")
    with pytest.raises(SystemExit, match="no recorded decision"):
        _run(root, "ai", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--response", str(raw),
             "--utc", "2026-11-16T12:00:00Z")
    assert not (p["work"] / "ai_review_demo_B1.jsonl").exists()
    assert L.read(p["ledger"])[-1]["step"] == "primary"                 # nothing recorded


def test_prompt_refused_without_decision_and_excludes_genuine_content(batch, capsys):
    root, p, tmp = batch
    with pytest.raises(SystemExit, match="forbidden token"):
        _run(root, "prompt", "--phase", "DV", "--repo", "demo", "--batch", "B1")
    _run(root, "prompt", "--phase", "DV", "--repo", "demo", "--batch", "B1",
         "--warnings-decision", str(_decision(tmp, "genuine", "reason ignored")))
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert out["excluded_forbidden"] == [NOISY["candidate_id"]]
    prompt = (p["work"] / "prompt_demo_B1.txt").read_text(encoding="utf-8")
    assert NOISY["text"] not in prompt and CLEAN["text"] in prompt and P._forbidden_in(prompt) == []


def test_ai_response_naming_an_excluded_candidate_is_rejected(batch, capsys):
    root, p, tmp = batch
    _run(root, "prompt", "--phase", "DV", "--repo", "demo", "--batch", "B1",
         "--warnings-decision", str(_decision(tmp, "genuine")))
    capsys.readouterr()
    bad = tmp / "bad.txt"
    bad.write_text(_ai_line(CLEAN["candidate_id"]) + "\n" + _ai_line(NOISY["candidate_id"]), encoding="utf-8")
    with pytest.raises(SystemExit, match="excluded candidate"):
        _run(root, "ai", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--response", str(bad),
             "--utc", "2026-11-16T12:00:00Z")
    assert not (p["work"] / "ai_review_demo_B1.jsonl").exists()
    good = tmp / "good.txt"
    good.write_text(_ai_line(CLEAN["candidate_id"]), encoding="utf-8")
    _run(root, "ai", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--response", str(good),
         "--utc", "2026-11-16T12:00:00Z")
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert out["records"] == 1 and out["excluded_forbidden"] == [NOISY["candidate_id"]] and out["absent"] == []
    recs = [json.loads(x) for x in (p["work"] / "ai_review_demo_B1.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["meta"]["candidate_id"] for r in recs] == [CLEAN["candidate_id"]]


def test_tampered_decision_file_is_refused_at_the_ai_step(batch, capsys):
    root, p, tmp = batch
    _run(root, "prompt", "--phase", "DV", "--repo", "demo", "--batch", "B1",
         "--warnings-decision", str(_decision(tmp, "genuine")))
    capsys.readouterr()
    dec = p["work"] / "forbidden_decision_demo_B1.csv"
    dec.write_text(dec.read_text(encoding="utf-8").replace("genuine", "false_positive"), encoding="utf-8")  # no evidence
    good = tmp / "good.txt"
    good.write_text(_ai_line(CLEAN["candidate_id"]), encoding="utf-8")
    with pytest.raises(SystemExit, match="file:line"):
        _run(root, "ai", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--response", str(good),
             "--utc", "2026-11-16T12:00:00Z")


def test_verified_false_positive_proceeds_through_both_steps(batch, capsys):
    root, p, tmp = batch
    _run(root, "prompt", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--warnings-decision",
         str(_decision(tmp, "false_positive", "b.py:1 is a vendored changelog line, not this study's comparison")))
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert out["excluded_forbidden"] == [] and out["false_positive"] == [NOISY["candidate_id"]]
    raw = tmp / "raw.txt"
    raw.write_text(_ai_line(CLEAN["candidate_id"]) + "\n" + _ai_line(NOISY["candidate_id"]), encoding="utf-8")
    _run(root, "ai", "--phase", "DV", "--repo", "demo", "--batch", "B1", "--response", str(raw),
         "--utc", "2026-11-16T12:00:00Z")
    assert json.loads(capsys.readouterr().out.strip().splitlines()[-1])["records"] == 2
