"""CycloneDX 1.6 CBOM export.

One `cryptographic-asset` component per role-bearing site:
  * operation sites -> assetType `algorithm` with primitive, padding, curve and cryptoFunctions;
  * key-material sites -> assetType `related-crypto-material` (private-key / public-key / key).
Role, evidence tier, recommendation or abstention, provenance and supporting evidence are carried
as `pqscan:*` properties because CycloneDX 1.6 has no field for them. Operation components depend
on the key-material components their receiver was traced to (`dependencies`).

Verified against the official 1.6 schema (cryptoProperties identical to the copy bundled in
cyclonedx-python-lib): `cryptoFunctions` has no key-agreement value, so ECDH/X25519/DH sites use
`other` with `pqscan:role=KEY_ESTABLISHMENT`; the padding enum has no PSS, so PSS is `other` with
`pqscan:padding=PSS`. No key bytes, passwords or source snippets are ever exported.
"""
from __future__ import annotations
import hashlib, json, uuid
from typing import Any
from ..models import Role
from ..pipeline import ScanResult, Finding

ROLE_FUNCTIONS = {Role.SIGN: ["sign"], Role.VERIFY: ["verify"], Role.PK_ENCRYPT: ["encrypt"], Role.PK_DECRYPT: ["decrypt"],
                  Role.KEY_ESTABLISHMENT: ["other"], Role.KEY_MATERIAL_ONLY: ["other"], Role.PROTOCOL_CONFIG: ["other"],
                  Role.UNKNOWN: ["unknown"]}
PADDING = {"PKCS1v15": "pkcs1v15", "pkcs1_15": "pkcs1v15", "PKCS1_v1_5": "pkcs1v15", "OAEP": "oaep", "PKCS1_OAEP": "oaep"}


def _algo_name(alg: str, role: Role | None) -> str:
    if alg == "EC":
        return {Role.KEY_ESTABLISHMENT: "ECDH", Role.SIGN: "ECDSA", Role.VERIFY: "ECDSA"}.get(role, "EC")
    if alg == "DH":
        return "FFDH"
    if alg in ("ANY", "EC-or-DSA", None):
        return "RSA-or-ECC (algorithm not statically resolved)" if alg != "EC-or-DSA" else "ECDSA-or-DSA"
    return alg


def _primitive(alg: str, role: Role | None) -> str:
    if role in (Role.SIGN, Role.VERIFY):
        return "signature"
    if role == Role.KEY_ESTABLISHMENT:
        return "key-agree"
    if role in (Role.PK_ENCRYPT, Role.PK_DECRYPT):
        return "pke"
    if alg in ("X25519", "X448", "XDH", "DH"):
        return "key-agree"
    if alg in ("Ed25519", "Ed448", "EdDSA", "DSA"):
        return "signature"
    return "unknown"


def _ref(f: Finding) -> str:
    loc = f.evidence.candidate.location
    return f"pqscan:site:{loc.file}:{loc.line}:{loc.col}"


def _props(f: Finding) -> list[dict[str, str]]:
    d, r, ev = f.decision, f.recommendation, f.evidence
    p = [("pqscan:siteKind", ev.site_kind), ("pqscan:role", d.role.value if d.role else "NONE"), ("pqscan:tier", d.tier.value),
         ("pqscan:action", r.action), ("pqscan:targetClass", r.target_class), ("pqscan:target", r.target),
         ("pqscan:rationale", r.rationale), ("pqscan:policyVersion", r.policy_version), ("pqscan:tierThreshold", r.tier_threshold),
         ("pqscan:scope", f.scope), ("pqscan:library", ev.candidate.library.value), ("pqscan:api", ev.candidate.api),
         ("pqscan:reason", d.reason)]
    if r.parameter_set:
        p.append(("pqscan:parameterSet", r.parameter_set))
    if r.abstain_reason:
        p.append(("pqscan:abstainReason", r.abstain_reason))
    if ev.operation:
        p.append(("pqscan:operation", ev.operation))
    for prov in ev.receiver.provenances:
        p.append(("pqscan:provenance", prov.value))
    if ev.receiver.proximate:
        p.append(("pqscan:proximateProvenance", ev.receiver.proximate.value))
    if ev.args.padding:
        p.append(("pqscan:padding", ev.args.padding))
    if ev.args.hash:
        p.append(("pqscan:hash", ev.args.hash))
    for role in d.possible_roles:
        p.append(("pqscan:possibleRole", role.value))
    for c in d.conflicts:
        p.append(("pqscan:conflict", c))
    for line, what in d.supporting[:8]:
        p.append(("pqscan:evidence", f"line {line}: {what}"))
    if ev.hybrid_apis:
        p.append(("pqscan:hybridWith", ", ".join(ev.hybrid_apis)))
    for rule in f.semgrep_rules:
        p.append(("pqscan:semgrepRule", rule))
    return [{"name": k, "value": str(v)} for k, v in p]


