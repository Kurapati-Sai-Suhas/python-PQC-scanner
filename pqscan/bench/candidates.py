"""Annotation candidate pool and seeded sequential sampler (Dataset B; protocol v1.0.3 Sec. 2, owner decisions D2/D3).

    python -m pqscan.bench.candidates build  --repo <dir> --name <repo> --commit <sha> --run-dir <batch out> --out <dir>
    python -m pqscan.bench.candidates next   --order <dir>/order_<repo>.json --labels <adjudicated.jsonl> --quota 30

Pool (repository_split.md Sec. 3): the union of
* the regex over-approximation, applied to files importing pyca or PyCryptodome (tool-independent, so it can contain
  sites every evaluated tool misses),
* every baseline's findings (parsed by the adapters from a batch-runner output directory),
* pqscan Module A/B locations (findings and Semgrep-only candidates of the `full` arm),
deduplicated by statement: each candidate line is mapped to the start line of the smallest enclosing statement, so a
multi-line call reported at different lines by different tools is one candidate.

Strata (tool-independent): S1-app and S1-test (candidate in a file importing a supported library; test path or not)
and S2 (all other candidates). Each stratum is put in a seeded random order (seed recorded in the freeze record).

Sequential rule (O2): batches of 10 per repository, normally 7 S1-app + 3 S1-test; test-path draws stop once the
adjudicated eligible test-path count reaches the cap (quota // 3), and empty slots go to the other S1 list. The first
batch also includes the first 10 S2 candidates (fixed, measured once). Sampling stops when
eligible_app + min(eligible_test, cap) >= quota, when 4 x quota S1 candidates have been issued, or when S1 is
exhausted (a shortfall that is reported). Stopping depends only on adjudicated eligibility, never on any tool's
correctness.

Outputs for annotators carry locations only (candidate id, repository, commit, file, line); which tools reported a
candidate is written to a separate `pool_sources_<repo>.json` that annotators must not see.
"""
from __future__ import annotations
import argparse, ast, hashlib, json, random, re, sys
from pathlib import Path

DEFAULT_SEED = 20261113
BATCH, APP_PER_BATCH, TEST_PER_BATCH, S2_FIXED, CAP_FACTOR = 10, 7, 3, 10, 4

# identical to experiments/bench/verify_candidates.py (a test enforces this)
REGEX = re.compile(r"generate_private_key|load_pem_|load_der_|load_ssh_|RSA\.(generate|import_key|construct)|"
                   r"ECC\.(generate|import_key|construct)|\.import_key\(|\.sign\(|\.verify\(|\.exchange\(|"
                   r"\.encrypt\(|\.decrypt\(|PKCS1_OAEP|PKCS1_v1_5|pkcs1_15|\bpss\b|\bDSS\b|ECDH\(|x25519\.|X25519|"
                   r"rsa\.|ec\.|RSAPrivateKey|RSAPublicKey|EllipticCurve")
PYCA = re.compile(r"^\s*(from|import)\s+cryptography\b", re.M)
PYCRYPTODOME = re.compile(r"^\s*(from|import)\s+(Crypto|Cryptodome)\b", re.M)
TEST_PATH = re.compile(r"(^|/)(tests?|testing)(/|$)|(^|/)test_[^/]*\.py$|_test\.py$")
SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "build", "dist"}


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
    """Candidates (file, line, stratum) and, separately, the sources that reported each one."""
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
        stratum = ("S1-test" if TEST_PATH.search(rel) else "S1-app") if lib[rel] else "S2"
        pool.append({"file": rel, "line": ln, "stratum": stratum})
        sources[f"{rel}:{ln}"] = sorted(merged[(rel, ln)])
    return pool, sources


