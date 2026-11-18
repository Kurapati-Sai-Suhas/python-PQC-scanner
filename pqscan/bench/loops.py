"""Pilot and synthetic validation loops (R4-20 step 4; protocol v1.0.4 Sec. 3: "Synthetic subset, pilot and
specification review. These follow the same loop.").

Two extra annotation phases for `pqscan.bench.annotate`, using the same issue -> primary -> prompt -> ai -> compare ->
adjudicate steps, the same hash-chained ledger (`benchmark/ledger/<phase>/`) and the same git-ignored work tree
(`benchmark/annotation/<phase>/<repo>/`):

* phase `pilot`: the 31 pilot sites (`docs/pilot/h1_pilot_sites.csv`), repositories `paramiko` and `python-jose`,
  labelled from the pinned pilot checkouts in `.cache/repos/<repo>/` (`scripts/fetch_pinned.py repos`).
* phase `synthetic`: the 78-instance blind validation subset of Dataset A (`benchmark/synthetic/validation_subset.csv`),
  pseudo-repository `synthetic`.

Blinding, as built into this module:
* Only locations are issued (opaque candidate ID, repository, commit, file, line). Earlier pilot labels and the
  generator's labels (`benchmark/synthetic/sites.jsonl`) are never written to the work tree before the reference step.
* Synthetic paths and site IDs encode the base case and hence the answer (e.g. `cases/pyca-rsa-key-sign/...`), and line 1
  of every case file is a docstring naming the case and the generator. The owner therefore labels a BLINDED COPY:
  `items/<candidate_id>.py`, identical to the case file except that line 1 is replaced by a neutral docstring
  (`BLIND_HEADER`); every other line and every line number is unchanged (checked).
* The reference comparison (owner-final labels vs the earlier pilot labels or the generator's labels) is refused until
  every item has been issued and every batch adjudicated, so the reference can never influence a label.

Not applied to these loops (they are reported separately): quotas and eligibility-based stopping (every item is
labelled), the packet-first subset (defined only for phases DV and T) and the intra-rater re-label rule.
Issue order: ascending opaque candidate ID (a seeded hash, so effectively random and reproducible), batches of 10.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from . import candidates as C
from .labels import COMPARED_FIELDS

LOOP_PHASES = ("pilot", "synthetic")
LOOP_SEED = 20261113
BATCH = 10
BLIND_HEADER = '"""Code fragment for review. Never executed."""'
_SYN_HEADER = re.compile(r'"""Synthetic case \S+ / \S+ \(pqscan synthetic generator [\d.]+\)\. Never executed\."""')
PILOT_REPOS = ("paramiko", "python-jose")
SYN_REPO = "synthetic"


class LoopError(ValueError):
    pass


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def items(phase: str, repo: str, root: Path) -> list[dict]:
    """Location-only items of one loop repository, in issue order. No label field is read into the result."""
    if phase == "pilot":
        if repo not in PILOT_REPOS:
            raise LoopError(f"pilot repository must be one of {PILOT_REPOS}, not {repo!r}")
        commit = json.loads((root / "docs/pilot/pilot_manifest.json").read_text(encoding="utf-8"))["pilot_repositories"][repo]["commit"]
        out = [{"candidate_id": C.candidate_id(LOOP_SEED, f"pilot:{repo}", r["file"], int(r["line_start"])),
                "repo": repo, "commit": commit, "file": r["file"], "line": int(r["line_start"])}
               for r in _rows(root / "docs/pilot/h1_pilot_sites.csv") if r["repo"] == repo]
    elif phase == "synthetic":
        if repo != SYN_REPO:
            raise LoopError(f"the synthetic loop has one pseudo-repository {SYN_REPO!r}, not {repo!r}")
        gen = json.loads((root / "benchmark/synthetic/manifest.json").read_text(encoding="utf-8"))["generator_sha256"]
        out = []
        for r in _rows(root / "benchmark/synthetic/validation_subset.csv"):
            cid = C.candidate_id(LOOP_SEED, SYN_REPO, r["file"], int(r["line_start"]))
            out.append({"candidate_id": cid, "repo": SYN_REPO, "commit": f"generator-{gen[:12]}",
                        "file": f"items/{cid}.py", "line": int(r["line_start"])})
    else:
        raise LoopError(f"{phase!r} is not a loop phase {LOOP_PHASES}")
    ids = [i["candidate_id"] for i in out]
    if len(set(ids)) != len(ids):
        raise LoopError("candidate ID collision")
    return sorted(out, key=lambda i: i["candidate_id"])


def next_batch(all_items: list[dict], issued: list[str]) -> dict:
    """The next up-to-10 items not yet issued; refuses IDs that do not belong to the loop."""
    known = {i["candidate_id"] for i in all_items}
    unknown = [c for c in issued if c not in known]
    if unknown:
        raise LoopError(f"unknown candidate IDs in the ledger: {unknown[:3]}")
    rest = [i for i in all_items if i["candidate_id"] not in set(issued)]
    if not rest:
        return {"stop": "all items issued", "batch": [], "issued": len(issued), "total": len(all_items)}
    return {"stop": None, "batch": rest[:BATCH], "issued": len(issued), "total": len(all_items)}


def _synthetic_source(root: Path) -> dict[str, Path]:
    """candidate_id -> original case file (resolved only inside tooling; never written to the work tree)."""
    return {C.candidate_id(LOOP_SEED, SYN_REPO, r["file"], int(r["line_start"])): root / "benchmark/synthetic" / r["file"]
            for r in _rows(root / "benchmark/synthetic/validation_subset.csv")}


def blind_copy(src: Path, dest: Path) -> None:
    """Copy a synthetic case file, replacing only its line-1 generator docstring. Line count and lines 2.. unchanged."""
    lines = src.read_text(encoding="utf-8").split("\n")
    if not lines or not _SYN_HEADER.fullmatch(lines[0]):
        raise LoopError(f"{src.name}: unexpected line 1; refusing to build a blinded copy")
    out = [BLIND_HEADER] + lines[1:]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out), encoding="utf-8", newline="\n")
    back = dest.read_text(encoding="utf-8").split("\n")
    if len(back) != len(lines) or back[1:] != lines[1:]:
        raise LoopError(f"{src.name}: blinded copy differs beyond line 1")


def checkout(phase: str, repo: str, root: Path, work: Path) -> Path:
    """The directory the owner labels from and packets are built from."""
    if phase == "pilot":
        return root / ".cache" / "repos" / repo
    return work


def prepare_batch(phase: str, batch: list[dict], root: Path, work: Path) -> None:
    """Synthetic: write the blinded copies of this batch into the work tree. Pilot: check the checkout exists."""
    if phase == "synthetic":
        src = _synthetic_source(root)
        for i in batch:
            blind_copy(src[i["candidate_id"]], work / i["file"])
    else:
        base = checkout(phase, batch[0]["repo"], root, work) if batch else None
        if base is not None and not base.is_dir():
            raise LoopError(f"pilot checkout {base} missing; run scripts/fetch_pinned.py repos .cache/repos")


# ---------------------------------------------------------------- pilot sites exposed in the annotation guide
# Owner decision (pilot exposure): the worked examples of annotation guide Sec. 7 are pilot sites whose labels the
# owner has read. They are kept in the pilot loop as a separately reported subset; their agreement with the AI review
# or the earlier labels is never counted as blind evidence. (repo, file name, line); a test ties this to the guide.
GUIDE_EXPOSED_PILOT = frozenset({
    ("paramiko", "kex_ecdh_nist.py", 59), ("paramiko", "kex_mlkem.py", 112), ("paramiko", "pkey.py", 195),
    ("python-jose", "cryptography_backend.py", 208), ("python-jose", "cryptography_backend.py", 252),
})


def guide_exposed(phase: str, repo: str, root: Path) -> set[str]:
    """Candidate IDs of the guide-exposed pilot sites of one loop repository (empty outside the pilot)."""
    if phase != "pilot":
        return set()
    return {i["candidate_id"] for i in items(phase, repo, root)
            if (repo, Path(i["file"]).name, i["line"]) in GUIDE_EXPOSED_PILOT}


# ---------------------------------------------------------------- reference comparison (after the loop only)
def _bool(v):
    if isinstance(v, bool) or v is None:
        return v
    s = str(v).strip().lower()
    return {"yes": True, "true": True, "no": False, "false": False}.get(s)          # 'n/a' or '' -> None


def _roles(v) -> list[str]:
    if v is None or v == "":
        return []
    if isinstance(v, str):
        return sorted(x for x in v.split("|") if x)
    return sorted(v)


def normalise(field: str, value):
    if field in ("eligible", "hybrid_component", "obvious_from_name"):
        return _bool(value)
    if field == "possible_roles":
        return _roles(value)
    return value if value not in ("", None) else None


def reference_labels(phase: str, repo: str, root: Path) -> dict[str, dict]:
    """candidate_id -> the 8 compared fields of the reference (pilot: Phase 1-2 developer labels, circular;
    synthetic: the generator's labels by construction)."""
    out = {}
    if phase == "pilot":
        for r in _rows(root / "docs/pilot/h1_pilot_sites.csv"):
            if r["repo"] == repo:
                cid = C.candidate_id(LOOP_SEED, f"pilot:{repo}", r["file"], int(r["line_start"]))
                out[cid] = {f: normalise(f, r.get(f)) for f in COMPARED_FIELDS}
    else:
        subset = {(r["file"], int(r["line_start"])) for r in _rows(root / "benchmark/synthetic/validation_subset.csv")}
        for line in (root / "benchmark/synthetic/sites.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if (r["file"], int(r["line_start"])) in subset:
                    cid = C.candidate_id(LOOP_SEED, SYN_REPO, r["file"], int(r["line_start"]))
                    out[cid] = {f: normalise(f, r.get(f)) for f in COMPARED_FIELDS}
    return out


def reference_compare(finals: list[dict], reference: dict[str, dict]) -> dict:
    """Owner-final labels vs the reference on the 8 compared fields. A reference value of None means 'not recorded'."""
    rows, missing = [], []
    for rec in finals:
        if rec["meta"].get("annotator_added"):
            continue
        cid = rec["meta"]["candidate_id"]
        ref = reference.get(cid)
        if ref is None:
            missing.append(cid)
            continue
        for f in COMPARED_FIELDS:
            rv, ov = ref.get(f), normalise(f, rec["site"].get(f))
            if rv is None:
                continue
            if ov != rv:
                rows.append({"candidate_id": cid, "field": f, "owner_final": json.dumps(ov), "reference": json.dumps(rv)})
    return {"disagreements": rows, "compared": len(finals) - len(missing), "no_reference": missing}
