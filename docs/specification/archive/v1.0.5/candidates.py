"""Annotation candidate pool and seeded sequential sampler (Dataset B; protocol v1.0.4 Sec. 2; decisions V2, V5, V6, V11).

    python -m pqscan.bench.candidates build --repo <dir> --name <repo> --commit <sha> --run-dir <batch out> --out <dir>
    python -m pqscan.bench.candidates next  --order <dir>/order_<repo>.json --split development \
                                            --issued <issued ids> --labels <final labels.jsonl> [--out batch.jsonl]

Pool (repository_split.md Sec. 3): the union of
* the regex over-approximation, applied to files importing pyca or PyCryptodome (tool-independent, so it can contain
  sites every evaluated tool misses),
* every baseline's findings (parsed by the adapters from a batch-runner output directory),
* pqscan Module A/B locations (findings and Semgrep-only candidates of the `full` arm),
deduplicated by statement: each candidate line is mapped to the start line of the smallest enclosing statement.

Scope classes (V5; first match on the path relative to the repository root; directory and file names are compared
in lower case): vendored (a directory vendor/_vendor/third_party) > test (a directory test/tests/testing, or a file
test_*.py, *_test.py, test.py, tests.py, tests_*.py, tests-*.py, conftest.py) > example (a directory example,
examples, demo, demos or demo*) > app.

Strata (V11; tool-independent): S1-app (file imports a supported library; scope app), S1-nonapp (the same; scope
test, example or vendored) and S2 (all other candidates). Each stratum is put in a seeded random order.

Candidate IDs (V6, M3) are opaque: "C-" + the first 12 hex digits of SHA-256("<seed>|<repo>|<file>|<line>"). They
reveal no stratum, tool or rank. A collision stops the build.

Issuance (V6): B0 = the first 10 S2 candidates, issued once before anything else (M4). B1, B2, ... = 10 candidates:
7 S1-app + min(3, cap - eligible S1-nonapp so far) S1-nonapp (M5); empty slots are filled from the other S1 list,
but non-app issuance never exceeds the remaining cap (M6). cap = quota // 3 (M8). counted = eligible S1-app +
min(eligible S1-nonapp, cap) (M7). Stop at counted >= quota, at 4 x quota issued S1 candidates (M9), or when S1 is
exhausted (M14); the last two are shortfalls. Unresolved eligibility counts as not eligible (M14). The quota comes
from the protocol table QUOTAS; an override needs a logged reason (M10). Eligibility must be a JSON boolean or the
string "unresolved" (M12). Unknown or duplicate candidate IDs are rejected (M13). The issued set is supplied
explicitly (from the issuance ledger, M11); every issued candidate must be labelled before the next batch.
Stopping depends only on adjudicated eligibility, never on any tool's output or correctness.

Outputs for annotators carry locations only (candidate id, repository, commit, file, line); which tools reported a
candidate is written to a separate `pool_sources_<repo>.json` that annotators must not see.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import random
import re
import sys
from pathlib import Path

PROTOCOL = "1.0.4"
ORDER_FORMAT = "pqscan-order/2"
DEFAULT_SEED = 20261113
QUOTAS = {"test": 30, "development": 25, "validation": 25}      # protocol v1.0.4 Sec. 2 (tested against the table)
BATCH, APP_PER_BATCH, NONAPP_PER_BATCH, S2_FIXED, CAP_FACTOR = 10, 7, 3, 10, 4
STRATA = ("S1-app", "S1-nonapp", "S2")

# identical to experiments/bench/verify_candidates.py (a test enforces this)
REGEX = re.compile(r"generate_private_key|load_pem_|load_der_|load_ssh_|RSA\.(generate|import_key|construct)|"
                   r"ECC\.(generate|import_key|construct)|\.import_key\(|\.sign\(|\.verify\(|\.exchange\(|"
                   r"\.encrypt\(|\.decrypt\(|PKCS1_OAEP|PKCS1_v1_5|pkcs1_15|\bpss\b|\bDSS\b|ECDH\(|x25519\.|X25519|"
                   r"rsa\.|ec\.|RSAPrivateKey|RSAPublicKey|EllipticCurve")
PYCA = re.compile(r"^\s*(from|import)\s+cryptography\b", re.M)
PYCRYPTODOME = re.compile(r"^\s*(from|import)\s+(Crypto|Cryptodome)\b", re.M)
SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "build", "dist"}

VENDORED_DIRS = {"vendor", "_vendor", "third_party"}
TEST_DIRS = {"test", "tests", "testing"}
TEST_FILE = re.compile(r"^(test_.*\.py|.*_test\.py|test\.py|tests\.py|tests_.*\.py|tests-.*\.py|conftest\.py)$")
EXAMPLE_DIRS = {"example", "examples", "demo", "demos"}


class SamplerError(ValueError):
    """Invalid input to the sampler: the operation is refused, never repaired."""


def scope_class(rel: str) -> str:
    """V5 scope class of a repository-relative POSIX path: vendored > test > example > app."""
    parts = [p.lower() for p in rel.replace("\\", "/").split("/") if p]
    dirs, name = parts[:-1], (parts[-1] if parts else "")
    if any(d in VENDORED_DIRS for d in dirs):
        return "vendored"
    if any(d in TEST_DIRS for d in dirs) or TEST_FILE.match(name):
        return "test"
    if any(d in EXAMPLE_DIRS or d.startswith("demo") for d in dirs):
        return "example"
    return "app"


def stratum_of(rel: str, imports_supported_library: bool) -> str:
    if not imports_supported_library:
        return "S2"
    return "S1-app" if scope_class(rel) == "app" else "S1-nonapp"


def candidate_id(seed: int, repo: str, file: str, line: int) -> str:
    return "C-" + hashlib.sha256(f"{seed}|{repo}|{file}|{line}".encode("utf-8")).hexdigest()[:12]


def quota_for(split: str, override: int | None = None, reason: str | None = None) -> int:
    """Quota from the protocol table (M10). An override must carry a reason, which the caller logs."""
    if split not in QUOTAS:
        raise SamplerError(f"unknown split {split!r}; expected one of {sorted(QUOTAS)}")
    if override is None:
        return QUOTAS[split]
    if not reason or not reason.strip():
        raise SamplerError("a quota override needs a recorded reason")
    if override <= 0:
        raise SamplerError("quota must be positive")
    return override


def python_files(repo: Path) -> list[Path]:
    out = []
    for p in sorted(repo.rglob("*.py")):
        if any(part in SKIP_DIRS or part.startswith(".") for part in p.relative_to(repo).parts[:-1]) or p.is_symlink():
            continue
        out.append(p)
    return out


def statement_starts(text: str) -> dict[int, int]:
    """Line -> start line of the smallest statement containing it (empty if the file does not parse)."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return {}
    best: dict[int, tuple[int, int]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt) and getattr(node, "end_lineno", None):
            span = node.end_lineno - node.lineno
            body_start = min((c.lineno for f in ("body", "orelse", "finalbody", "handlers")
                              for c in getattr(node, f, []) or []), default=node.end_lineno + 1)
            last = min(node.end_lineno, body_start - 1)    # compound statements own only their header lines
            for ln in range(node.lineno, last + 1):
                if ln not in best or span < best[ln][1]:
                    best[ln] = (node.lineno, span)
    return {ln: v[0] for ln, v in best.items()}


