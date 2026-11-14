"""SARIF 2.1.0 export: one result per role-bearing site."""
from __future__ import annotations
from typing import Any
from ..pipeline import ScanResult

LEVEL = {"RECOMMEND": "warning", "ABSTAIN": "note", "FLAG_NO_TARGET": "note"}


def to_sarif(res: ScanResult) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    results = []
    for f in res.findings:
        r, d = f.recommendation, f.decision
        rid = f"pqscan/{r.action.lower()}/{(d.role.value if d.role else 'NONE').lower()}"
        rules.setdefault(rid, {"id": rid, "shortDescription": {"text": f"{r.action} for role {d.role.value if d.role else 'NONE'}"}})
        loc = f.evidence.candidate.location
        results.append({
            "ruleId": rid, "level": LEVEL.get(r.action, "note"),
            "message": {"text": f"{d.algorithm} {d.role.value if d.role else ''} [{d.tier.value}] -> {r.target_class}: {r.rationale}"},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": loc.file},
                                                "region": {"startLine": loc.line, "startColumn": loc.col,
                                                           "endLine": loc.end_line, "endColumn": loc.end_col}}}],
            "properties": {"tier": d.tier.value, "targetClass": r.target_class, "policyVersion": r.policy_version, "scope": f.scope},
        })
    return {"$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0",
            "runs": [{"tool": {"driver": {"name": "pqscan", "version": res.tool_version, "rules": sorted(rules.values(), key=lambda x: x["id"])}},
                      "results": results,
                      "invocations": [{"executionSuccessful": not res.errors,
                                       "toolExecutionNotifications": [{"level": "error", "message": {"text": f"{e['file']}: {e['error']}"}} for e in res.errors]}]}]}
