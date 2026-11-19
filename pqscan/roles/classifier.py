"""Role decision table (taxonomy v1.0, data_dictionary.md Sec. 3 tier definitions).

Operation sites (`<recv>.sign/verify/exchange/encrypt/decrypt`):
  role from the method; tier from the evidence that the receiver is a public-key object:
    T0  receiver unresolved and no algorithm-specific argument
    T1  only one of {receiver is a key object, algorithm-specific argument / single-purpose algorithm}
    T2  both
    T3  T2 and the receiver's origin is resolved to at least one concrete provenance
        (generated / loaded / constructed / certificate), with no conflict
  any conflict (e.g. ECDSA argument on an RSA receiver) -> T1, conflict recorded.

Key-material sites (keygen / loader / construct):
  role from the type-valid consumers found by bounded tracing (taxonomy rule 1):
    one family, no escape   -> that family's role, T3
    one family, escape      -> that family's role, T2 (other consumers may exist outside the bound)
    two or more families    -> UNKNOWN (possible roles listed), T2
    no consumer, no escape  -> KEY_MATERIAL_ONLY, T2
    no consumer, escape     -> single-purpose algorithm decides (X25519/X448/DH -> KEY_ESTABLISHMENT,
                               Ed25519/Ed448/DSA -> SIGN) at T2; otherwise UNKNOWN, T1
  a single-purpose algorithm that disagrees with the consumers -> conflict, T1.

Ablation arms restrict the evidence:
  method-only        operations: method name only (receiver and arguments ignored, so tier T0);
                     key material: UNKNOWN (T1, the key API is known) unless the algorithm is single-purpose
  method+args        + algorithm-specific arguments
  method+args+recv   + receiver typing (operations can reach T2)
  full               + provenance and consumers (T3 and key-material roles)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from ..models import Role, Tier, Provenance
from ..semantic.evidence import SiteEvidence

ARMS = ("method-only", "method+args", "method+args+recv", "full")

ROLE_OF_METHOD = {"sign": Role.SIGN, "verify": Role.VERIFY, "exchange": Role.KEY_ESTABLISHMENT,
                  "encrypt": Role.PK_ENCRYPT, "decrypt": Role.PK_DECRYPT}
SINGLE_PURPOSE = {"X25519": Role.KEY_ESTABLISHMENT, "X448": Role.KEY_ESTABLISHMENT, "XDH": Role.KEY_ESTABLISHMENT,
                  "DH": Role.KEY_ESTABLISHMENT, "Ed25519": Role.SIGN, "Ed448": Role.SIGN, "EdDSA": Role.SIGN, "DSA": Role.SIGN}
FAMILY_ROLES = {"SIG": (Role.SIGN, Role.VERIFY), "KE": (Role.KEY_ESTABLISHMENT,), "PKE": (Role.PK_ENCRYPT, Role.PK_DECRYPT)}
RSA_PARAMS = {"PKCS1v15", "PSS", "OAEP", "pkcs1_15", "pss", "PKCS1_OAEP", "PKCS1_v1_5", "PKCS1_PSS"}
CONCRETE_PROVENANCE = {Provenance.GENERATED, Provenance.LOADED_PEM, Provenance.LOADED_DER, Provenance.LOADED_SSH,
                       Provenance.LOADED_JWK, Provenance.LOADED_CERTIFICATE, Provenance.CONSTRUCTED}


@dataclass
class RoleDecision:
    site_kind: str
    role: Role | None                     # None = not a recommendation site (excluded, see reason)
    tier: Tier
    algorithm: str                        # best evidence: receiver type, else arguments, else "ANY"
    reason: str
    possible_roles: list[Role] = field(default_factory=list)
    secondary_roles: list[Role] = field(default_factory=list)
    supporting: list[tuple[int, str]] = field(default_factory=list)   # (line, what)
    conflicts: list[str] = field(default_factory=list)
    hybrid_context: bool = False
    arm: str = "full"

    def to_dict(self) -> dict[str, Any]:
        return {"site_kind": self.site_kind, "role": self.role.value if self.role else None, "tier": self.tier.value,
                "algorithm": self.algorithm, "reason": self.reason,
                "possible_roles": [r.value for r in self.possible_roles], "secondary_roles": [r.value for r in self.secondary_roles],
                "supporting": self.supporting, "conflicts": self.conflicts, "hybrid_context": self.hybrid_context, "arm": self.arm}


def _algorithm_from_args(ev: SiteEvidence) -> str | None:
    pad = ev.args.padding or ""
    pads = set(pad[6:-1].split("|")) if pad.startswith("multi{") else ({pad} if pad else set())
    if pads and pads <= RSA_PARAMS:
        return "RSA"
    if ev.args.ecdsa or ev.args.ecdh:
        return "EC"
    if pads & {"DSS"}:
        return "EC-or-DSA"
    if pads & {"eddsa"}:
        return "Ed25519"
    return None


def _ops_in(ev: SiteEvidence) -> set[str]:
    return {d.strip(".()") for _, d in ev.consumers.locations if d.startswith(".")}


def _direction_unknown(single_role: Role, recv) -> bool:
    """Owner decision TA07 (taxonomy rule 10, 19 Nov 2026): a signature-family key whose public/private status is not
    established (e.g. PyCryptodome DSA.import_key) has no determinable direction; SIGN is never inferred from it."""
    return single_role == Role.SIGN and recv.private is None


def _unknown_direction(d: RoleDecision, alg: str, where: str) -> None:
    d.role, d.tier = Role.UNKNOWN, Tier.T1
    d.possible_roles = [Role.SIGN, Role.VERIFY, Role.KEY_MATERIAL_ONLY]
    d.reason = (f"{alg} is a signature-only algorithm, but whether this key is private (SIGN) or public (VERIFY) is not "
                f"established; {where}")


def _key_material_role(ev: SiteEvidence, family: str) -> tuple[Role, list[Role]]:
    """Type-valid consumer rule: a public key with signature consumers verifies; a private key signs."""
    ops = _ops_in(ev)
    priv = ev.receiver.private
    if family == "SIG":
        if priv is False or (priv is None and ops and ops <= {"verify"}):
            return Role.VERIFY, []
        return Role.SIGN, [Role.VERIFY]
    if family == "PKE":
        if priv is False or (ops and ops <= {"encrypt"}):
            return Role.PK_ENCRYPT, []
        if priv is True and ops <= {"decrypt"}:
            return Role.PK_DECRYPT, []
        return (Role.PK_DECRYPT, [Role.PK_ENCRYPT]) if priv else (Role.PK_ENCRYPT, [Role.PK_DECRYPT])
    return Role.KEY_ESTABLISHMENT, []


def classify(ev: SiteEvidence, arm: str = "full") -> RoleDecision:
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}; expected one of {ARMS}")
    use_args = arm in ("method+args", "method+args+recv", "full")
    use_recv = arm in ("method+args+recv", "full")
    use_prov = arm == "full"
    recv = ev.receiver
    recv_alg = recv.algorithm if (use_recv and recv.algorithm not in (None, "ANY")) else None
    arg_alg = _algorithm_from_args(ev) if use_args else None
    algorithm = recv_alg or arg_alg or (recv.algorithm if use_recv and recv.algorithm else "ANY")
    conflicts = list(ev.conflicts) if use_args and use_recv else []
    if use_prov:
        conflicts += [c for c in ev.consumers.conflicts if c not in conflicts]
    d = RoleDecision(site_kind=ev.site_kind, role=None, tier=Tier.T0, algorithm=algorithm, reason="", hybrid_context=ev.hybrid_context,
                     arm=arm, conflicts=conflicts)

    # ------------------------------------------------------------------ excluded kinds
    if ev.site_kind == "not-public-key":
        d.reason = "receiver is a symmetric/MAC object, not a public key; not a PQC migration site"
        return d
    if ev.site_kind in ("signer-object", "cipher-object", "pqc", "parse-error"):
        d.reason = {"signer-object": "PyCryptodome signer object; the recommendation is attached to its sign/verify call",
                    "cipher-object": "PyCryptodome cipher object; the recommendation is attached to its encrypt/decrypt call",
                    "pqc": "post-quantum algorithm usage (hybrid-context evidence only)",
                    "parse-error": "file could not be parsed"}[ev.site_kind]
        return d

    # ------------------------------------------------------------------ operations
    if ev.site_kind == "operation":
        d.role = ROLE_OF_METHOD[ev.operation]
        d.supporting.append((ev.candidate.location.line, f"method .{ev.operation}()"))
        key_evidence = use_recv and recv.algorithm is not None          # receiver resolved to a key object
        single = recv_alg in SINGLE_PURPOSE if recv_alg else False
        arg_evidence = arg_alg is not None or single
        if key_evidence:
            d.supporting.append((ev.candidate.location.line, f"receiver {recv.description}"))
        if arg_evidence and arg_alg:
            d.supporting.append((ev.candidate.location.line, f"arguments {ev.args.summary()}"))
        if single:
            allowed = {Role.KEY_ESTABLISHMENT} if SINGLE_PURPOSE[recv_alg] == Role.KEY_ESTABLISHMENT else {Role.SIGN, Role.VERIFY}
            if d.role not in allowed:
                d.conflicts.append(f"{recv_alg} is single-purpose ({SINGLE_PURPOSE[recv_alg].value}) but the method is .{ev.operation}()")
        compatible = {"RSA": {"RSA"}, "EC": {"EC"}, "EC-or-DSA": {"EC", "DSA"}, "Ed25519": {"Ed25519", "Ed448"}}
        if recv_alg and arg_alg and recv_alg not in compatible.get(arg_alg, {arg_alg}):
            msg = f"arguments suggest {arg_alg} but the receiver is {recv_alg}"
            if not any(recv_alg in c and ("argument" in c) for c in d.conflicts):
                d.conflicts.append(msg)
        if key_evidence and arg_evidence:
            d.tier = Tier.T2
            concrete = [p for p in recv.provenances if p in CONCRETE_PROVENANCE]
            if use_prov and concrete:
                d.tier = Tier.T3
                for line, text in recv.origins[:4]:
                    d.supporting.append((line, f"key origin {text}"))
        elif key_evidence or arg_evidence:
            d.tier = Tier.T1
        else:
            d.tier = Tier.T0
        if d.conflicts:
            d.tier = min(d.tier, Tier.T1, key=lambda t: t.rank)
        inconsistent = use_prov and d.tier == Tier.T3 and (len(ev.origin_families) > 1 or ev.origin_conflict
                                                           or Provenance.PARAMETER in recv.provenances)
        if inconsistent:
            d.tier = Tier.T2   # T3 requires provenance and downstream use to be mutually consistent
        d.reason = (f"operation .{ev.operation}() -> {d.role.value}; "
                    f"receiver {'resolved: ' + recv.description if key_evidence else 'unresolved' + (' (' + recv.unresolved_reason + ')' if recv.unresolved_reason and use_recv else '')}; "
                    f"arguments: {ev.args.summary() if use_args else 'not used in this arm'}"
                    + ("; the key may also come from an untyped parameter, or its origin is consumed by another role family or has "
                       "conflicting consumers, so the tier is capped at T2" if inconsistent else ""))
        return d

    # ------------------------------------------------------------------ key material
    alg = recv.algorithm or "ANY"
    d.algorithm = alg if alg != "ANY" else (arg_alg or "ANY")
    d.supporting.append((ev.candidate.location.line, f"{ev.candidate.api} ({recv.provenance.value if recv.provenance else 'unknown provenance'})"))
    single_role = SINGLE_PURPOSE.get(alg)
    if not use_prov:
        if single_role and _direction_unknown(single_role, recv):
            _unknown_direction(d, alg, "consumers not used in this arm")
        elif single_role:
            # the key API names a single-purpose algorithm; receiver/key typing (the recv arms) makes it T2
            d.role, d.tier = single_role, Tier.T2 if use_recv else Tier.T1
            if single_role == Role.SIGN and recv.private is False:
                d.role = Role.VERIFY
            d.reason = f"{alg} is a single-purpose algorithm ({single_role.value}); consumers not used in this arm"
        else:
            d.role, d.tier = Role.UNKNOWN, Tier.T1
            d.possible_roles = [Role.SIGN, Role.VERIFY, Role.KEY_ESTABLISHMENT, Role.PK_ENCRYPT, Role.PK_DECRYPT, Role.KEY_MATERIAL_ONLY]
            if alg == "EC":
                d.possible_roles = [Role.SIGN, Role.VERIFY, Role.KEY_ESTABLISHMENT, Role.KEY_MATERIAL_ONLY]
            d.reason = f"key material ({alg}); role needs consumer evidence, which this arm does not use"
        return d

    fams = ev.consumers.families
    if any("rebound to a non-key object" in c or "is rebound to a" in c and "key at line" in c for c in ev.consumers.conflicts):
        d.role, d.tier = Role.UNKNOWN, Tier.T1
        d.possible_roles = [r for f in sorted(fams) for r in FAMILY_ROLES[f]] + [Role.KEY_MATERIAL_ONLY]
        d.reason = ("the variable holding this key is reused for another key or object, so the consumers found under that "
                    "name cannot be attributed to this key (flow-insensitive analysis)")
        return d
    for line, desc in ev.consumers.locations[:6]:
        d.supporting.append((line, f"consumer {desc}"))
    if len(fams) == 1:
        fam = next(iter(fams))
        d.role, d.secondary_roles = _key_material_role(ev, fam)
        d.tier = Tier.T2 if ev.consumers.escapes else Tier.T3
        d.reason = (f"key material ({alg}, {recv.provenance.value if recv.provenance else '?'}) reaches {fam} consumers only"
                    + ("; it also escapes the analysed scope (" + "; ".join(ev.consumers.escape_notes[:2]) + ")" if ev.consumers.escapes else ""))
        if single_role and single_role not in FAMILY_ROLES[fam]:
            d.conflicts.append(f"{alg} is single-purpose ({single_role.value}) but its consumers are {fam}")
    elif len(fams) > 1:
        d.role, d.tier = Role.UNKNOWN, Tier.T2
        d.possible_roles = [r for f in sorted(fams) for r in FAMILY_ROLES[f]]
        if recv.private is False:
            d.possible_roles = [r for r in d.possible_roles if r not in (Role.SIGN, Role.PK_DECRYPT)]
        elif recv.private is True:
            d.possible_roles = [r for r in d.possible_roles if r != Role.PK_ENCRYPT]
        d.reason = (f"key material ({alg}) reaches consumers of {len(fams)} families ({', '.join(sorted(fams))}); "
                    "the role depends on which path runs, so it is not statically determinable")
    elif not ev.consumers.escapes:
        d.role, d.tier = Role.KEY_MATERIAL_ONLY, Tier.T2
        d.reason = f"key material ({alg}) with no consumer inside the analysed scope and no escape: inventory only"
    elif single_role and _direction_unknown(single_role, recv):
        _unknown_direction(d, alg, "consumers lie outside the analysed scope (" + "; ".join(ev.consumers.escape_notes[:2]) + ")")
    elif single_role:
        d.role, d.tier = (Role.VERIFY if single_role == Role.SIGN and recv.private is False else single_role), Tier.T2
        d.reason = f"{alg} is a single-purpose algorithm ({single_role.value}); consumers lie outside the analysed scope"
    else:
        d.role, d.tier = Role.UNKNOWN, Tier.T1
        d.possible_roles = [Role.SIGN, Role.VERIFY, Role.KEY_ESTABLISHMENT, Role.PK_ENCRYPT, Role.PK_DECRYPT] if alg in ("RSA", "ANY") \
            else [Role.SIGN, Role.VERIFY, Role.KEY_ESTABLISHMENT]
        if alg == "RSA":
            d.possible_roles = [Role.SIGN, Role.VERIFY, Role.PK_ENCRYPT, Role.PK_DECRYPT]
        d.reason = "key material leaves the analysed scope before any consumer is seen (" + "; ".join(ev.consumers.escape_notes[:2]) + ")"
    if d.conflicts:
        d.tier = Tier.T1
    return d
