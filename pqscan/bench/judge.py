"""Outcome judging, recommendation_policy.md v1.1 Section 5, applied to normalised tool actions.

Ground truth (site labels) and tool behaviour are kept as separate fields:
  site:   gt_role, assessability, eligible, hybrid_component
  tool:   action (RECOMMEND | FLAG_NO_TARGET | ABSTAIN | NO_FINDING | EXECUTION_FAILURE) and
          rec_class (SIG | KEM | DUAL | PQC_ALREADY | NONE)
  result: judgment (CORRECT | INCORRECT | UNDECIDED | UNJUSTIFIED | UNASSESSABLE | MISSED |
          DETECTED_ONLY | FALSE_POSITIVE_SITE | N/A | EXECUTION_FAILURE) and harm category.
An abstention on a determinate site is UNASSESSABLE (neither right nor harmful; it reduces coverage);
on an indeterminate site it is CORRECT.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Mapping

DROPIN = re.compile(r"replace[sd]?\b.*\b(entirely|directly)|drop-?in|\bswap\b|replace (RSA|ECDH|X25519|ECDSA|EC) with", re.I)
NEGATION = re.compile(r"\b(no|not|never|cannot|can't|isn't|is not|without|nor)\b[^.;]{0,25}$", re.I)
# only the negated token is removed ("No ML-KEM equivalent exists ..., migrate to ML-DSA" keeps ML-DSA)
_TOK = r"(?:ML[-_ ]?KEM|ML[-_ ]?DSA|SLH[-_ ]?DSA|Kyber|Dilithium)(?:[-_ ]?\d+)?"
NEGATED_TARGET = re.compile(
    r"\b(?:do not|don't|never|not|no|avoid|instead of|rather than|over|not recommended:?)\s+(?:use\s+|recommend\s+)?" + _TOK
    + r"|" + _TOK + r"\s+(?:is not|isn't|is|are not|should not|shouldn't|must not)\s+(?:be\s+)?"
    r"(?:used|recommended|suitable|appropriate|applied|needed|necessary|unnecessary|unsuitable|inappropriate|a\s)",
    re.I)
_KEM = re.compile(r"ML[-_ ]?KEM|Kyber", re.I)
_SIG = re.compile(r"ML[-_ ]?DSA|SLH[-_ ]?DSA|Dilithium", re.I)


def dropin_wording(text: str | None) -> bool:
    """True when the text implies a direct substitution; negated phrases ("no drop-in replacement",
    "not a drop-in") do not count."""
    t = text or ""
    for m in DROPIN.finditer(t):
        if not NEGATION.search(t[max(0, m.start() - 40):m.start()]):
            return True
    return False
TARGET_OF_ROLE = {"SIGN": "SIG", "VERIFY": "SIG", "KEY_ESTABLISHMENT": "KEM", "PK_ENCRYPT": "KEM", "PK_DECRYPT": "KEM"}


def classify_text(text: str | None) -> str:
    """Map a tool's free-text recommendation to a target class."""
    t = NEGATED_TARGET.sub(" ", text or "")   # "do not use ML-KEM for signatures" is not a KEM target
    if "Already using PQC" in t:
        return "PQC_ALREADY"
    has_kem = bool(_KEM.search(t))
    has_sig = bool(_SIG.search(t))
    if has_kem and has_sig:
        return "DUAL"
    if has_kem:
        return "KEM"
    if has_sig:
        return "SIG"
    return "NONE"


def expected_class(site: Mapping[str, str]) -> str:
    if str(site["eligible"]).lower() not in ("yes", "true"):
        return "N/A"
    if str(site.get("hybrid_component", "")).lower() in ("yes", "true") or site["gt_role"] in ("KEY_MATERIAL_ONLY", "PROTOCOL_CONFIG"):
        return "NONE"
    if site["assessability"] == "INDETERMINATE":
        return "ABSTAIN"
    return TARGET_OF_ROLE.get(site["gt_role"], "ABSTAIN")


