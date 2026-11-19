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
import re
import sys
from pathlib import Path

from . import candidates as C
from . import ledger as L
from . import loops as LP
from . import multicall as MC
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


def _multi(base: Path, row: dict) -> dict:
    """`multi_call` marking of an issued candidate (owner decision F03; guide v1.2 Step A): source only."""
    f = Path(base) / row["file"]
    if not f.is_file():
        return {"multi_call": False}
    return MC.mark(f.read_text(encoding="utf-8", errors="replace"), int(row["line"]))


def _attribution_isolated(root: Path, work: Path) -> None:
    """Second review G11: no tool-attribution file (pool_sources_*.json) may sit in a candidate or annotation folder
    when a batch is issued; it belongs in benchmark/restricted/pool_sources/. This is a procedural check: with a single
    investigator it cannot stop a deliberate look (the access attestation records that)."""
    places = [root / "benchmark" / "candidates", root / "benchmark" / "annotation", Path(work)]
    found = sorted({str(f.relative_to(root)) for d in places if d.exists() for f in d.rglob("pool_sources_*.json")})
    if found:
        raise SystemExit(f"tool-attribution file(s) {found} sit in a candidate or annotation folder; move them to "
                         "benchmark/restricted/pool_sources/ before issuing (guide Sec. 2)")


def _issue_loop(a, root: Path) -> dict:
    """Validation-loop issuance (phases pilot / synthetic): location-only, every item, batches of 10."""
    if a.split is not None:
        raise SystemExit(f"--split does not apply to the {a.phase} loop")
    p = paths(a.phase, a.repo, root)
    _attribution_isolated(root, p["work"])
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
    base = LP.checkout(a.phase, a.repo, root, p["work"])
    todo = p["work"] / f"todo_{a.repo}_{label}.jsonl"
    todo.write_text("".join(json.dumps(r | {"packet_first": False} | _multi(base, r)) + "\n" for r in rows),
                    encoding="utf-8", newline="\n")
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
    _attribution_isolated(root, p["work"])
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
    checkout = _checkout(a.split, a.repo, root)
    todo = p["work"] / f"todo_{a.repo}_{label}.jsonl"
    todo.write_text("".join(json.dumps(r | {"packet_first": flags.get(r["candidate_id"], False)} | _multi(checkout, r))
                            + "\n" for r in rows), encoding="utf-8", newline="\n")
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


DECISION_COLUMNS = ["candidate_id", "token", "verdict", "evidence"]
_EVIDENCE_LOC = re.compile(r"\S+:\d+")


def _forbidden_gate(a, p: dict, packets: list[dict]) -> tuple[list[dict], list[str], dict]:
    """Forbidden-token gate (guide v1.2 Sec. 6; owner decision F07). A packet whose text contains a forbidden token
    (packets.FORBIDDEN) never reaches the AI unless the owner has recorded, for every (candidate, token):
    * verdict `genuine` -> the candidate is EXCLUDED from the AI review (no reason can override this), or
    * verdict `false_positive` -> allowed only with evidence (file:line and why the match does not refer to an
      evaluated tool, this project or its hypotheses).
    Returns (packets to send, excluded candidate IDs, info). The decision file is copied to the work tree and its
    SHA-256 is recorded in the ledger as a `note`. Nothing is redacted."""
    pairs = _warned_pairs(packets)
    if not pairs:
        return packets, [], {}
    if not a.warnings_decision:
        raise SystemExit(f"forbidden token(s) in {len({c for c, _ in pairs})} packet(s): {sorted(pairs)}. The prompt is "
                         f"not built. Record a decision per (candidate_id, token) in a CSV with columns "
                         f"{DECISION_COLUMNS} and pass it with --warnings-decision (guide v1.2 Sec. 6).")
    src = Path(a.warnings_decision)
    excluded, fp = _read_decision(src, pairs)
    dest = p["work"] / f"forbidden_decision_{a.repo}_{a.batch}.csv"
    if dest.exists() and dest.read_bytes() != src.read_bytes():
        raise SystemExit(f"{dest.name} already exists with a different decision; a change is a new batch decision")
    if not dest.exists():
        dest.write_bytes(src.read_bytes())
    rec = L.append(p["ledger"], step="note", repo=a.repo, phase=a.phase, batch=a.batch, file=dest,
                   note=f"forbidden-token decision: excluded {sorted(excluded)}; verified false positives "
                        f"{sorted(fp - excluded)}")
    return ([pk for pk in packets if pk["candidate_id"] not in excluded], sorted(excluded),
            {"decision_sha256": rec["sha256"], "false_positive": sorted(fp - excluded)})


def _warned_pairs(packets: list[dict]) -> set[tuple[str, str]]:
    """(candidate_id, token) for every forbidden token in the text that would be sent to the AI."""
    return {(pk["candidate_id"], t) for pk in packets for t in P._forbidden_in(pk["text"])}


def _read_decision(src: Path, pairs: set[tuple[str, str]]) -> tuple[set[str], set[str]]:
    """Validate a forbidden-token decision file against the warned pairs. Returns (excluded, verified false positives).
    genuine -> excluded (no override); false_positive -> needs file:line evidence. Anything else is refused."""
    with Path(src).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != DECISION_COLUMNS:
            raise SystemExit(f"decision file columns must be exactly {DECISION_COLUMNS}")
        rows = list(reader)
    got = [(r["candidate_id"], r["token"]) for r in rows]
    if len(got) != len(set(got)) or set(got) != pairs:
        raise SystemExit(f"the decision file must cover exactly the warned (candidate, token) pairs {sorted(pairs)}")
    excluded, fp = set(), set()
    for r in rows:
        v = (r["verdict"] or "").strip()
        if v == "genuine":
            excluded.add(r["candidate_id"])
        elif v == "false_positive":
            if not _EVIDENCE_LOC.search(r["evidence"] or ""):
                raise SystemExit(f"{r['candidate_id']}/{r['token']}: a false positive needs evidence with a file:line "
                                 "reference showing the match is not forbidden content")
            fp.add(r["candidate_id"])
        else:
            raise SystemExit(f"verdict must be 'genuine' or 'false_positive', not {v!r}")
    return excluded, fp


