"""Command-line interface: `pqscan scan <path>`.

Exit codes: 0 scan completed (with or without findings); 2 usage / input error; 3 internal failure.
"""
from __future__ import annotations
import argparse, json, logging, sys
from pathlib import Path
from . import __version__
from .export import to_cbom, to_sarif, to_json, validate_cbom
from .pipeline import scan
from .policy import load_policy
from .roles import ARMS


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pqscan", description="Post-quantum crypto scanner for Python projects (research prototype)")
    p.add_argument("--version", action="version", version=f"pqscan {__version__}")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan", help="scan a directory of Python source (never executes it)")
    s.add_argument("path", type=Path)
    s.add_argument("--format", choices=["cbom", "sarif", "json", "summary"], default="summary")
    s.add_argument("-o", "--output", type=Path, help="write the report here instead of stdout")
    s.add_argument("--policy", type=Path, help="policy YAML (default: bundled policy v1.1)")
    s.add_argument("--tier-threshold", choices=["T0", "T1", "T2", "T3"], help="override the policy threshold (default T2)")
    s.add_argument("--arm", choices=ARMS, default="full", help="evidence arm (ablation); default full")
    s.add_argument("--exclude-tests", action="store_true", help="skip test files")
    s.add_argument("--no-semgrep", action="store_true", help="skip Module A (Semgrep) candidates")
    s.add_argument("--max-file-bytes", type=int, default=2_000_000)
    s.add_argument("--file-timeout", type=float, default=30.0)
    s.add_argument("--timestamp", help="ISO timestamp to record in the CBOM (omitted by default for reproducibility)")
    s.add_argument("-v", "--verbose", action="store_true")
    return p


def _summary(res) -> str:
    from collections import Counter
    acts = Counter(f.recommendation.action for f in res.findings)
    classes = Counter(f.recommendation.target_class for f in res.findings)
    lines = [f"pqscan {res.tool_version} | policy {res.policy_version} | threshold {res.tier_threshold} | arm {res.arm}",
             f"files scanned: {res.files_scanned}, skipped: {len(res.files_skipped)}, execution failures: {len(res.errors)}, semgrep: {res.semgrep_status}",
             f"sites: {len(res.findings)} ({', '.join(f'{k}={v}' for k, v in sorted(acts.items()))}); excluded non-PK sites: {len(res.excluded)}; "
             f"unsupported-library imports: {len(res.unsupported)} ({', '.join(sorted({u['library'] for u in res.unsupported})) or 'none'})",
             "target classes: " + ", ".join(f"{k}={v}" for k, v in sorted(classes.items())), ""]
    for f in res.findings:
        loc = f.evidence.candidate.location
        lines.append(f"{loc.file}:{loc.line}  {f.decision.algorithm:<8} {(f.decision.role.value if f.decision.role else '-'):<18} "
                     f"{f.decision.tier.value}  {f.recommendation.action:<14} {f.recommendation.target_class}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO if getattr(args, "verbose", False) else logging.WARNING, format="%(levelname)s %(message)s")
    if args.command != "scan":
        return 2
    if not args.path.is_dir():
        print(f"error: not a directory: {args.path}", file=sys.stderr)
        return 2
    try:
        policy = load_policy(args.policy, args.tier_threshold)
        res = scan(args.path, policy=policy, arm=args.arm, include_tests=not args.exclude_tests,
                   max_bytes=args.max_file_bytes, file_timeout_s=args.file_timeout, run_semgrep_rules=not args.no_semgrep)
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"internal error: {e.__class__.__name__}: {e}", file=sys.stderr)
        return 3
    if args.format == "cbom":
        doc = to_cbom(res, args.timestamp)
        errs = validate_cbom(doc)
        if errs:
            print("error: generated CBOM failed CycloneDX 1.6 validation: " + errs[0][:500], file=sys.stderr)
            return 3
        text = json.dumps(doc, indent=2, sort_keys=False)
    elif args.format == "sarif":
        text = json.dumps(to_sarif(res), indent=2)
    elif args.format == "json":
        text = json.dumps(to_json(res), indent=2, default=str)
    else:
        text = _summary(res)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    return 0


def app() -> None:  # console-script entry point
    sys.exit(main())


if __name__ == "__main__":
    app()
