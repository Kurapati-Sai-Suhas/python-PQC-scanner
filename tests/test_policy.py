"""Module D — policy v1.1 engine: exhaustive role x tier sweep, safety invariants, hybrid, wording."""
from __future__ import annotations
import copy, re
import pytest
import yaml
from pqscan.models import Role, Tier
from pqscan.policy import load_policy, Policy
from pqscan.policy.engine import DEFAULT_POLICY
from pqscan.roles.classifier import RoleDecision

MLKEM = "cryptography.hazmat.primitives.asymmetric.mlkem.MLKEM768PrivateKey.generate"


def dec(role, tier=Tier.T3, alg="RSA", hybrid=False, possible=()):
    return RoleDecision(site_kind="operation", role=role, tier=tier, algorithm=alg, reason="test",
                        possible_roles=list(possible), hybrid_context=hybrid)


@pytest.fixture(scope="module")
def policy():
    return load_policy()


def test_policy_metadata(policy):
    assert policy.version == "1.1" and policy.threshold == Tier.T2


@pytest.mark.parametrize("role", list(Role))
@pytest.mark.parametrize("tier", list(Tier))
def test_exhaustive_role_tier_sweep(policy, role, tier):
    r = policy.apply(dec(role, tier))
    assert r is not None and r.policy_version == "1.1" and r.tier_threshold == "T2"
    if role == Role.UNKNOWN or tier.rank < Tier.T2.rank:
        assert r.action == "ABSTAIN" and r.family == "NONE" and r.abstain_reason
        return
    expected = {Role.SIGN: "SIG", Role.VERIFY: "SIG", Role.KEY_ESTABLISHMENT: "KEM", Role.PK_ENCRYPT: "KEM_DEM",
                Role.PK_DECRYPT: "KEM_DEM", Role.KEY_MATERIAL_ONLY: "INVENTORY", Role.PROTOCOL_CONFIG: "PROTOCOL_REVIEW"}[role]
    assert r.target_class == expected
    assert r.action == ("RECOMMEND" if expected in ("SIG", "KEM", "KEM_DEM") else "FLAG_NO_TARGET")


@pytest.mark.parametrize("role", [Role.SIGN, Role.VERIFY])
def test_signatures_never_get_ml_kem(policy, role):
    r = policy.apply(dec(role))
    assert r.family == "SIG" and "ML-DSA" in r.target and "ML-KEM" not in r.target + r.rationale


@pytest.mark.parametrize("role", [Role.KEY_ESTABLISHMENT, Role.PK_ENCRYPT, Role.PK_DECRYPT])
def test_key_establishment_and_encryption_never_get_ml_dsa(policy, role):
    r = policy.apply(dec(role))
    assert r.family == "KEM" and "ML-DSA" not in r.target + r.rationale


@pytest.mark.parametrize("role", [Role.PK_ENCRYPT, Role.PK_DECRYPT])
def test_public_key_encryption_is_a_redesign_not_a_drop_in(policy, role):
    r = policy.apply(dec(role))
    text = r.target + " " + r.rationale
    assert "redesign" in text.lower() and "no drop-in" in text.lower()
    assert not re.search(r"replace (RSA|it|this)[^.]* with ML-KEM", text, re.I)


def test_tier_threshold_is_a_parameter():
    strict = load_policy(tier_threshold="T3")
    assert strict.apply(dec(Role.SIGN, Tier.T2)).action == "ABSTAIN"
    lax = load_policy(tier_threshold="T1")
    assert lax.apply(dec(Role.SIGN, Tier.T1)).action == "RECOMMEND"


def test_unknown_lists_possible_roles(policy):
    r = policy.apply(dec(Role.UNKNOWN, possible=[Role.VERIFY, Role.PK_ENCRYPT]))
    assert r.action == "ABSTAIN" and "VERIFY" in r.rationale and "PK_ENCRYPT" in r.rationale


def test_excluded_site_produces_no_record(policy):
    assert policy.apply(dec(None)) is None


def test_approved_hybrid_is_no_action(policy):
    r = policy.apply(dec(Role.KEY_ESTABLISHMENT, alg="X25519", hybrid=True), hybrid_apis=[MLKEM], hybrid_combined=True)
    assert r.target_class == "NO_ACTION_HYBRID" and r.action == "FLAG_NO_TARGET" and "transitional" in r.rationale


def test_unverified_pq_component_is_not_an_approved_hybrid(policy):
    r = policy.apply(dec(Role.KEY_ESTABLISHMENT, alg="X25519", hybrid=True), hybrid_apis=["oqs.KeyEncapsulation"])
    assert r.target_class == "KEM" and "not the NIST-approved scheme for this role" in r.rationale


def test_dsa_signing_has_its_own_sentence(policy):
    assert "FIPS 186-5" in policy.apply(dec(Role.SIGN, alg="DSA")).rationale


