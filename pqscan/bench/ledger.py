"""Append-only, hash-chained issuance ledger (protocol v1.0.4 Sec. 2-3; decision V6; R4-19 item 3).

One ledger per repository and phase: `benchmark/ledger/<phase>/ledger_<repo>.jsonl`. It holds **hashes only**, never
label content, so it is committed and pushed after every step. Label files, AI exports and packets live in the
git-ignored `benchmark/annotation/` tree; their SHA-256 values are what the ledger records.

Record fields: seq, prev (hash of the previous record, 64 zeros for the first), utc, step, repo, phase, batch,
candidates (for `issue`), file (basename) and sha256 (for file steps), note; `hash` = SHA-256 of the canonical JSON
of every other field.

Step order per batch (protocol Sec. 3): issue -> [primary_packet] -> primary -> ai_review -> compare -> adjudication.
`primary_packet` is present only when the batch contains packet-first candidates. A new `issue` is accepted only
after the previous batch's `adjudication`. Re-label steps (`relabel_issue`, `relabel`) and `note` records may follow
any completed batch. Every violation raises LedgerError; nothing is repaired.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import subprocess
from pathlib import Path

GENESIS = "0" * 64
BATCH_STEPS = ("issue", "primary_packet", "primary", "ai_review", "compare", "adjudication")
NEXT = {None: {"issue"}, "issue": {"primary_packet", "primary"}, "primary_packet": {"primary"},
        "primary": {"ai_review"}, "ai_review": {"compare"}, "compare": {"adjudication"}, "adjudication": {"issue"}}
FREE_STEPS = ("relabel_issue", "relabel", "note")
FILE_STEPS = {"primary_packet", "primary", "ai_review", "compare", "adjudication", "relabel"}
PHASES = ("DV", "T", "pilot", "synthetic")


class LedgerError(ValueError):
    pass


def canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def record_hash(rec: dict) -> str:
    return hashlib.sha256(canonical({k: v for k, v in rec.items() if k != "hash"})).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path: Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def verify(records: list[dict]) -> None:
    """Chain integrity and step order. Raises LedgerError on the first problem."""
    prev, state, last_batch = GENESIS, None, None
    issued: set[str] = set()
    for i, r in enumerate(records):
        if r.get("seq") != i:
            raise LedgerError(f"record {i}: seq {r.get('seq')} out of order")
        if r.get("prev") != prev:
            raise LedgerError(f"record {i}: broken chain (prev does not match)")
        if record_hash(r) != r.get("hash"):
            raise LedgerError(f"record {i}: hash mismatch (record modified)")
        step = r.get("step")
        if step in FREE_STEPS:
            if state not in (None, "adjudication") and step != "note":
                raise LedgerError(f"record {i}: {step} inside an unfinished batch")
        elif step in BATCH_STEPS:
            if step not in NEXT[state]:
                raise LedgerError(f"record {i}: step {step} after {state} is not allowed")
            if step == "issue":
                ids = r.get("candidates") or []
                if not ids or len(set(ids)) != len(ids):
                    raise LedgerError(f"record {i}: issue needs distinct candidate IDs")
                dup = issued & set(ids)
                if dup:
                    raise LedgerError(f"record {i}: candidates issued twice: {sorted(dup)[:3]}")
                issued |= set(ids)
                last_batch = r.get("batch")
            elif r.get("batch") != last_batch:
                raise LedgerError(f"record {i}: {step} for batch {r.get('batch')} but the open batch is {last_batch}")
            state = step
        else:
            raise LedgerError(f"record {i}: unknown step {step!r}")
        if step in FILE_STEPS and not (isinstance(r.get("sha256"), str) and len(r["sha256"]) == 64):
            raise LedgerError(f"record {i}: {step} needs a file SHA-256")
        prev = r["hash"]


def issued_ids(records: list[dict]) -> list[str]:
    """Issued candidate IDs in issuance order (the sampler's `issued` input, M11)."""
    return [c for r in records if r["step"] == "issue" for c in r["candidates"]]


def open_batch(records: list[dict]) -> tuple[str | None, str | None]:
    """(batch label, last batch step) of the most recent batch, or (None, None)."""
    state = batch = None
    for r in records:
        if r["step"] in BATCH_STEPS:
            state, batch = r["step"], r.get("batch")
    return batch, state


def append(path: Path, *, step: str, repo: str, phase: str, batch: str | None = None, candidates: list[str] | None = None,
           file: Path | None = None, note: str = "", utc: str | None = None) -> dict:
    """Validate the whole chain, append one record, validate again, write. Returns the new record."""
    if phase not in PHASES:
        raise LedgerError(f"unknown phase {phase!r}")
    path = Path(path)
    records = read(path)
    verify(records)
    if records and (records[0]["repo"] != repo or records[0]["phase"] != phase):
        raise LedgerError("one ledger per repository and phase")
    rec = {"seq": len(records), "prev": records[-1]["hash"] if records else GENESIS,
           "utc": utc or _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "step": step, "repo": repo, "phase": phase, "batch": batch, "note": note}
    if candidates is not None:
        rec["candidates"] = list(candidates)
    if file is not None:
        rec["file"] = Path(file).name
        rec["sha256"] = file_sha256(Path(file))
    rec["hash"] = record_hash(rec)
    verify(records + [rec])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    return rec


def head(path: Path) -> str:
    recs = read(path)
    verify(recs)
    return recs[-1]["hash"] if recs else GENESIS


def check_file(path: Path, ledger_records: list[dict], step: str, batch: str) -> None:
    """The file on disk must still have the hash the ledger recorded for (step, batch)."""
    rec = [r for r in ledger_records if r["step"] == step and r.get("batch") == batch]
    if not rec:
        raise LedgerError(f"no {step} record for batch {batch}")
    if file_sha256(path) != rec[-1]["sha256"]:
        raise LedgerError(f"{path.name}: content differs from the ledger ({step}, {batch})")


def git_commit_and_push(ledger_path: Path, message: str, repo_root: Path) -> None:
    """Commit and push only the ledger file (the protocol requires a push after every step)."""
    rel = Path(ledger_path).resolve().relative_to(Path(repo_root).resolve()).as_posix()
    subprocess.run(["git", "-C", str(repo_root), "add", "--", rel], check=True)
    subprocess.run(["git", "-C", str(repo_root), "commit", "-m", message, "--", rel], check=True)
    subprocess.run(["git", "-C", str(repo_root), "push"], check=True)
