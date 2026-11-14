"""Full machine-readable report (evidence, decision, recommendation per site, plus run metadata)."""
from __future__ import annotations
from typing import Any
from ..pipeline import ScanResult


def to_json(res: ScanResult) -> dict[str, Any]:
    return {
        "tool": "pqscan", "tool_version": res.tool_version, "policy_version": res.policy_version,
        "tier_threshold": res.tier_threshold, "arm": res.arm, "files_scanned": res.files_scanned,
        "semgrep_status": res.semgrep_status, "semgrep_errors": res.semgrep_errors,
        "findings": [{"evidence": f.evidence.to_dict(), "decision": f.decision.to_dict(), "recommendation": f.recommendation.to_dict(),
                      "scope": f.scope, "semgrep_rules": f.semgrep_rules} for f in res.findings],
        "excluded": res.excluded, "semgrep_only": res.semgrep_only, "unsupported": res.unsupported,
        "execution_failures": res.errors, "files_skipped": res.files_skipped,
    }