def build_pool(repo: Path, run_dir: Path | None, name: str) -> tuple[list[dict], dict[str, list[str]]]:
    """Candidates (file, line, scope, stratum) and, separately, the sources that reported each one."""
    from ..baselines.adapters import ADAPTERS
    from .run import TOOL_FILES
    texts, lib = {}, {}
    for p in python_files(repo):
        rel = p.relative_to(repo).as_posix()
        texts[rel] = p.read_text(encoding="utf-8", errors="replace")
        lib[rel] = bool(PYCA.search(texts[rel]) or PYCRYPTODOME.search(texts[rel]))
    raw: dict[tuple[str, int], set[str]] = {}
    for rel, text in texts.items():
        if lib[rel]:
            for i, line in enumerate(text.splitlines(), 1):
                if REGEX.search(line):
                    raw.setdefault((rel, i), set()).add("regex")
    if run_dir is not None:
        root = repo.resolve().as_posix().rstrip("/") + "/"
        for tool, pattern in TOOL_FILES.items():
            f = run_dir / pattern.format(repo=name)
            if f.exists():
                for x in ADAPTERS[tool](f):
                    path = x.file.replace("\\", "/")
                    path = path[len(root):] if path.startswith(root) else path.lstrip("./")
                    if path in texts:
                        raw.setdefault((path, int(x.line)), set()).add(tool)
        pq = run_dir / f"pqscan_full_{name}.json"
        if pq.exists():
            d = json.loads(pq.read_text(encoding="utf-8"))
            locs = [(f["evidence"]["location"]["file"], f["evidence"]["location"]["line"]) for f in d["findings"]]
            locs += [(f["file"], f["line"]) for f in d["semgrep_only"]]
            for path, ln in locs:
                if path in texts:
                    raw.setdefault((path, int(ln)), set()).add("pqscan")
    starts = {rel: statement_starts(t) for rel, t in texts.items()}
    merged: dict[tuple[str, int], set[str]] = {}
    for (rel, ln), src in raw.items():
        key = (rel, starts[rel].get(ln, ln))
        merged.setdefault(key, set()).update(src)
    pool, sources = [], {}
    for (rel, ln) in sorted(merged):
        pool.append({"file": rel, "line": ln, "scope": scope_class(rel), "stratum": stratum_of(rel, lib[rel])})
        sources[f"{rel}:{ln}"] = sorted(merged[(rel, ln)])
    return pool, sources