def test_invalid_policy_is_rejected():
    data = yaml.safe_load(open(DEFAULT_POLICY, encoding="utf-8"))
    bad = copy.deepcopy(data); bad["roles"]["SIGN"] = "KEM"
    with pytest.raises(ValueError):
        Policy(bad)
    bad = copy.deepcopy(data); bad["roles"]["KEY_ESTABLISHMENT"] = "SIG"
    with pytest.raises(ValueError):
        Policy(bad)
    bad = copy.deepcopy(data); bad["roles"]["UNKNOWN"] = "SIG"
    with pytest.raises(ValueError):
        Policy(bad)
    bad = copy.deepcopy(data); del bad["roles"]["VERIFY"]
    with pytest.raises(ValueError):
        Policy(bad)


def test_end_to_end_hybrid_from_source(policy):
    from pqscan.semantic.evidence import analyze_source
    from pqscan.roles import classify
    # paramiko mlkem768x25519 shape: classical secret returned by a helper, combined with the ML-KEM secret
    src = ("import hashlib\nfrom cryptography.hazmat.primitives.asymmetric import x25519, mlkem\n"
           "class Kex:\n    def start(self):\n        self.x = x25519.X25519PrivateKey.generate()\n"
           "        self.k = mlkem.MLKEM768PrivateKey.generate()\n"
           "    def _x(self, peer):\n        secret = self.x.exchange(peer)\n        return secret\n"
           "    def finish(self, ct, peer):\n        k_pq = self.k.decapsulate(ct)\n        k_cl = self._x(peer)\n"
           "        return hashlib.sha256(k_pq + k_cl).digest()\n")
    evs = analyze_source("h.py", src)
    ev = [e for e in evs if e.operation == "exchange"][0]
    assert ev.hybrid_combined
    assert policy.apply(classify(ev), ev.hybrid_apis, ev.hybrid_combined).target_class == "NO_ACTION_HYBRID"
    km = [e for e in evs if e.site_kind == "key-material" and "x25519" in e.candidate.api][0]
    assert km.hybrid_combined and policy.apply(classify(km), km.hybrid_apis, km.hybrid_combined).target_class == "NO_ACTION_HYBRID"


def test_reviewer_repro_dual_stack_legacy_path_is_not_a_hybrid(policy):
    from pqscan.semantic.evidence import analyze_source
    from pqscan.roles import classify
    src = ("from cryptography.hazmat.primitives.asymmetric import x25519, mlkem\n"
           "class Migrating:\n    def legacy(self, peer):\n        k = x25519.X25519PrivateKey.generate()\n        return k.exchange(peer)\n"
           "    def modern(self):\n        return mlkem.MLKEM768PrivateKey.generate()\n")
    for ev in analyze_source("d.py", src):
        d = classify(ev)
        if d.role == Role.KEY_ESTABLISHMENT:
            r = policy.apply(d, ev.hybrid_apis, ev.hybrid_combined)
            assert r.target_class == "KEM" and "treated as classical" in r.rationale


# ---------------------------------------------------------------- review finding 1: hybrid family must match the role
MLDSA = "cryptography.hazmat.primitives.asymmetric.mldsa.MLDSA65PrivateKey.generate"


def test_ml_kem_nearby_does_not_excuse_a_classical_signature(policy):
    r = policy.apply(dec(Role.SIGN, alg="RSA", hybrid=True), hybrid_apis=[MLKEM])
    assert r.target_class == "SIG" and r.action == "RECOMMEND"


def test_ml_dsa_nearby_does_not_excuse_classical_key_establishment(policy):
    r = policy.apply(dec(Role.KEY_ESTABLISHMENT, alg="EC", hybrid=True), hybrid_apis=[MLDSA])
    assert r.target_class == "KEM" and r.action == "RECOMMEND"


def test_ml_dsa_alongside_ecdsa_signature_is_an_approved_signature_hybrid(policy):
    assert policy.apply(dec(Role.SIGN, alg="EC", hybrid=True), hybrid_apis=[MLDSA], hybrid_combined=True).target_class == "NO_ACTION_HYBRID"
    assert policy.apply(dec(Role.SIGN, alg="EC", hybrid=True), hybrid_apis=[MLDSA]).target_class == "SIG"


def test_policy_rejects_cross_family_hybrid_prefixes():
    data = yaml.safe_load(open(DEFAULT_POLICY, encoding="utf-8"))
    bad = copy.deepcopy(data); bad["approved_hybrid_prefixes"]["SIGN"] = ["cryptography.hazmat.primitives.asymmetric.mlkem."]
    with pytest.raises(ValueError):
        Policy(bad)


def test_reviewer_repro_rsa_signing_next_to_ml_kem_is_recommended_sig():
    from pqscan.semantic.evidence import analyze_source
    from pqscan.roles import classify
    src = ("from cryptography.hazmat.primitives.asymmetric import rsa, padding, mlkem\nfrom cryptography.hazmat.primitives import hashes\n"
           "class Mixed:\n    def kem(self):\n        return mlkem.MLKEM768PrivateKey.generate()\n"
           "    def sig(self, data):\n        k = rsa.generate_private_key(65537, 2048)\n"
           "        return k.sign(data, padding.PSS(padding.MGF1(hashes.SHA256()), 32), hashes.SHA256())\n")
    pol = load_policy()
    for ev in analyze_source("m.py", src):
        d = classify(ev)
        if d.role in (Role.SIGN, Role.VERIFY):
            assert pol.apply(d, ev.hybrid_apis).target_class == "SIG"