def _component(f: Finding) -> dict[str, Any]:
    d, ev = f.decision, f.evidence
    loc = ev.candidate.location
    alg = d.algorithm
    occ = {"location": loc.file, "line": loc.line, "offset": loc.col}
    comp: dict[str, Any] = {"type": "cryptographic-asset", "bom-ref": _ref(f), "name": _algo_name(alg, d.role),
                            "evidence": {"occurrences": [occ]}, "properties": _props(f)}
    if ev.site_kind == "key-material":
        priv = ev.receiver.private
        comp["cryptoProperties"] = {
            "assetType": "related-crypto-material",
            "relatedCryptoMaterialProperties": {"type": {True: "private-key", False: "public-key"}.get(priv, "key")},
        }
        if ev.receiver.key_size:
            comp["cryptoProperties"]["relatedCryptoMaterialProperties"]["size"] = ev.receiver.key_size
    else:
        ap: dict[str, Any] = {"primitive": _primitive(alg, d.role), "cryptoFunctions": ROLE_FUNCTIONS.get(d.role, ["unknown"]),
                              "nistQuantumSecurityLevel": 0}
        pad = ev.args.padding or ""
        if pad in PADDING:
            ap["padding"] = PADDING[pad]
        elif pad:
            ap["padding"] = "other"
        if ev.receiver.curve:
            ap["curve"] = ev.receiver.curve
        comp["cryptoProperties"] = {"assetType": "algorithm", "algorithmProperties": ap}
    return comp


def to_cbom(res: ScanResult, timestamp: str | None = None) -> dict[str, Any]:
    comps = [_component(f) for f in res.findings]
    # dependencies: operation -> key-material sites in the same file whose line is one of the receiver's origins
    km_by_line = {(f.evidence.candidate.location.file, f.evidence.candidate.location.line): _ref(f)
                  for f in res.findings if f.evidence.site_kind == "key-material"}
    deps = []
    for f in res.findings:
        if f.evidence.site_kind != "operation":
            continue
        targets = sorted({km_by_line[(f.evidence.candidate.location.file, line)] for line, _ in f.evidence.receiver.origins
                          if (f.evidence.candidate.location.file, line) in km_by_line})
        if targets:
            deps.append({"ref": _ref(f), "dependsOn": targets})
    body = json.dumps(comps, sort_keys=True).encode("utf-8")
    serial = uuid.UUID(hashlib.sha256(body + res.policy_version.encode()).hexdigest()[:32], version=5)
    meta: dict[str, Any] = {
        "tools": {"components": [{"type": "application", "name": "pqscan", "version": res.tool_version,
                                  "description": "Post-quantum crypto scanner for Python projects (research prototype)"}]},
        "properties": [{"name": "pqscan:policyVersion", "value": res.policy_version},
                       {"name": "pqscan:tierThreshold", "value": res.tier_threshold},
                       {"name": "pqscan:arm", "value": res.arm},
                       {"name": "pqscan:filesScanned", "value": str(res.files_scanned)},
                       {"name": "pqscan:executionFailures", "value": str(len(res.errors))},
                       {"name": "pqscan:semgrepStatus", "value": res.semgrep_status},
                       {"name": "pqscan:unsupportedLibraryImports", "value": str(len(res.unsupported))},
                       {"name": "pqscan:disclaimer", "value": "Migration guidance only; does not establish that a migrated system is secure, compliant or quantum-safe."}],
    }
    if timestamp:
        meta["timestamp"] = timestamp
    bom: dict[str, Any] = {"$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json", "bomFormat": "CycloneDX", "specVersion": "1.6",
                           "serialNumber": f"urn:uuid:{serial}", "version": 1, "metadata": meta, "components": comps}
    if deps:
        bom["dependencies"] = deps
    return bom


def validate_cbom(bom: dict[str, Any]) -> list[str]:
    """Validate against the CycloneDX 1.6 JSON schema (strict). Returns a list of error messages."""
    from cyclonedx.schema import SchemaVersion
    from cyclonedx.validation.json import JsonStrictValidator
    err = JsonStrictValidator(SchemaVersion.V1_6).validate_str(json.dumps(bom))
    return [] if err is None else [str(err)]
