"""F1 readiness check and DRAFT freeze package (protocol Sec. 6, Stage F1, items 1-9). Never performs F1.

    python scripts/f1_readiness.py            # prints the checklist; exit 1 while any prerequisite is missing
    python scripts/f1_readiness.py --write    # also writes docs/freeze_preparation/f1_package_DRAFT/f1_readiness.{json,md}

This script never writes the real freeze record (docs/freeze/pretest_freeze.json), never creates the tag
`phase3-pretest-freeze`, never fetches or opens a test repository and never reads labels. It computes the hashes F1
will need, verifies the confirmed eight-member H4 Part 1 set, checks that the test split is still unopened, and lists
every prerequisite that is still missing (human review, annotation, reliability, owner decisions, explicit approval).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "freeze_preparation" / "f1_package_DRAFT"
FREEZE_RECORD = ROOT / "docs" / "freeze" / "pretest_freeze.json"
FREEZE_TAG = "phase3-pretest-freeze"
ITEM2_DOCS = [
    "docs/specification/role_taxonomy.md", "pqscan/policy/policy_v1_1.yaml", "docs/specification/recommendation_policy.md",
    "docs/specification/scoring_policy.md", "docs/specification/evaluation_protocol.md",
    "docs/specification/phase3_analysis_plan.md", "docs/specification/phase3_decisions.md",
    "docs/specification/data_dictionary.md", "docs/benchmark/annotation_guide.md", "docs/benchmark/benchmark_schema.json",
    "docs/benchmark/meta_schema.json", "docs/specification/run_specification_pre_f1.md",
    "docs/specification/run_specification_pre_f1.json",
]
STAT_CODE = ["pqscan/bench/h2.py", "pqscan/bench/stats.py", "pqscan/bench/judge.py", "pqscan/bench/matching.py",
             "pqscan/bench/fa.py", "pqscan/bench/h4.py", "pqscan/bench/reliability.py"]
H4_PART1 = ("pqcheck", "pqc-audit", "PostQuant", "qsafe", "QSA-regex", "pqblocks-scan",
            "pqscan:B1-algorithm", "pqscan:B2-method-args")
# Third-review findings that settle how a hypothesis is computed or how sites are labelled (owner decisions; F1 or
# annotation prerequisites). Source: docs/review/spec_review_v1.0.5-r3/review_outputs/third_ai_review_report.md
OPEN_DECISIONS = {
    "before annotation": ["TA06 PROTOCOL_CONFIG examples", "TA07 escaped single-purpose keys",
                          "TA11 PyCryptodome split idiom", "TA19 hybrid_component roles"],
    "before F1": ["TA01 S16 exemption", "TA03 H3 harmful-rate definition", "TA04 H4 quantifier",
                  "TA05 H4 synthetic split", "TA08 H1a numerator", "TA09 kappa statistic", "TA10 api_coverage.md hash",
                  "TA28 H3 bootstrap procedure", "W6 policy citation", "N1 PyCryptodome PQ modules"],
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def test_split_unopened() -> tuple[bool, str]:
    manifest = json.loads((ROOT / "benchmark/real/manifest.json").read_text(encoding="utf-8"))
    names = [e["repo"].replace("/", "__") for e in manifest["splits"]["test"]]
    real_files = sorted(p.name for p in (ROOT / "benchmark/real").iterdir())
    cache = ROOT / ".cache" / "repos"
    present = [n for n in names for d in (cache, cache / "test") if (d / n).exists() or (d / n.split("__")[-1]).exists()]
    ok = real_files == ["manifest.json"] and not present
    return ok, f"{len(names)} test repositories; benchmark/real holds {real_files}; local checkouts found: {present or 'none'}"


def run() -> dict:
    items, missing = [], []

    def item(no, name, status, detail):
        items.append({"item": no, "name": name, "status": status, "detail": detail})
        if status == "MISSING":
            missing.append(f"{no} {name}: {detail}")

    head = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=no"))
    tree = subprocess.run([sys.executable, "scripts/tree_hash.py"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    item("1", "commit and source-tree fingerprint", "COMPUTED", {"head": head, "tracked_changes": dirty, "tree": tree})
    item("2", "SHA-256 of the normative documents", "COMPUTED", {d: sha(ROOT / d) for d in ITEM2_DOCS})
    item("2+", "api_coverage.md (TA10: not yet in the item-2 list)", "COMPUTED",
         {"docs/specification/api_coverage.md": sha(ROOT / "docs/specification/api_coverage.md")}
         if (ROOT / "docs/specification/api_coverage.md").exists() else "file not found")
    item("3", "tau, thresholds and decision rules", "COMPUTED", "recorded in the item-2 documents (hashed above)")
    item("4", "baseline manifest", "COMPUTED", {"benchmark/baselines_manifest.json": sha(ROOT / "benchmark/baselines_manifest.json")})
    item("5", "sampling frame and rule", "COMPUTED", {"benchmark/real/manifest.json": sha(ROOT / "benchmark/real/manifest.json"),
                                                      "pqscan/bench/candidates.py": sha(ROOT / "pqscan/bench/candidates.py")})
    ledger = ROOT / "benchmark" / "ledger"
    item("6a", "frozen DV labels and ledger heads", "MISSING" if not ledger.exists() else "PRESENT",
         "no annotation has taken place (no benchmark/ledger/)" if not ledger.exists() else str(ledger))
    item("6b", "synthetic dataset hashes", "COMPUTED", {p: sha(ROOT / p) for p in
         ("benchmark/synthetic/manifest.json", "benchmark/synthetic/sites.jsonl", "benchmark/synthetic/validation_subset.csv")})
    item("7", "hypotheses and families", "COMPUTED", "in the item-2 documents")
    e_driver = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "scripts").glob("*experiment*"))
    item("8", "experiment commands F1->F2 and E", "MISSING" if not e_driver else "PRESENT",
         e_driver or "no Experiment E driver or command list yet (third review TA17 notes the E driver is still to write)")
    item("9a", "AI interface identity, prompt and packet-rule hashes", "COMPUTED",
         {p: sha(ROOT / p) for p in ("docs/benchmark/ai_review_identity.json", "docs/benchmark/ai_review_prompt_v1.md",
                                     "pqscan/bench/packets.py")})
    item("9b", "Phase DV reliability results", "MISSING", "needs DV labels and the >= 14-day re-label")
    item("9c", "frame-audit result", "MISSING", "needs the owner's blind whole-file audit (pqscan/bench/frame_audit.py)")
    completed = sorted((ROOT / "docs/review/forms/completed").glob("external_spec_review_*.md"))
    item("9d", "specification-review record: EXTERNAL HUMAN REVIEW (mandatory, F14)",
         "PRESENT" if completed else "MISSING",
         [str(p.relative_to(ROOT)) for p in completed] or "no completed external human review form; AI reviews do not count")
    item("9e", "Phase DV feasibility check (c_DV, k_r)", "MISSING", "needs DV labels")
    item("9f", "production statistical code hashes", "COMPUTED", {p: sha(ROOT / p) for p in STAT_CODE})
    item("9g", "calibration evidence", "COMPUTED", {p: sha(ROOT / p) for p in (
        "docs/implementation/acceptance/statistical_acceptance.json", "docs/implementation/acceptance/fa_type1.json",
        "docs/implementation/acceptance/g10_calibration.json")})
    att = sorted((ROOT / "docs/audit").glob("source_attribution_access_attestation_2*.md"))
    item("9h", "source-attribution access attestation (G11)", "PRESENT" if att else "MISSING",
         [str(p.relative_to(ROOT)) for p in att] or "only the template exists; the owner signs it at F1")
    spec = json.loads((ROOT / "docs/specification/run_specification_pre_f1.json").read_text(encoding="utf-8"))
    part1 = tuple(spec["interpretations"]["H-6 (H4)"]["tool_inventory_G08"]["decision_set_part1"])
    item("H4", "H4 Part 1 = the eight confirmed F-A baselines (owner decision 19 Nov 2026)",
         "VERIFIED" if part1 == H4_PART1 == tuple(spec["families"]["F-A"]["baselines"]) else "MISMATCH", list(part1))
    ok, detail = test_split_unopened()
    item("T", "test split unopened", "VERIFIED" if ok else "VIOLATION", detail)
    item("D", "open owner decisions from the third AI review", "MISSING", OPEN_DECISIONS)
    missing.append("explicit owner approval of F1 (not given)")
    tag = git("tag", "-l", FREEZE_TAG)
    return {"status": "NOT READY - DRAFT, NOT APPROVED" if missing else "READY FOR OWNER APPROVAL (not approved)",
            "freeze_record_exists": FREEZE_RECORD.exists(), "freeze_tag_exists": bool(tag),
            "items": items, "missing_prerequisites": missing}


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    r = run()
    for i in r["items"]:
        print(f"{i['item']:>3}  {i['status']:<9} {i['name']}")
    print("\nSTATUS:", r["status"])
    for m in r["missing_prerequisites"]:
        print("  missing:", m if len(m) < 160 else m[:157] + "...")
    if "--write" in args:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "f1_readiness.json").write_text(json.dumps(r, indent=1) + "\n", encoding="utf-8", newline="\n")
        print("wrote", (OUT / "f1_readiness.json").relative_to(ROOT))
    return 0 if r["status"].startswith("READY") else 1


if __name__ == "__main__":
    sys.exit(main())