@dataclass(frozen=True)
class Judgment:
    judgment: str
    harm: str = ""


def judge(site: Mapping[str, str], action: str, rec_class: str) -> Judgment:
    exp = expected_class(site)
    hybrid = str(site.get("hybrid_component", "")).lower() in ("yes", "true")
    if action == "EXECUTION_FAILURE":
        return Judgment("EXECUTION_FAILURE")
    if exp == "N/A":
        # any reported record on an ineligible site (an abstention included) is a detection false positive
        return Judgment("N/A") if action == "NO_FINDING" else Judgment("FALSE_POSITIVE_SITE")
    if action == "NO_FINDING":
        return Judgment("MISSED")
    if action == "ABSTAIN":
        return Judgment("CORRECT") if exp == "ABSTAIN" else Judgment("UNASSESSABLE")
    if action == "FLAG_NO_TARGET":
        # correct where no target is justified (inventory / hybrid / protocol); otherwise detection only
        return Judgment("CORRECT") if exp == "NONE" else Judgment("DETECTED_ONLY")
    # action == RECOMMEND
    if exp == "ABSTAIN":
        if rec_class == "DUAL":
            return Judgment("UNDECIDED")
        if rec_class == "PQC_ALREADY":
            return Judgment("INCORRECT", "FALSE_ASSURANCE")
        return Judgment("UNJUSTIFIED")
    if exp == "NONE":
        if rec_class == "PQC_ALREADY":
            return Judgment("CORRECT") if hybrid else Judgment("INCORRECT", "FALSE_ASSURANCE")
        if rec_class == "DUAL":
            return Judgment("UNDECIDED")
        return Judgment("INCORRECT", "OVER_RECOMMENDATION")
    if rec_class == "PQC_ALREADY":
        return Judgment("INCORRECT", "FALSE_ASSURANCE")
    if rec_class == "DUAL":
        return Judgment("UNDECIDED")
    if rec_class == exp:
        return Judgment("CORRECT")
    return Judgment("INCORRECT", "ROLE_INCOMPATIBLE")


def combine_texts(texts: list[str]) -> tuple[str, str]:
    """Several tool findings in one site window -> (action, rec_class). Mirrors the pilot rule:
    a site with only non-PQC texts is FLAG_NO_TARGET; contradictory 'already PQC' plus a migration
    target counts as the migration target; two different targets count as DUAL."""
    if not texts:
        return "NO_FINDING", "NONE"
    classes = {classify_text(t) for t in texts}
    if classes == {"NONE"}:
        return "FLAG_NO_TARGET", "NONE"
    cl = classes - {"NONE"}
    if "PQC_ALREADY" in cl and cl - {"PQC_ALREADY"}:
        cl = cl - {"PQC_ALREADY"}
    if "DUAL" in cl or len(cl) > 1:
        return "RECOMMEND", "DUAL"
    return "RECOMMEND", cl.pop()


def our_action(target_class: str, action: str) -> tuple[str, str]:
    """pqscan Recommendation -> (action, rec_class) in the common vocabulary."""
    if action == "ABSTAIN":
        return "ABSTAIN", "NONE"
    if action == "FLAG_NO_TARGET":
        return "FLAG_NO_TARGET", "NONE"
    return "RECOMMEND", {"SIG": "SIG", "KEM": "KEM", "KEM_DEM": "KEM"}[target_class]


def strict_judgment(j: Judgment, dropin: bool) -> Judgment:
    """Pre-registered strict sensitivity scoring (docs/specification/scoring_policy.md Sec. 3): a
    family-correct KEM / KEM_DEM recommendation whose wording implies a drop-in substitution is
    INCORRECT with harm UNSUPPORTED_DROP_IN. Every other judgment is unchanged."""
    if dropin and j.judgment == "CORRECT":
        return Judgment("INCORRECT", "UNSUPPORTED_DROP_IN")
    return j
