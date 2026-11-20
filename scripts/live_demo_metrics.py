"""Helper for scripts/run_college_live_demo.ps1 (college live demonstration). Read-only with respect to the repository's
committed outputs: it never writes into docs/demo/outputs or docs/final/demo/outputs.

    python scripts/live_demo_metrics.py prepare OUTDIR
        Locate the installed cryptography and PyCryptodome packages through imports, record their versions, copy their
        .py files to OUTDIR/sources/<dist>-<version>/ and compute the same tree hash as the committed source manifest.
    python scripts/live_demo_metrics.py report OUTDIR REPORTDIR
        Compute every metric from the freshly written outputs in OUTDIR, validate each CBOM (CycloneDX 1.6 strict) and
        SARIF (2.1.0 schema), compare with the committed reference outputs, and write REPORTDIR/live_demo_metrics.json,
        REPORTDIR/live_demo_report.md and OUTDIR/SHA256_MANIFEST.txt. Nothing in the report is hard-coded: every number
        comes from the live files. The counts describe what the analyser reported, not whether it was right.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import shutil
import sys
import sysconfig
from collections import Counter
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF_REAL = ROOT / "docs" / "final" / "demo" / "outputs" / "real"
REF_DEMO = ROOT / "docs" / "demo" / "outputs"
LIBS = (("cryptography", "cryptography"), ("Crypto", "pycryptodome"))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm_text(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


# ------------------------------------------------------------------------------------------------------------- prepare
def prepare(out: Path) -> int:
    import importlib
    sp = Path(sysconfig.get_paths()["purelib"])
    man = {}
    for pkg, dist in LIBS:
        mod = importlib.import_module(pkg)
        pkg_dir = Path(mod.__file__).resolve().parent
        name = f"{dist}-{version(dist)}"
        files = sorted(pkg_dir.rglob("*.py"))
        h = hashlib.sha256()
        for p in files:
            rel = p.relative_to(pkg_dir.parent)
            q = out / "sources" / name / rel
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, q)
            h.update(rel.as_posix().encode() + b"\0" + p.read_bytes().replace(b"\r\n", b"\n"))
        man[name] = {"import_name": pkg, "distribution": dist, "version": version(dist),
                     "installed_path": str(pkg_dir), "site_packages": str(sp), "py_files": len(files),
                     "tree_sha256": h.hexdigest(), "scan_root": str(out / "sources" / name)}
    ref = json.loads((REF_REAL / "source_manifest.json").read_text(encoding="utf-8"))
    for name, m in man.items():
        r = ref.get(name)
        m["matches_committed_reference_input"] = bool(r and r["tree_sha256"] == m["tree_sha256"]
                                                     and r["py_files"] == m["py_files"])
    (out / "inputs_manifest.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    for name, m in man.items():
        print(f"{name}: {m['py_files']} .py files from {m['installed_path']}; tree {m['tree_sha256'][:16]}...; "
              f"identical to the committed reference input: {m['matches_committed_reference_input']}")
    print("SCANROOT", *[m["scan_root"] for m in man.values()], sep="\n")
    return 0


# -------------------------------------------------------------------------------------------------------------- report
def scan_metrics(doc: dict) -> dict:
    f = doc["findings"]
    rec = [x["recommendation"] for x in f]
    dec = [x["decision"] for x in f]
    n = len(f)
    actions = Counter(r["action"] for r in rec)
    return {
        "tool_version": doc["tool_version"], "policy_version": doc["policy_version"],
        "tier_threshold": doc["tier_threshold"], "arm": doc["arm"],
        "files_scanned": doc["files_scanned"], "files_skipped": len(doc["files_skipped"]),
        "execution_failures": len(doc["execution_failures"]), "semgrep_status": doc["semgrep_status"],
        "sites": n,
        "actions": dict(sorted(actions.items())),
        "action_percent": {k: round(100 * v / n, 1) for k, v in sorted(actions.items())} if n else {},
        "target_classes": dict(sorted(Counter(r["target_class"] for r in rec).items())),
        "roles": dict(sorted(Counter(d["role"] for d in dec).items())),
        "tiers": dict(sorted(Counter(d["tier"] for d in dec).items())),
        "role_x_action": dict(sorted(Counter(f"{d['role']} -> {r['action']}" for d, r in zip(dec, rec)).items())),
        "abstain_reasons": dict(sorted(Counter(r.get("abstain_reason") or "(none)" for r in rec
                                               if r["action"] == "ABSTAIN").items())),
        "excluded_non_pk_sites": len(doc["excluded"]), "unsupported_library_imports": len(doc["unsupported"]),
    }


def keyset(doc: dict) -> Counter:
    return Counter((x["evidence"]["location"]["file"], x["evidence"]["location"]["line"],
                    x["evidence"]["location"]["col"], x["decision"]["role"], x["decision"]["tier"],
                    x["recommendation"]["action"], x["recommendation"]["target_class"]) for x in doc["findings"])


def validate_cbom(text: str) -> str:
    from cyclonedx.schema import SchemaVersion
    from cyclonedx.validation.json import JsonStrictValidator
    err = JsonStrictValidator(SchemaVersion.V1_6).validate_str(text)
    return "VALID (CycloneDX 1.6 strict)" if err is None else f"INVALID: {str(err)[:200]}"


def validate_sarif(doc: dict) -> str:
    import jsonschema
    schema = json.loads((ROOT / "pqscan" / "export" / "schemas" / "sarif-2.1.0.json").read_text(encoding="utf-8"))
    errs = list(jsonschema.Draft4Validator(schema).iter_errors(doc))
    return "VALID (SARIF 2.1.0 schema)" if not errs else f"INVALID: {errs[0].message[:200]}"


def ref_file(name: str, kind: str) -> Path | None:
    if name == "demo-fixture-synthetic":
        p = REF_DEMO / {"summary": "01_summary.txt", "json": "02_scan.json", "cbom": "03_cbom.json",
                        "sarif": "04_scan.sarif"}[kind]
        return p if p.exists() else None
    base = {"summary": f"{name}_summary.txt", "json": f"{name}_scan.json", "cbom": f"{name}_cbom.json",
            "sarif": f"{name}_scan.sarif"}[kind]
    for p in (REF_REAL / base, REF_REAL / (base + ".gz")):
        if p.exists():
            return p
    return None


def read_ref(p: Path) -> bytes:
    return gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes()


def examples(doc: dict, label: str) -> list[dict]:
    """First real finding for each decision path the walkthrough needs (from the live output, never invented)."""
    want = [("SIGN/VERIFY -> ML-DSA (SIG)", lambda r, d: r["action"] == "RECOMMEND" and r["target_class"] == "SIG"),
            ("KEY_ESTABLISHMENT -> ML-KEM redesign (KEM)", lambda r, d: r["action"] == "RECOMMEND" and r["target_class"] == "KEM"),
            ("PK_ENCRYPT/PK_DECRYPT -> KEM + KDF + AEAD (KEM_DEM)", lambda r, d: r["action"] == "RECOMMEND" and r["target_class"] == "KEM_DEM"),
            ("UNKNOWN role -> ABSTAIN", lambda r, d: r["action"] == "ABSTAIN" and d["role"] == "UNKNOWN"),
            ("known role, tier below T2 -> ABSTAIN", lambda r, d: r["action"] == "ABSTAIN" and d["role"] != "UNKNOWN"),
            ("key material only -> FLAG_NO_TARGET (INVENTORY)", lambda r, d: r["target_class"] == "INVENTORY"),
            ("detected PQ/T combination -> NO_ACTION_HYBRID", lambda r, d: r["target_class"] == "NO_ACTION_HYBRID")]
    out = []
    for title, pred in want:
        hit = next((x for x in doc["findings"] if pred(x["recommendation"], x["decision"])), None)
        if hit:
            loc, d, r = hit["evidence"]["location"], hit["decision"], hit["recommendation"]
            out.append({"path": title, "input": label, "site": f"{loc['file']}:{loc['line']}", "role": d["role"],
                        "tier": d["tier"], "action": r["action"], "target_class": r["target_class"],
                        "reason": d["reason"], "target": r["target"], "abstain_reason": r.get("abstain_reason")})
    return out


def report(out: Path, rep: Path) -> int:
    runs = json.loads((out / "runs.json").read_text(encoding="utf-8-sig"))
    inputs = json.loads((out / "inputs_manifest.json").read_text(encoding="utf-8"))
    env = json.loads((out / "environment.json").read_text(encoding="utf-8-sig"))
    scans, problems = {}, []
    for name in ("cryptography-47.0.0", "pycryptodome-4.4.0", "demo-fixture-synthetic"):
        d = out / name
        if not d.exists():
            continue
        doc = json.loads((d / "scan.json").read_text(encoding="utf-8"))
        cbom_text = (d / "cbom.json").read_text(encoding="utf-8")
        sarif = json.loads((d / "scan.sarif").read_text(encoding="utf-8"))
        s = {"metrics": scan_metrics(doc),
             "validation": {"cbom": validate_cbom(cbom_text), "sarif": validate_sarif(sarif)},
             "cbom_components": len(json.loads(cbom_text).get("components", [])),
             "sarif_results": sum(len(r.get("results", [])) for r in sarif.get("runs", [])),
             "reference_comparison": {}}
        for kind, fn in (("summary", "summary.txt"), ("json", "scan.json"), ("cbom", "cbom.json"), ("sarif", "scan.sarif")):
            rp = ref_file(name, kind)
            if rp is None:
                s["reference_comparison"][kind] = "no committed reference"
                continue
            same = norm_text(read_ref(rp)) == norm_text((d / fn).read_bytes())
            s["reference_comparison"][kind] = ("identical after line-ending normalisation" if same
                                               else f"DIFFERENT from {rp.relative_to(ROOT).as_posix()}")
        rp = ref_file(name, "json")
        if rp is not None:
            a, b = keyset(json.loads(read_ref(rp))), keyset(doc)
            s["reference_comparison"]["findings_only_in_reference"] = sum((a - b).values())
            s["reference_comparison"]["findings_only_in_live_run"] = sum((b - a).values())
        for extra in ("T3", "exclude-tests"):
            p = d / f"scan_{extra}.json"
            if p.exists():
                s[f"variant_{extra}"] = scan_metrics(json.loads(p.read_text(encoding="utf-8")))
        s["examples"] = examples(doc, "synthetic fixture (not real-world code)" if "synthetic" in name else f"{name} (real library source)")
        if "INVALID" in s["validation"]["cbom"] or "INVALID" in s["validation"]["sarif"]:
            problems.append(f"{name}: schema validation failed")
        scans[name] = s
    failed = [r for r in runs if r["exit_code"] != 0]
    problems += [f"command failed: {r['label']} (exit {r['exit_code']})" for r in failed]
    metrics = {"status": "OK" if not problems else "PROBLEMS", "problems": problems, "environment": env,
               "inputs": inputs, "runs": runs, "scans": scans,
               "interpretation": ("Counts are what pqscan reported on library-internal source code. They are not "
                                  "accuracy, precision or recall: no labels exist for these files, and these libraries "
                                  "are not representative application repositories.")}
    rep.mkdir(parents=True, exist_ok=True)
    (rep / "live_demo_metrics.json").write_text(json.dumps(metrics, indent=1) + "\n", encoding="utf-8")
    (rep / "live_demo_report.md").write_text(render(metrics), encoding="utf-8")
    lines = [f"{sha(p)}  {p.relative_to(out).as_posix()}" for p in sorted(out.rglob("*"))
             if p.is_file() and "sources" not in p.relative_to(out).parts and p.name != "SHA256_MANIFEST.txt"]
    (out / "SHA256_MANIFEST.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.copyfile(rep / "live_demo_metrics.json", out / "live_demo_metrics.json")
    shutil.copyfile(rep / "live_demo_report.md", out / "live_demo_report.md")
    print("STATUS", metrics["status"], *problems)
    return 0 if not problems else 1


def _t(d: dict) -> str:
    return ", ".join(f"{k} {v}" for k, v in d.items()) or "none"


def render(m: dict) -> str:
    e = m["environment"]
    L = ["# PQScan live demonstration report", "",
         f"Generated by `scripts/run_college_live_demo.ps1` at {e['started_utc']} (UTC). Every number below was computed "
         "from the output files of this run; none is typed in by hand.", "",
         f"**Status: {m['status']}**" + ("" if not m["problems"] else " — " + "; ".join(m["problems"])), "",
         "## Environment", "",
         "| Item | Value |", "|---|---|",
         f"| Repository commit | `{e['git_commit']}` |", f"| Scanner code identical to paper snapshot `f69d81b` | {e['scanner_code_matches_f69d81b']} |",
         f"| pqscan | {e['pqscan_version']} (imported from `{e['pqscan_module']}`) |",
         f"| Python | {e['python']} |", f"| Semgrep | {e['semgrep']} |",
         f"| cryptography | {e['cryptography']} |", f"| PyCryptodome | {e['pycryptodome']} |",
         f"| Output folder | `{e['out_dir']}` |", "",
         "## Inputs (real third-party library source, not application repositories)", "",
         "| Input | .py files | Installed at | Tree SHA-256 | Same as committed reference input |", "|---|---|---|---|---|"]
    for name, i in m["inputs"].items():
        L.append(f"| {name} | {i['py_files']} | `{i['installed_path']}` | `{i['tree_sha256'][:16]}…` | {i['matches_committed_reference_input']} |")
    L += ["", "The synthetic demonstration fixture (`docs/demo/demo_repo`, 7 files written for this project) is scanned as well, "
          "and is always labelled synthetic.", "", "## Commands, exit codes and wall-clock time", "",
          "| Command | Exit | Seconds |", "|---|---|---|"]
    for r in m["runs"]:
        L.append(f"| `{r['label']}` | {r['exit_code']} | {r['seconds']} |")
    for name, s in m["scans"].items():
        x = s["metrics"]
        L += ["", f"## {name}", "",
              "| Metric | Value |", "|---|---|",
              f"| Files scanned / skipped / execution failures | {x['files_scanned']} / {x['files_skipped']} / {x['execution_failures']} |",
              f"| Semgrep | {x['semgrep_status']} |",
              f"| Public-key sites reported | {x['sites']} |",
              f"| Actions | {_t(x['actions'])} |",
              f"| Actions, % of sites | {_t({k: str(v) + '%' for k, v in x['action_percent'].items()})} |",
              f"| Target classes | {_t(x['target_classes'])} |",
              f"| Roles | {_t(x['roles'])} |",
              f"| Evidence tiers | {_t(x['tiers'])} |",
              f"| Abstention reasons | {_t(x['abstain_reasons'])} |",
              f"| Excluded non-public-key sites | {x['excluded_non_pk_sites']} |",
              f"| CBOM | {s['validation']['cbom']}; {s['cbom_components']} components |",
              f"| SARIF | {s['validation']['sarif']}; {s['sarif_results']} results |"]
        for extra, label in (("T3", "Threshold T3 instead of T2"), ("exclude-tests", "`--exclude-tests` (reported separately; not merged)")):
            v = s.get(f"variant_{extra}")
            if v:
                L.append(f"| {label} | sites {v['sites']}; {_t(v['actions'])}; files scanned {v['files_scanned']} |")
        L += ["", "Comparison with the committed reference outputs: " +
              "; ".join(f"{k}: {v}" for k, v in s["reference_comparison"].items()) + ".", ""]
        if s["examples"]:
            L += ["Decision paths found in this live output:", "", "| Path | Site | Role, tier | Action → class | Reason |", "|---|---|---|---|---|"]
            for ex in s["examples"]:
                L.append(f"| {ex['path']} | `{ex['site']}` | {ex['role']}, {ex['tier']} | {ex['action']} → {ex['target_class']} | {ex['reason'][:150]} |")
    L += ["", "## What these numbers mean", "", m["interpretation"],
          "PyCryptodome's sites are mostly in its own self-test files. The evaluation of recommendation correctness on "
          "labelled repositories has not been run; F1 is blocked by the S16 calibration finding "
          "(`docs/audit/ta01_s16_historical_verification.md`).", ""]
    return "\n".join(L)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "prepare":
        sys.exit(prepare(Path(sys.argv[2])))
    if cmd == "report":
        sys.exit(report(Path(sys.argv[2]), Path(sys.argv[3])))
    print(__doc__)
    sys.exit(2)
