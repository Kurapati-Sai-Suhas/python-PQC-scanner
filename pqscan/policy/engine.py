"""Apply the frozen policy table to a role decision.

Actions (data_dictionary.md, tool_action): RECOMMEND (a migration target class), FLAG_NO_TARGET
(inventory / protocol review / hybrid: the site is reported but no target is justified), ABSTAIN
(evidence below the tier threshold, or role UNKNOWN). Sites Module C excluded produce no record.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml
from ..models import Role, Tier
from ..roles.classifier import RoleDecision

POLICY_DIR = Path(__file__).parent
DEFAULT_POLICY = POLICY_DIR / "policy_v1_1.yaml"

MISSING_EVIDENCE = {
    Tier.T0: "the receiver is not resolved to a key object and no algorithm-specific argument is visible",
    Tier.T1: "only one of receiver typing or algorithm-specific arguments is available (or evidence conflicts)",
    Tier.T2: "the key's origin or its consumers are not fully resolved",
}


@dataclass
class Recommendation:
    action: str                          # RECOMMEND | FLAG_NO_TARGET | ABSTAIN
    target_class: str                    # SIG | KEM | KEM_DEM | INVENTORY | PROTOCOL_REVIEW | NO_ACTION_HYBRID | ABSTAIN
    family: str                          # SIG | KEM | NONE  (KEM_DEM belongs to the KEM family)
    role: str | None
    tier: str
    target: str
    parameter_set: str | None
    rationale: str
    references: list[str] = field(default_factory=list)
    policy_version: str = ""
    tier_threshold: str = ""
    abstain_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dict(vars(self))


class Policy:
    def __init__(self, data: dict[str, Any], tier_threshold: str | None = None):
        self.data = data
        self.version = str(data["version"])
        self.threshold = Tier(tier_threshold or data["default_tier_threshold"])
        self.refs = data["references"]
        self._validate()

    def _validate(self) -> None:
        roles = {r.value for r in Role}
        if set(self.data["roles"]) != roles:
            raise ValueError(f"policy must map every role exactly once: missing {roles - set(self.data['roles'])}")
        for role, cls in self.data["roles"].items():
            if cls not in self.data["classes"]:
                raise ValueError(f"role {role} maps to unknown class {cls}")
        # hard safety invariants: never a KEM for signatures, never a signature scheme for KE/PKE
        fam = {c: v["family"] for c, v in self.data["classes"].items()}
        for role in ("SIGN", "VERIFY"):
            if fam[self.data["roles"][role]] != "SIG":
                raise ValueError(f"{role} must map to the SIG family")
        for role in ("KEY_ESTABLISHMENT", "PK_ENCRYPT", "PK_DECRYPT"):
            if fam[self.data["roles"][role]] != "KEM":
                raise ValueError(f"{role} must map to the KEM family")
        if self.data["roles"]["UNKNOWN"] != "ABSTAIN":
            raise ValueError("UNKNOWN must abstain")
        hyb = self.data.get("approved_hybrid_prefixes", {})
        if not isinstance(hyb, dict):
            raise ValueError("approved_hybrid_prefixes must map roles to PQ API prefixes")
        for role, prefs in hyb.items():
            for p in prefs:
                if role == "KEY_ESTABLISHMENT" and ".mlkem." not in p:
                    raise ValueError("only ML-KEM can make a key-establishment site part of an approved hybrid")
                if role in ("SIGN", "VERIFY") and ".mldsa." not in p and ".slhdsa." not in p:
                    raise ValueError("only ML-DSA/SLH-DSA can make a signature site part of an approved hybrid")
                if role not in ("KEY_ESTABLISHMENT", "SIGN", "VERIFY"):
                    raise ValueError(f"role {role} cannot be part of a hybrid")

    # ------------------------------------------------------------------ main entry
    def apply(self, d: RoleDecision, hybrid_apis: list[str] | None = None, hybrid_combined: bool = False) -> Recommendation | None:
        if d.role is None:
            return None
        hybrid_apis = hybrid_apis or []
        prefixes = tuple(self.data["approved_hybrid_prefixes"].get(d.role.value, [])) if d.role else ()
        family_present = bool(prefixes) and any(a.startswith(prefixes) for a in hybrid_apis)
        # a matching-family PQ API nearby is not enough: the classical and PQ results must be combined
        approved_hybrid = family_present and hybrid_combined
        alg = d.algorithm if d.algorithm not in ("ANY", "EC-or-DSA") else ("RSA/ECC" if d.algorithm == "ANY" else "ECDSA/DSA")
        alg_label = {"EC": "ECDSA/ECDH (elliptic-curve)", "RSA": "RSA"}.get(alg, alg)

        if d.role == Role.UNKNOWN:
            return self._abstain(d, self.data["templates"]["ABSTAIN_UNKNOWN"].format(
                missing=d.reason, possible=", ".join(r.value for r in d.possible_roles) or "unknown"), reason="role UNKNOWN")
        if d.tier.rank < self.threshold.rank:
            return self._abstain(d, self.data["templates"]["ABSTAIN_TIER"].format(
                tier=d.tier.value, threshold=self.threshold.value, missing=MISSING_EVIDENCE.get(d.tier, ""), role=d.role.value),
                reason=f"tier {d.tier.value} < {self.threshold.value}")

        if approved_hybrid:
            cls = "NO_ACTION_HYBRID"
            text = self.data["templates"]["HYBRID"]
        else:
            cls = self.data["roles"][d.role.value]
            key = d.role.value
            if d.role == Role.SIGN and d.algorithm == "DSA":
                key = "SIGN_DSA"
            text = self.data["templates"][key].format(alg=alg_label)
            if family_present and not hybrid_combined:
                text += (" Note: an approved post-quantum algorithm is used in the same class or function, but this site's "
                         "result is not combined with it, so this path is treated as classical (a legacy path kept beside a "
                         "post-quantum path still needs migration).")
            elif d.hybrid_context and d.role in (Role.KEY_ESTABLISHMENT, Role.SIGN, Role.VERIFY):
                text += (" Note: a post-quantum API is used nearby, but it is not the NIST-approved scheme for this role "
                         "(ML-KEM for key establishment, ML-DSA for signatures), so the site is not treated as part of an approved hybrid.")
        c = self.data["classes"][cls]
        action = "RECOMMEND" if c["family"] in ("SIG", "KEM") else "FLAG_NO_TARGET"
        return Recommendation(action=action, target_class=cls, family=c["family"], role=d.role.value, tier=d.tier.value,
                              target=c["target"], parameter_set=c.get("parameter_set"), rationale=" ".join(text.split()),
                              references=[self.refs[r] for r in c.get("references", [])], policy_version=self.version,
                              tier_threshold=self.threshold.value)

    def _abstain(self, d: RoleDecision, text: str, reason: str) -> Recommendation:
        c = self.data["classes"]["ABSTAIN"]
        return Recommendation(action="ABSTAIN", target_class="ABSTAIN", family="NONE", role=d.role.value if d.role else None,
                              tier=d.tier.value, target=c["target"], parameter_set=None, rationale=" ".join(text.split()),
                              references=[], policy_version=self.version, tier_threshold=self.threshold.value, abstain_reason=reason)


def load_policy(path: Path | None = None, tier_threshold: str | None = None) -> Policy:
    with open(path or DEFAULT_POLICY, encoding="utf-8") as f:
        return Policy(yaml.safe_load(f), tier_threshold)