def order_pool(pool: list[dict], name: str, commit: str, seed: int = DEFAULT_SEED) -> dict:
    """Seeded random order per stratum with opaque candidate IDs (collision -> SamplerError)."""
    out = {"format": ORDER_FORMAT, "protocol": PROTOCOL, "repo": name, "commit": commit, "seed": seed, "strata": {}}
    seen: dict[str, tuple[str, int]] = {}
    for stratum in STRATA:
        items = sorted((c for c in pool if c["stratum"] == stratum), key=lambda c: (c["file"], c["line"]))
        random.Random(f"{seed}:{name}:{stratum}").shuffle(items)
        rows = []
        for c in items:
            cid = candidate_id(seed, name, c["file"], c["line"])
            if cid in seen and seen[cid] != (c["file"], c["line"]):
                raise SamplerError(f"candidate-ID collision: {cid} for {seen[cid]} and {(c['file'], c['line'])}")
            if cid in seen:
                raise SamplerError(f"duplicate pool entry {c['file']}:{c['line']}")
            seen[cid] = (c["file"], c["line"])
            rows.append({"candidate_id": cid, "file": c["file"], "line": c["line"], "scope": c["scope"]})
        out["strata"][stratum] = rows
    out["counts"] = {k: len(v) for k, v in out["strata"].items()}
    out["pool_sha256"] = hashlib.sha256(json.dumps(out["strata"], sort_keys=True).encode()).hexdigest()
    return out


def parse_eligibility(value) -> bool | None:
    """JSON boolean -> bool; the string "unresolved" -> None (counts as not eligible). Anything else is refused (M12)."""
    if value is True or value is False:
        return value
    if value == "unresolved":
        return None
    raise SamplerError(f"eligibility must be a JSON boolean or \"unresolved\", got {value!r}")


def _status(order: dict, issued: set[str], eligible: dict[str, bool | None], quota: int) -> dict:
    cap = quota // 3
    app, nonapp = order["strata"]["S1-app"], order["strata"]["S1-nonapp"]
    e_app = sum(eligible.get(c["candidate_id"]) is True for c in app)
    e_nonapp = sum(eligible.get(c["candidate_id"]) is True for c in nonapp)
    n_s1 = sum(c["candidate_id"] in issued for c in app + nonapp)
    return {"quota": quota, "nonapp_cap": cap, "eligible_app": e_app, "eligible_nonapp": e_nonapp,
            "counted": e_app + min(e_nonapp, cap), "s1_issued": n_s1, "s1_limit": CAP_FACTOR * quota,
            "unresolved": sum(v is None for v in eligible.values())}


def next_batch(order: dict, issued: list[str], eligible: dict[str, object], quota: int) -> dict:
    """Next batch to issue, given the issued candidate IDs (in issuance order, from the ledger) and the final
    eligibility of each of them. Refuses (SamplerError) on unknown, duplicate or unlabelled IDs."""
    if order.get("format") != ORDER_FORMAT:
        raise SamplerError(f"order file format {order.get('format')!r} is not {ORDER_FORMAT}; rebuild the order")
    known = {c["candidate_id"] for s in STRATA for c in order["strata"][s]}
    if len(set(issued)) != len(issued):
        raise SamplerError("duplicate candidate ID in the issued list")
    unknown = [c for c in list(issued) + list(eligible) if c not in known]
    if unknown:
        raise SamplerError(f"unknown candidate IDs: {sorted(set(unknown))[:5]}")
    issued_set = set(issued)
    extra = set(eligible) - issued_set
    if extra:
        raise SamplerError(f"labels for candidates that were never issued: {sorted(extra)[:5]}")
    missing = issued_set - set(eligible)
    if missing:
        raise SamplerError(f"{len(missing)} issued candidates have no final label yet; label them before the next batch")
    elig = {k: parse_eligibility(v) for k, v in eligible.items()}
    s2 = order["strata"]["S2"]
    status = _status(order, issued_set, elig, quota)
    if s2 and not any(c["candidate_id"] in issued_set for c in s2):
        return {**status, "stop": None, "batch_kind": "B0", "batch": s2[:S2_FIXED]}       # S2, once, before B1 (M4)
    if status["counted"] >= quota:
        return {**status, "stop": "quota reached", "batch_kind": None, "batch": []}
    if status["s1_issued"] >= CAP_FACTOR * quota:
        return {**status, "stop": "candidate cap reached (shortfall reported)", "batch_kind": None, "batch": []}
    rest_app = [c for c in order["strata"]["S1-app"] if c["candidate_id"] not in issued_set]
    rest_non = [c for c in order["strata"]["S1-nonapp"] if c["candidate_id"] not in issued_set]
    allowed_non = max(0, status["nonapp_cap"] - status["eligible_nonapp"])          # remaining cap (M6)
    room = min(BATCH, CAP_FACTOR * quota - status["s1_issued"])
    take_non = min(len(rest_non), NONAPP_PER_BATCH, allowed_non)
    take_app = min(len(rest_app), room - take_non)
    if take_app + take_non < room:                       # fill empty slots from the other S1 list, cap respected
        take_non = min(len(rest_non), room - take_app, allowed_non)
        take_app = min(len(rest_app), room - take_non)
    if take_app + take_non == 0:
        return {**status, "stop": "S1 exhausted (shortfall reported)", "batch_kind": None, "batch": []}
    return {**status, "stop": None, "batch_kind": "B1+", "batch": rest_app[:take_app] + rest_non[:take_non]}


