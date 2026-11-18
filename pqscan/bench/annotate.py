"""Annotation workflow in the protocol's step order (protocol v1.0.4 Sec. 3; guide v1.1 Sec. 1; R4-19 items 1-7).

    python -m pqscan.bench.annotate issue      --phase DV --split development --repo paramiko__paramiko
    python -m pqscan.bench.annotate primary    --phase DV --repo paramiko__paramiko --batch B1 --file primary_..._B1.jsonl [--packet-first]
    python -m pqscan.bench.annotate prompt     --phase DV --repo paramiko__paramiko --batch B1
    python -m pqscan.bench.annotate ai         --phase DV --repo paramiko__paramiko --batch B1 --response raw.txt --utc 2026-...Z
    python -m pqscan.bench.annotate compare    --phase DV --repo paramiko__paramiko --batch B1
    python -m pqscan.bench.annotate adjudicate --phase DV --repo paramiko__paramiko --batch B1 --adjudication adj.csv
    python -m pqscan.bench.annotate status     --phase DV --repo paramiko__paramiko

Validation loops (R4-20 step 4; `pqscan/bench/loops.py`): phases `pilot` (repos `paramiko`, `python-jose`) and
`synthetic` (repo `synthetic`) use the same steps without `--split`; every item is issued in batches of 10; no quota,
no packet-first subset, no re-label rule. After the last batch is adjudicated:
    python -m pqscan.bench.annotate reference  --phase synthetic --repo synthetic

Files: labels, packets, prompts, AI exports and final labels go to the git-ignored `benchmark/annotation/<phase>/<repo>/`.
The hash-only ledger goes to `benchmark/ledger/<phase>/ledger_<repo>.jsonl`. Add `--push` to commit and push the
ledger after a step (the protocol requires that during annotation). Nothing here starts annotation by itself: every
step is run by the owner.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from . import candidates as C
from . import ledger as L
from . import loops as LP
from . import packets as P
from . import review as R
from .labels import eligibility_of, validate_file

ROOT = Path(__file__).resolve().parents[2]
SPLIT_OF_PHASE = {"DV": ("development", "validation"), "T": ("test",)}


def paths(phase: str, repo: str, root: Path = ROOT) -> dict:
    work = root / "benchmark" / "annotation" / phase / repo
    return {"work": work, "ledger": root / "benchmark" / "ledger" / phase / f"ledger_{repo}.jsonl"}


def _order_path(split: str, repo: str, root: Path) -> Path:
    return root / "benchmark" / "candidates" / split / f"order_{repo}.json"


def _checkout(split: str, repo: str, root: Path) -> Path:
    return root / ".cache" / "repos" / split / repo


def _final_eligibility(work: Path) -> dict:
    out = {}
    for f in sorted(work.glob("final_*_B*.jsonl")):
        for rec in (json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()):
            if not rec["meta"].get("annotator_added"):
                out[rec["meta"]["candidate_id"]] = eligibility_of(rec)
    return out


def _batch_ids(records: list[dict], batch: str) -> list[str]:
    for r in records:
        if r["step"] == "issue" and r["batch"] == batch:
            return r["candidates"]
    raise L.LedgerError(f"batch {batch} was never issued")


def _issue_loop(a, root: Path) -> dict:
    """Validation-loop issuance (phases pilot / synthetic): location-only, every item, batches of 10."""
    if a.split is not None:
        raise SystemExit(f"--split does not apply to the {a.phase} loop")
    p = paths(a.phase, a.repo, root)
    recs = L.read(p["ledger"])
    L.verify(recs)
    batch, state = L.open_batch(recs)
    if state not in (None, "adjudication"):
        raise SystemExit(f"batch {batch} is still open at step {state}")
    all_items = LP.items(a.phase, a.repo, root)
    res = LP.next_batch(all_items, L.issued_ids(recs))
    if res["stop"]:
        return {k: v for k, v in res.items() if k != "batch"}
    label = f"B{sum(r['step'] == 'issue' for r in recs) + 1}"
    p["work"].mkdir(parents=True, exist_ok=True)
    rows = res["batch"]
    LP.prepare_batch(a.phase, rows, root, p["work"])
    todo = p["work"] / f"todo_{a.repo}_{label}.jsonl"
    todo.write_text("".join(json.dumps(r | {"packet_first": False}) + "\n" for r in rows), encoding="utf-8", newline="\n")
    base = LP.checkout(a.phase, a.repo, root, p["work"])
    packets = [P.build_packet(base, r["file"], r["line"], r["candidate_id"]) for r in rows]
    (p["work"] / f"packets_{a.repo}_{label}.json").write_text(json.dumps(packets, indent=1), encoding="utf-8", newline="\n")
    rec = L.append(p["ledger"], step="issue", repo=a.repo, phase=a.phase, batch=label,
                   candidates=[r["candidate_id"] for r in rows])
    return {"batch": label, "candidates": len(rows), "packet_first": 0, "issued_total": res["issued"] + len(rows),
            "items_total": res["total"], "ledger": rec["hash"][:12],
            "warnings": sorted({w for pk in packets for w in pk["warnings"]})}


def cmd_issue(a, root: Path) -> dict:
    if a.phase in LP.LOOP_PHASES:
        return _issue_loop(a, root)
    if a.phase == "T" and not (root / "docs" / "freeze" / "pretest_freeze.json").exists():
        raise SystemExit("the test phase needs the F1 freeze record first")
    if a.split not in SPLIT_OF_PHASE[a.phase]:
        raise SystemExit(f"split {a.split} does not belong to phase {a.phase}")
    p = paths(a.phase, a.repo, root)
    recs = L.read(p["ledger"])
    L.verify(recs)
    batch, state = L.open_batch(recs)
    if state not in (None, "adjudication"):
        raise SystemExit(f"batch {batch} is still open at step {state}")
    order = json.loads(_order_path(a.split, a.repo, root).read_text(encoding="utf-8"))
    res = C.next_batch(order, L.issued_ids(recs), _final_eligibility(p["work"]), C.quota_for(a.split))
    if res["stop"]:
        return {k: v for k, v in res.items() if k != "batch"}
    label = "B0" if res["batch_kind"] == "B0" else f"B{sum(r['step'] == 'issue' and r['batch'] != 'B0' for r in recs) + 1}"
    p["work"].mkdir(parents=True, exist_ok=True)
    rows = C.annotator_list(order, res["batch"])
    flags = {r["candidate_id"]: P.packet_first(r["candidate_id"], a.phase) for r in rows} if a.phase in P.PLANNED_CANDIDATES else {}
    todo = p["work"] / f"todo_{a.repo}_{label}.jsonl"
    todo.write_text("".join(json.dumps(r | {"packet_first": flags.get(r["candidate_id"], False)}) + "\n" for r in rows),
                    encoding="utf-8", newline="\n")
    checkout = _checkout(a.split, a.repo, root)
    packets = [P.build_packet(checkout, r["file"], r["line"], r["candidate_id"]) for r in rows]
    (p["work"] / f"packets_{a.repo}_{label}.json").write_text(json.dumps(packets, indent=1), encoding="utf-8", newline="\n")
    rec = L.append(p["ledger"], step="issue", repo=a.repo, phase=a.phase, batch=label,
                   candidates=[r["candidate_id"] for r in rows])
    return {"batch": label, "candidates": len(rows), "packet_first": sum(flags.values()), "ledger": rec["hash"][:12],
            "warnings": sorted({w for pk in packets for w in pk["warnings"]})}


def cmd_primary(a, root: Path) -> dict:
    p = paths(a.phase, a.repo, root)
    recs = L.read(p["ledger"])
    if a.packet_first and a.phase in LP.LOOP_PHASES:
        raise SystemExit(f"the packet-first subset is defined for phases DV and T only, not the {a.phase} loop")
    kind = "packet_first" if a.packet_first else "primary"
    ids = _batch_ids(recs, a.batch)
    if a.packet_first:
        todo = [json.loads(x) for x in (p["work"] / f"todo_{a.repo}_{a.batch}.jsonl").read_text(encoding="utf-8").splitlines() if x]
        ids = [t["candidate_id"] for t in todo if t["packet_first"]]
    validate_file(Path(a.file), kind, issued=ids)
    dest = p["work"] / f"{'primary_packet' if a.packet_first else 'primary'}_{a.repo}_{a.batch}.jsonl"
    if Path(a.file).resolve() != dest.resolve():
        if dest.exists():
            raise SystemExit(f"{dest.name} already exists; a correction is a new file with a reason")
        dest.write_bytes(Path(a.file).read_bytes())
    rec = L.append(p["ledger"], step="primary_packet" if a.packet_first else "primary", repo=a.repo, phase=a.phase,
                   batch=a.batch, file=dest)
    return {"step": rec["step"], "sha256": rec["sha256"][:12]}


def cmd_prompt(a, root: Path) -> dict:
    p = paths(a.phase, a.repo, root)
    packets = json.loads((p["work"] / f"packets_{a.repo}_{a.batch}.json").read_text(encoding="utf-8"))
    text, sha = R.build_prompt(packets)
    out = p["work"] / f"prompt_{a.repo}_{a.batch}.txt"
    out.write_text(text, encoding="utf-8", newline="\n")
    return {"prompt": str(out), "template_sha256": sha}


def cmd_ai(a, root: Path) -> dict:
    p = paths(a.phase, a.repo, root)
    packets = json.loads((p["work"] / f"packets_{a.repo}_{a.batch}.json").read_text(encoding="utf-8"))
    raw = Path(a.response).read_text(encoding="utf-8")
    parsed = R.parse_ai_response(raw, packets, R.load_identity(), datetime_utc=a.utc, prompt_sha256=R.template_sha256())
    out = p["work"] / f"ai_review_{a.repo}_{a.batch}.jsonl"
    out.write_text("".join(json.dumps(r) + "\n" for r in parsed["records"]), encoding="utf-8", newline="\n")
    (p["work"] / f"ai_raw_{a.repo}_{a.batch}.txt").write_bytes(Path(a.response).read_bytes())
    L.append(p["ledger"], step="ai_review", repo=a.repo, phase=a.phase, batch=a.batch, file=out,
             note=f"raw sha256 {L.file_sha256(Path(a.response))}")
    return {"records": len(parsed["records"]), "problems": parsed["problems"], "absent": parsed["absent"]}


def cmd_compare(a, root: Path) -> dict:
    p = paths(a.phase, a.repo, root)
    prim = validate_file(p["work"] / f"primary_{a.repo}_{a.batch}.jsonl", "primary")
    ai = [json.loads(x) for x in (p["work"] / f"ai_review_{a.repo}_{a.batch}.jsonl").read_text(encoding="utf-8").splitlines() if x]
    res = R.compare(prim, ai)
    out = p["work"] / f"disagreements_{a.repo}_{a.batch}.csv"
    R.write_disagreements(res["disagreements"], out)
    L.append(p["ledger"], step="compare", repo=a.repo, phase=a.phase, batch=a.batch, file=out)
    return {"disagreements": len(res["disagreements"]), "insufficient_context": len(res["insufficient_context"]),
            "not_reviewed": len(res["not_reviewed"])}


def cmd_adjudicate(a, root: Path) -> dict:
    p = paths(a.phase, a.repo, root)
    prim = validate_file(p["work"] / f"primary_{a.repo}_{a.batch}.jsonl", "primary")
    dis = R.read_adjudication(p["work"] / f"disagreements_{a.repo}_{a.batch}.csv")
    finals = R.adjudicate(prim, [{k: d[k] for k in ("candidate_id", "field", "owner_value", "ai_value")} for d in dis],
                          R.read_adjudication(Path(a.adjudication)))
    out = p["work"] / f"final_{a.repo}_{a.batch}.jsonl"
    out.write_text("".join(json.dumps(r) + "\n" for r in finals), encoding="utf-8", newline="\n")
    adj_copy = p["work"] / f"adjudication_{a.repo}_{a.batch}.csv"
    adj_copy.write_bytes(Path(a.adjudication).read_bytes())
    L.append(p["ledger"], step="adjudication", repo=a.repo, phase=a.phase, batch=a.batch, file=out,
             note=f"adjudication csv sha256 {L.file_sha256(adj_copy)}")
    return {"final_records": len(finals), "unresolved": R.unresolved_report(finals)["with_unresolved_field"]}


def cmd_reference(a, root: Path) -> dict:
    """Validation loops only: owner-final labels vs the reference labels (pilot: earlier developer labels, circular;
    synthetic: generator labels by construction). Refused until every item is issued and every batch adjudicated."""
    if a.phase not in LP.LOOP_PHASES:
        raise SystemExit("the reference comparison exists only for the pilot and synthetic loops")
    p = paths(a.phase, a.repo, root)
    recs = L.read(p["ledger"])
    L.verify(recs)
    batch, state = L.open_batch(recs)
    total = len(LP.items(a.phase, a.repo, root))
    if len(set(L.issued_ids(recs))) != total or state != "adjudication":
        raise SystemExit(f"the loop is not finished: {len(set(L.issued_ids(recs)))}/{total} items issued, "
                         f"last step {state!r}; the reference stays closed until every batch is adjudicated")
    finals = [json.loads(x) for f in sorted(p["work"].glob(f"final_{a.repo}_B*.jsonl"))
              for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
    res = LP.reference_compare(finals, LP.reference_labels(a.phase, a.repo, root))
    out = p["work"] / f"reference_disagreements_{a.repo}.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["candidate_id", "field", "owner_final", "reference", "decision", "reason"])
        w.writeheader()
        for r in res["disagreements"]:
            w.writerow({**r, "decision": "", "reason": ""})
    L.append(p["ledger"], step="note", repo=a.repo, phase=a.phase, file=out,
             note=f"reference comparison: {len(res['disagreements'])} field disagreements over {res['compared']} items")
    return {"disagreements": len(res["disagreements"]), "compared": res["compared"], "no_reference": len(res["no_reference"]),
            "file": out.name}


def cmd_status(a, root: Path) -> dict:
    p = paths(a.phase, a.repo, root)
    recs = L.read(p["ledger"])
    L.verify(recs)
    batch, state = L.open_batch(recs)
    return {"records": len(recs), "head": (recs[-1]["hash"][:12] if recs else None), "open_batch": batch,
            "last_step": state, "issued": len(L.issued_ids(recs))}


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    ap = argparse.ArgumentParser(prog="pqscan.bench.annotate")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("issue", "primary", "prompt", "ai", "compare", "adjudicate", "status", "reference"):
        s = sub.add_parser(name)
        s.add_argument("--phase", choices=["DV", "T", *LP.LOOP_PHASES], required=True)
        s.add_argument("--repo", required=True)
        s.add_argument("--push", action="store_true", help="commit and push the ledger after the step")
        if name == "issue":
            s.add_argument("--split", choices=sorted(C.QUOTAS), default=None,
                           help="required for phases DV and T; not used by the pilot/synthetic loops")
        if name in ("primary", "prompt", "ai", "compare", "adjudicate"):
            s.add_argument("--batch", required=True)
        if name == "primary":
            s.add_argument("--file", required=True)
            s.add_argument("--packet-first", action="store_true")
        if name == "ai":
            s.add_argument("--response", required=True)
            s.add_argument("--utc", required=True)
        if name == "adjudicate":
            s.add_argument("--adjudication", required=True)
    a = ap.parse_args(argv)
    res = globals()[f"cmd_{a.cmd}"](a, root)
    if a.push and a.cmd != "status":
        L.git_commit_and_push(paths(a.phase, a.repo, root)["ledger"], f"Ledger {a.phase} {a.repo}: {a.cmd}", root)
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
