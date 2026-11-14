"""Simple mapping baselines (evaluation_protocol.md Experiments A–C), computed on pqscan's own
candidate sites so that only the decision rule differs.

B1-algorithm   : algorithm-family mapping, the convention most inspected tools use:
                 RSA -> KEM, EC -> SIG, X25519/X448/DH -> KEM, Ed25519/Ed448/DSA -> SIG;
                 an unresolved algorithm -> DUAL.
B1-dual        : algorithm mapping that refuses to choose for multi-purpose algorithms:
                 RSA/EC/unresolved -> DUAL, single-purpose algorithms as above.
B2-method-args : Module C arm `method+args`, always recommend (tier threshold T0).
B3-full-noabst : Module C arm `full`, always recommend (T0) — provenance without abstention.
B4-full-T2     : Module C arm `full` with the pre-registered threshold T2 — the proposed system.
UNKNOWN roles always abstain (a single target is never invented for them by the B2–B4 arms).
"""
from __future__ import annotations
from ..policy import load_policy
from ..roles import classify
from ..semantic.evidence import SiteEvidence

ALG_RULE = {"RSA": "KEM", "EC": "SIG", "X25519": "KEM", "X448": "KEM", "XDH": "KEM", "DH": "KEM",
            "Ed25519": "SIG", "Ed448": "SIG", "EdDSA": "SIG", "DSA": "SIG"}
SINGLE = {"X25519": "KEM", "X448": "KEM", "XDH": "KEM", "DH": "KEM", "Ed25519": "SIG", "Ed448": "SIG", "EdDSA": "SIG", "DSA": "SIG"}
ARMS = ("B1-algorithm", "B1-dual", "B2-method-args", "B3-full-noabst", "B4-full-T2")


def _algorithm(ev: SiteEvidence) -> str:
    d = classify(ev, "method+args+recv")   # best algorithm evidence without provenance/consumers
    return d.algorithm


def decide(ev: SiteEvidence, arm: str) -> tuple[str, str, str, str]:
    """Return (action, rec_class, tier, recommendation text) for one evidence record under a baseline arm."""
    if arm == "B1-algorithm":
        return "RECOMMEND", ALG_RULE.get(_algorithm(ev), "DUAL"), "-", ""
    if arm == "B1-dual":
        return "RECOMMEND", SINGLE.get(_algorithm(ev), "DUAL"), "-", ""
    cls_arm, thr = {"B2-method-args": ("method+args", "T0"), "B3-full-noabst": ("full", "T0"), "B4-full-T2": ("full", "T2")}[arm]
    d = classify(ev, cls_arm)
    if d.role is None:
        return "NO_FINDING", "NONE", d.tier.value, ""
    rec = load_policy(tier_threshold=thr).apply(d, ev.hybrid_apis, ev.hybrid_combined)
    text = f"{rec.target} {rec.rationale}"
    if rec.action == "ABSTAIN":
        return "ABSTAIN", "NONE", d.tier.value, text
    if rec.action == "FLAG_NO_TARGET":
        return "FLAG_NO_TARGET", "NONE", d.tier.value, text
    return "RECOMMEND", "SIG" if rec.family == "SIG" else "KEM", d.tier.value, text