def annotator_list(order: dict, batch: list[dict]) -> list[dict]:
    """Location-only records for annotators: no stratum, scope, tool or source."""
    return [{"candidate_id": c["candidate_id"], "repo": order["repo"], "commit": order["commit"],
             "file": c["file"], "line": c["line"]} for c in batch]


def read_final_eligibility(path: Path) -> dict[str, object]:
    """Final eligibility per candidate from a final-label file: envelope records {"site": {...}, "meta": {...}}
    (guide v1.1 Sec. 5) or plain {"candidate_id", "eligible"} rows. An eligibility listed in meta.unresolved is
    returned as "unresolved". Values are returned raw so that next_batch validates their type (M12)."""
    out: dict[str, object] = {}
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        if "site" in r and "meta" in r:
            cid, value = r["meta"].get("candidate_id"), r["site"].get("eligible")
            if "eligible" in (r["meta"].get("unresolved") or []):
                value = "unresolved"
        else:
            cid, value = r.get("candidate_id"), r.get("eligible")
        if not cid:
            raise SamplerError(f"{path}:{n}: no candidate_id")
        if cid in out:
            raise SamplerError(f"{path}:{n}: duplicate candidate_id {cid}")
        out[cid] = value
    return out


def read_issued(path: Path) -> list[str]:
    """Issued candidate IDs, one per line or a JSON list (the issuance ledger provides this list)."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        return list(json.loads(text))
    return [json.loads(x)["candidate_id"] if x.lstrip().startswith("{") else x.strip() for x in text.splitlines() if x.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pqscan.bench.candidates")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--repo", type=Path, required=True)
    b.add_argument("--name", required=True)
    b.add_argument("--commit", required=True)
    b.add_argument("--run-dir", type=Path)
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--seed", type=int, default=DEFAULT_SEED)
    n = sub.add_parser("next")
    n.add_argument("--order", type=Path, required=True)
    n.add_argument("--split", choices=sorted(QUOTAS), required=True)
    n.add_argument("--quota-override", type=int)
    n.add_argument("--reason", help="required with --quota-override; recorded in the output")
    n.add_argument("--issued", type=Path, help="issued candidate IDs (from the issuance ledger)")
    n.add_argument("--labels", type=Path, help="final labels of every issued candidate")
    n.add_argument("--out", type=Path, help="write the location-only batch here (jsonl)")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        pool, sources = build_pool(a.repo, a.run_dir, a.name)
        order = order_pool(pool, a.name, a.commit, a.seed)
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / f"order_{a.name}.json").write_text(json.dumps(order, indent=1), encoding="utf-8", newline="\n")
        (a.out / f"pool_sources_{a.name}.json").write_text(json.dumps(sources, indent=1, sort_keys=True),
                                                           encoding="utf-8", newline="\n")
        print(f"{a.name}: {len(pool)} candidates {order['counts']}")
        return 0
    quota = quota_for(a.split, a.quota_override, a.reason)
    order = json.loads(a.order.read_text(encoding="utf-8"))
    issued = read_issued(a.issued) if a.issued and a.issued.exists() else []
    labels = read_final_eligibility(a.labels) if a.labels and a.labels.exists() else {}
    res = next_batch(order, issued, labels, quota)
    if a.out and res["batch"]:
        with a.out.open("w", encoding="utf-8", newline="\n") as f:
            for r in annotator_list(order, res["batch"]):
                f.write(json.dumps(r) + "\n")
    summary = {k: v for k, v in res.items() if k != "batch"} | {"batch_size": len(res["batch"])}
    if a.quota_override is not None:
        summary["quota_override_reason"] = a.reason
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