def _ai_gate(a, p: dict, packets: list[dict], raw: str) -> tuple[list[dict], list[str]]:
    """Fail-closed check at the AI-response step (second-review finding G06). If any packet of the batch contains a
    forbidden token, the batch's recorded decision (written by the prompt gate) must exist and be valid; the response
    is rejected outright if it contains a record for an excluded candidate; excluded candidates are never parsed."""
    pairs = _warned_pairs(packets)
    if not pairs:
        return packets, []
    dec = p["work"] / f"forbidden_decision_{a.repo}_{a.batch}.csv"
    if not dec.exists():
        raise SystemExit(f"forbidden token(s) in {len({c for c, _ in pairs})} packet(s) and no recorded decision: run "
                         "the prompt step with --warnings-decision first; the AI response is not accepted")
    excluded, _ = _read_decision(dec, pairs)
    named = {o.get("candidate_id") for o in R._json_objects(raw)}
    leaked = sorted(named & excluded)
    if leaked:
        raise SystemExit(f"the AI response contains records for excluded candidate(s) {leaked}; it is rejected")
    return [pk for pk in packets if pk["candidate_id"] not in excluded], sorted(excluded)


def _excluded(p: dict, a) -> list[str]:
    f = p["work"] / f"forbidden_decision_{a.repo}_{a.batch}.csv"
    if not f.exists():
        return []
    with f.open(encoding="utf-8", newline="") as fh:
        return sorted({r["candidate_id"] for r in csv.DictReader(fh) if r["verdict"].strip() == "genuine"})


def cmd_prompt(a, root: Path) -> dict:
    p = paths(a.phase, a.repo, root)
    packets = json.loads((p["work"] / f"packets_{a.repo}_{a.batch}.json").read_text(encoding="utf-8"))
    send, excluded, info = _forbidden_gate(a, p, packets)
    text, sha = R.build_prompt(send)
    out = p["work"] / f"prompt_{a.repo}_{a.batch}.txt"
    out.write_text(text, encoding="utf-8", newline="\n")
    return {"prompt": str(out), "template_sha256": sha, "excluded_forbidden": excluded, **info}


def cmd_ai(a, root: Path) -> dict:
    p = paths(a.phase, a.repo, root)
    packets = json.loads((p["work"] / f"packets_{a.repo}_{a.batch}.json").read_text(encoding="utf-8"))
    raw = Path(a.response).read_text(encoding="utf-8")
    packets, _ = _ai_gate(a, p, packets, raw)
    ident = R.load_identity()
    parsed = R.parse_ai_response(raw, packets, ident, datetime_utc=a.utc, prompt_sha256=R.template_sha256())
    out = p["work"] / f"ai_review_{a.repo}_{a.batch}.jsonl"
    out.write_text("".join(json.dumps(r) + "\n" for r in parsed["records"]), encoding="utf-8", newline="\n")
    (p["work"] / f"ai_raw_{a.repo}_{a.batch}.txt").write_bytes(Path(a.response).read_bytes())
    L.append(p["ledger"], step="ai_review", repo=a.repo, phase=a.phase, batch=a.batch, file=out,
             note=f"raw sha256 {L.file_sha256(Path(a.response))}; identity sha256 {R.identity_sha256()}"
                  f"; app_version {ident.get('app_version') or 'not shown'}")
    excl = _excluded(p, a)
    return {"records": len(parsed["records"]), "problems": parsed["problems"],
            "absent": [c for c in parsed["absent"] if c not in excl], "excluded_forbidden": excl}


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
    exposed = LP.guide_exposed(a.phase, a.repo, root)
    out = p["work"] / f"reference_disagreements_{a.repo}.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["candidate_id", "guide_exposed", "field", "owner_final", "reference",
                                          "decision", "reason"])
        w.writeheader()
        for r in res["disagreements"]:
            w.writerow({**r, "guide_exposed": r["candidate_id"] in exposed, "decision": "", "reason": ""})
    dis_exp = sum(r["candidate_id"] in exposed for r in res["disagreements"])
    fin_ids = {r["meta"]["candidate_id"] for r in finals if not r["meta"].get("annotator_added")}
    L.append(p["ledger"], step="note", repo=a.repo, phase=a.phase, file=out,
             note=f"reference comparison: {len(res['disagreements'])} field disagreements over {res['compared']} items "
                  f"(guide-exposed subset: {len(exposed & fin_ids)} items, {dis_exp} disagreements; reported separately)")
    return {"disagreements": len(res["disagreements"]), "compared": res["compared"], "no_reference": len(res["no_reference"]),
            "file": out.name, "guide_exposed_items": len(exposed & fin_ids), "disagreements_guide_exposed": dis_exp,
            "disagreements_not_exposed": len(res["disagreements"]) - dis_exp}


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
        if name == "prompt":
            s.add_argument("--warnings-decision", default=None,
                           help="CSV (candidate_id,token,verdict,evidence) required when a packet contains a "
                                "forbidden token: genuine -> excluded from the AI review; false_positive -> needs "
                                "file:line evidence")
    a = ap.parse_args(argv)
    res = globals()[f"cmd_{a.cmd}"](a, root)
    if a.push and a.cmd != "status":
        L.git_commit_and_push(paths(a.phase, a.repo, root)["ledger"], f"Ledger {a.phase} {a.repo}: {a.cmd}", root)
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