def order_pool(pool: list[dict], name: str, commit: str, seed: int = DEFAULT_SEED) -> dict:
    """Seeded random order per stratum; candidate ids follow the order within each stratum."""
    out = {"repo": name, "commit": commit, "seed": seed, "strata": {}}
    for stratum in ("S1-app", "S1-test", "S2"):
        items = sorted((c for c in pool if c["stratum"] == stratum), key=lambda c: (c["file"], c["line"]))
        random.Random(f"{seed}:{name}:{stratum}").shuffle(items)
        out["strata"][stratum] = [{"candidate_id": f"C-{name}-{stratum}-{i + 1:04d}", "file": c["file"], "line": c["line"]}
                                  for i, c in enumerate(items)]
    out["pool_sha256"] = hashlib.sha256(json.dumps(out["strata"], sort_keys=True).encode()).hexdigest()
    return out


def next_batch(order: dict, eligible: dict[str, bool], quota: int) -> dict:
    """Next candidates to annotate, given adjudicated eligibility of every candidate issued so far.

    `eligible` maps candidate_id -> adjudicated eligible. Issued = everything already labelled (sampling is
    sequential, so labels exist for all issued candidates before the next batch)."""
    cap = quota // 3
    app, test, s2 = (order["strata"][k] for k in ("S1-app", "S1-test", "S2"))
    issued = set(eligible)
    e_app = sum(eligible.get(c["candidate_id"], False) for c in app)
    e_test = sum(eligible.get(c["candidate_id"], False) for c in test)
    counted = e_app + min(e_test, cap)
    n_s1 = sum(c["candidate_id"] in issued for c in app + test)
    status = {"eligible_app": e_app, "eligible_test": e_test, "test_cap": cap, "counted": counted, "quota": quota,
              "s1_issued": n_s1, "s1_limit": CAP_FACTOR * quota}
    if counted >= quota:
        return {**status, "stop": "quota reached", "batch": []}
    if n_s1 >= CAP_FACTOR * quota:
        return {**status, "stop": "candidate cap reached (shortfall reported)", "batch": []}
    rest_app = [c for c in app if c["candidate_id"] not in issued]
    rest_test = [c for c in test if c["candidate_id"] not in issued] if e_test < cap else []
    if not rest_app and not rest_test:
        return {**status, "stop": "S1 exhausted (shortfall reported)", "batch": []}
    room = min(BATCH, CAP_FACTOR * quota - n_s1)
    take_test = min(len(rest_test), TEST_PER_BATCH if rest_app else room)
    take_app = min(len(rest_app), room - take_test)
    take_test = min(len(rest_test), room - take_app)        # fill empty app slots with test-path candidates
    batch = rest_app[:take_app] + rest_test[:take_test]
    if not any(c["candidate_id"] in issued for c in s2):
        batch += s2[:S2_FIXED]                               # S2 measured once, in the first batch
    return {**status, "stop": None, "batch": batch}


def annotator_list(order: dict, batch: list[dict]) -> list[dict]:
    """Location-only records for annotators: no stratum, no tool, no source."""
    return [{"candidate_id": c["candidate_id"], "repo": order["repo"], "commit": order["commit"],
             "file": c["file"], "line": c["line"]} for c in batch]


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
    n.add_argument("--labels", type=Path, help="adjudicated labels (jsonl with candidate_id, eligible)")
    n.add_argument("--quota", type=int, required=True)
    n.add_argument("--out", type=Path, help="write the location-only batch here (jsonl)")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        pool, sources = build_pool(a.repo, a.run_dir, a.name)
        order = order_pool(pool, a.name, a.commit, a.seed)
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / f"order_{a.name}.json").write_text(json.dumps(order, indent=1), encoding="utf-8")
        (a.out / f"pool_sources_{a.name}.json").write_text(json.dumps(sources, indent=1, sort_keys=True), encoding="utf-8")
        print(f"{a.name}: {len(pool)} candidates " + str({k: len(v) for k, v in order["strata"].items()}))
        return 0
    order = json.loads(a.order.read_text(encoding="utf-8"))
    labels = {}
    if a.labels and a.labels.exists():
        for line in a.labels.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                labels[r["candidate_id"]] = bool(r["eligible"])
    res = next_batch(order, labels, a.quota)
    if a.out and res["batch"]:
        with a.out.open("w", encoding="utf-8", newline="\n") as f:
            for r in annotator_list(order, res["batch"]):
                f.write(json.dumps(r) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "batch"} | {"batch_size": len(res["batch"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
