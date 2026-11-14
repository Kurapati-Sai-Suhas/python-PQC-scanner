"""Module C — role inference and evidence tiers on labelled snippets (one behaviour per test)."""
from __future__ import annotations
import pytest
from pqscan.models import Role, Tier
from pqscan.roles import classify, ARMS
from pqscan.semantic.evidence import analyze_source

HDR = ("from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding, x25519\n"
       "from cryptography.hazmat.primitives import hashes, serialization\n"
       "from cryptography.hazmat.primitives.ciphers.aead import AESGCM\n")


def decision_at(src: str, needle: str, arm: str = "full"):
    full = HDR + src
    line = next(i for i, l in enumerate(full.splitlines(), 1) if needle in l)
    evs = [e for e in analyze_source("x.py", full) if e.candidate.location.line == line]
    assert evs, f"no site at {needle!r}"
    return classify(evs[0], arm)


# ---------------------------------------------------------------- operations
def test_sign_on_generated_rsa_key_is_sign_t3():
    d = decision_at("def f(m):\n    k = rsa.generate_private_key(65537, 2048)\n"
                    "    return k.sign(m, padding.PSS(padding.MGF1(hashes.SHA256()), 32), hashes.SHA256())\n", "k.sign(")
    assert d.role == Role.SIGN and d.tier == Tier.T3 and d.algorithm == "RSA" and not d.conflicts


def test_verify_on_loaded_public_key_is_verify_t3():
    d = decision_at("def f(pem, s, m):\n    k = serialization.load_pem_public_key(pem)\n"
                    "    k.verify(s, m, ec.ECDSA(hashes.SHA256()))\n", "k.verify(")
    assert d.role == Role.VERIFY and d.tier == Tier.T3 and d.algorithm == "EC"


def test_oaep_encrypt_is_pk_encrypt_and_decrypt_is_pk_decrypt():
    src = ("def f(m):\n    k = rsa.generate_private_key(65537, 3072)\n"
           "    oaep = padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None)\n"
           "    c = k.public_key().encrypt(m, oaep)\n    return k.decrypt(c, oaep)\n")
    assert decision_at(src, ".encrypt(m, oaep)").role == Role.PK_ENCRYPT
    d = decision_at(src, "k.decrypt(c, oaep)")
    assert d.role == Role.PK_DECRYPT and d.tier == Tier.T3


def test_ecdh_exchange_is_key_establishment_t3():
    d = decision_at("def f(peer):\n    k = ec.generate_private_key(ec.SECP384R1())\n    return k.exchange(ec.ECDH(), peer)\n", "k.exchange(")
    assert d.role == Role.KEY_ESTABLISHMENT and d.tier == Tier.T3


def test_x25519_exchange_needs_no_argument_evidence():
    d = decision_at("def f(peer):\n    k = x25519.X25519PrivateKey.generate()\n    return k.exchange(peer)\n", "k.exchange(")
    assert d.role == Role.KEY_ESTABLISHMENT and d.tier == Tier.T3


def test_untyped_parameter_with_rsa_padding_is_t1():
    d = decision_at("def f(key, m):\n    return key.sign(m, padding.PKCS1v15(), hashes.SHA256())\n", "key.sign(")
    assert d.role == Role.SIGN and d.tier == Tier.T1 and d.algorithm == "RSA"


def test_untyped_parameter_without_arguments_is_t0():
    d = decision_at("def f(key, m):\n    return key.sign(m)\n", "key.sign(")
    assert d.role == Role.SIGN and d.tier == Tier.T0


def test_typed_receiver_with_unresolved_padding_is_t1():
    d = decision_at("def f(m, pad, h):\n    k = rsa.generate_private_key(65537, 2048)\n    return k.sign(m, pad, h)\n", "k.sign(")
    assert d.tier == Tier.T1


def test_conflicting_argument_drops_to_t1():
    d = decision_at("def f(m):\n    k = rsa.generate_private_key(65537, 2048)\n    return k.sign(m, ec.ECDSA(hashes.SHA256()))\n", "k.sign(")
    assert d.tier == Tier.T1 and d.conflicts


def test_symmetric_receiver_is_excluded():
    d = decision_at("def f(k, n, m):\n    c = AESGCM(k)\n    return c.encrypt(n, m, None)\n", "c.encrypt(")
    assert d.role is None and "symmetric" in d.reason


# ---------------------------------------------------------------- key material
def test_ec_keygen_used_only_for_exchange_is_key_establishment():
    d = decision_at("class Kex:\n    def start(self):\n        self.p = ec.generate_private_key(ec.SECP256R1())\n"
                    "    def finish(self, peer):\n        return self.p.exchange(ec.ECDH(), peer)\n", "ec.generate_private_key(")
    assert d.role == Role.KEY_ESTABLISHMENT and d.tier == Tier.T3


def test_public_key_loader_with_verify_consumer_is_verify():
    d = decision_at("def f(pem, s, m):\n    k = serialization.load_pem_public_key(pem)\n"
                    "    k.verify(s, m, ec.ECDSA(hashes.SHA256()))\n", "load_pem_public_key(")
    assert d.role == Role.VERIFY and d.tier == Tier.T3


def test_private_key_with_signature_consumers_is_sign_with_verify_secondary():
    d = decision_at("def f(m):\n    k = rsa.generate_private_key(65537, 2048)\n"
                    "    s = k.sign(m, padding.PKCS1v15(), hashes.SHA256())\n"
                    "    k.public_key().verify(s, m, padding.PKCS1v15(), hashes.SHA256())\n", "rsa.generate_private_key(")
    assert d.role == Role.SIGN and d.secondary_roles == [Role.VERIFY] and d.tier == Tier.T3


def test_key_reaching_two_families_is_unknown_with_possible_roles():
    d = decision_at("class K:\n    def __init__(self, pem):\n        self.k = serialization.load_pem_private_key(pem, None)\n"
                    "    def s(self, m):\n        return self.k.sign(m, padding.PKCS1v15(), hashes.SHA256())\n"
                    "    def d(self, c):\n        return self.k.decrypt(c, padding.PKCS1v15())\n", "load_pem_private_key(")
    assert d.role == Role.UNKNOWN and set(d.possible_roles) == {Role.SIGN, Role.VERIFY, Role.PK_DECRYPT}


def test_key_without_consumer_or_escape_is_key_material_only():
    d = decision_at("def f(pem):\n    k = serialization.load_pem_private_key(pem, None)\n"
                    "    return isinstance(k, rsa.RSAPrivateKey)\n", "load_pem_private_key(")
    assert d.role == Role.KEY_MATERIAL_ONLY


def test_rsa_key_returned_from_public_function_is_unknown_t1():
    d = decision_at("def make():\n    return rsa.generate_private_key(65537, 2048)\n", "rsa.generate_private_key(")
    assert d.role == Role.UNKNOWN and d.tier == Tier.T1 and Role.KEY_ESTABLISHMENT not in d.possible_roles


def test_escaping_x25519_key_uses_single_purpose_algorithm():
    d = decision_at("def make():\n    return x25519.X25519PrivateKey.generate()\n", "X25519PrivateKey.generate(")
    assert d.role == Role.KEY_ESTABLISHMENT and d.tier == Tier.T2


# ---------------------------------------------------------------- arms
def test_arms_increase_evidence_monotonically_for_a_keygen_site():
    src = "class Kex:\n    def start(self):\n        self.p = ec.generate_private_key(ec.SECP256R1())\n" \
          "    def finish(self, peer):\n        return self.p.exchange(ec.ECDH(), peer)\n"
    roles = {arm: decision_at(src, "ec.generate_private_key(", arm).role for arm in ARMS}
    assert roles["method-only"] == roles["method+args"] == roles["method+args+recv"] == Role.UNKNOWN
    assert roles["full"] == Role.KEY_ESTABLISHMENT


def test_method_only_arm_ignores_receiver_and_arguments():
    d = decision_at("def f(m):\n    k = rsa.generate_private_key(65537, 2048)\n"
                    "    return k.sign(m, padding.PKCS1v15(), hashes.SHA256())\n", "k.sign(", arm="method-only")
    # tier definitions are frozen: an operation with neither receiver nor argument evidence is T0
    assert d.role == Role.SIGN and d.tier == Tier.T0 and d.algorithm == "ANY"


def test_unknown_arm_rejected():
    with pytest.raises(ValueError):
        decision_at("def f(key, m):\n    return key.sign(m)\n", "key.sign(", arm="bogus")


# ---------------------------------------------------------------- PyCryptodome
def test_pycryptodome_chained_signature_is_sign_t3():
    src = ("from Crypto.PublicKey import RSA\nfrom Crypto.Signature import pkcs1_15\nfrom Crypto.Hash import SHA256\n"
           "def f(m):\n    k = RSA.generate(2048)\n    return pkcs1_15.new(k).sign(SHA256.new(m))\n")
    evs = analyze_source("p.py", src)
    op = [e for e in evs if e.site_kind == "operation"][0]
    d = classify(op)
    assert d.role == Role.SIGN and d.tier == Tier.T3 and d.algorithm == "RSA"
    km = classify([e for e in evs if e.site_kind == "key-material"][0])
    assert km.role == Role.SIGN
    signer = classify([e for e in evs if e.site_kind == "signer-object"][0])
    assert signer.role is None


# ---------------------------------------------------------------- review finding 2, 10, 11: type validity and consistency
def test_reviewer_repro_rsa_name_reused_for_x25519_does_not_get_kem():
    from pqscan.policy import load_policy
    src = ("def f(m, peer, sign_manifest):\n    key = rsa.generate_private_key(65537, 2048)\n    sig = sign_manifest(key, m)\n"
           "    key = x25519.X25519PrivateKey.generate()\n    return key.exchange(peer)\n")
    d = decision_at(src, "rsa.generate_private_key(")
    assert d.role != Role.KEY_ESTABLISHMENT or d.tier == Tier.T1
    assert load_policy().apply(d).target_class != "KEM"


def test_rsa_key_with_exchange_consumer_is_a_conflict():
    d = decision_at("def f(peer):\n    k = rsa.generate_private_key(65537, 2048)\n    return k.exchange(peer)\n", "rsa.generate_private_key(")
    assert d.tier == Tier.T1 and d.conflicts and d.role != Role.KEY_ESTABLISHMENT


def test_ec_key_with_decrypt_consumer_is_a_conflict():
    d = decision_at("def f(c):\n    k = ec.generate_private_key(ec.SECP256R1())\n    return k.decrypt(c)\n", "ec.generate_private_key(")
    assert d.tier == Tier.T1 and d.conflicts


def test_public_key_with_sign_consumer_is_a_conflict():
    d = decision_at("def f(pem, m):\n    k = serialization.load_pem_public_key(pem)\n    return k.sign(m)\n", "load_pem_public_key(")
    assert d.tier == Tier.T1 and d.conflicts


def test_name_rebound_to_non_key_object_is_a_conflict():
    d = decision_at("from cryptography.fernet import Fernet\ndef f(m, fk):\n    k = rsa.generate_private_key(65537, 2048)\n"
                    "    k = Fernet(fk)\n    return k.encrypt(m)\n", "rsa.generate_private_key(")
    assert d.tier == Tier.T1 and any("non-key object" in c for c in d.conflicts)


def test_operation_capped_at_t2_when_origin_key_spans_two_families():
    src = ("def f(m, c):\n    k = rsa.generate_private_key(65537, 2048)\n"
           "    s = k.sign(m, padding.PKCS1v15(), hashes.SHA256())\n    return s, k.decrypt(c, padding.PKCS1v15())\n")
    assert decision_at(src, "rsa.generate_private_key(").role == Role.UNKNOWN
    assert decision_at(src, "k.sign(").tier == Tier.T2
    assert decision_at(src, "k.decrypt(").tier == Tier.T2


def test_private_key_reached_only_through_public_half_verify_is_sign():
    d = decision_at("def f(s, m):\n    k = ec.generate_private_key(ec.SECP256R1())\n"
                    "    k.public_key().verify(s, m, ec.ECDSA(hashes.SHA256()))\n", "ec.generate_private_key(")
    assert d.role == Role.SIGN and d.secondary_roles == [Role.VERIFY]


def test_escaping_ed25519_public_key_is_verify():
    src = ("from cryptography.hazmat.primitives.asymmetric import ed25519\n"
           "def load(b):\n    return ed25519.Ed25519PublicKey.from_public_bytes(b)\n")
    assert decision_at(src, "from_public_bytes(").role == Role.VERIFY


def test_ecdh_argument_on_sign_is_a_conflict():
    d = decision_at("def f(m):\n    k = ec.generate_private_key(ec.SECP256R1())\n    return k.sign(m, ec.ECDH())\n", "k.sign(")
    assert d.tier == Tier.T1 and d.conflicts


def test_class_holding_either_key_half_filters_impossible_consumers_silently():
    src = ("class K:\n    def __init__(self, pem, private):\n        if private:\n"
           "            self.k = serialization.load_pem_private_key(pem, None)\n        else:\n"
           "            self.k = serialization.load_pem_public_key(pem)\n"
           "    def s(self, m):\n        return self.k.sign(m, ec.ECDSA(hashes.SHA256()))\n"
           "    def v(self, sig, m):\n        self.k.verify(sig, m, ec.ECDSA(hashes.SHA256()))\n")
    pub = decision_at(src, "load_pem_public_key(pem)")
    assert pub.role == Role.VERIFY and pub.tier == Tier.T3 and not pub.conflicts


def test_consumer_through_method_returning_same_class_instance():
    src = ("class RK:\n    def __init__(self, pem):\n        self.k = serialization.load_pem_public_key(pem)\n"
           "    def public_key(self):\n        return self.__class__(self.k)\n"
           "    def verify(self, s, m):\n        self.public_key().k.verify(s, m, padding.PKCS1v15(), hashes.SHA256())\n"
           "    def wrap(self, cek):\n        return self.k.encrypt(cek, padding.PKCS1v15())\n")
    d = decision_at(src, "load_pem_public_key(")
    assert d.role == Role.UNKNOWN and set(d.possible_roles) == {Role.VERIFY, Role.PK_ENCRYPT}



def test_operation_whose_key_may_come_from_a_parameter_is_capped_at_t2():
    d = decision_at("def f(m, key=None):\n    if key is None:\n        key = rsa.generate_private_key(65537, 2048)\n"
                    "    return key.sign(m, padding.PKCS1v15(), hashes.SHA256())\n", "key.sign(")
    assert d.role == Role.SIGN and d.tier == Tier.T2


def test_key_whose_name_is_reused_for_a_non_key_object_is_unknown_in_every_threshold():
    from pqscan.policy import load_policy
    d = decision_at("from cryptography.fernet import Fernet\ndef f(m, fk):\n    k = rsa.generate_private_key(65537, 2048)\n"
                    "    k = Fernet(fk)\n    return k.encrypt(m)\n", "rsa.generate_private_key(")
    assert d.role == Role.UNKNOWN and load_policy(tier_threshold="T0").apply(d).action == "ABSTAIN"


def test_operation_conflict_flows_back_to_the_key_site():
    d = decision_at("def f(m):\n    k = ec.generate_private_key(ec.SECP256R1())\n    return k.sign(m, ec.ECDH())\n",
                    "ec.generate_private_key(")
    assert d.tier == Tier.T1 and any("conflicting arguments" in c for c in d.conflicts)


def test_signature_hybrid_requires_combined_signatures():
    from pqscan.policy import load_policy
    from pqscan.semantic.evidence import analyze_source
    from pqscan.roles import classify
    base = ("from cryptography.hazmat.primitives.asymmetric import ec, mldsa\nfrom cryptography.hazmat.primitives import hashes\n"
            "def both(m):\n    k = ec.generate_private_key(ec.SECP256R1())\n    q = mldsa.MLDSA65PrivateKey.generate()\n"
            "    s1 = k.sign(m, ec.ECDSA(hashes.SHA256()))\n    s2 = q.sign(m)\n")
    for tail, expected in (("    return s1 + s2\n", "NO_ACTION_HYBRID"), ("    return s1\n", "SIG")):
        ev = [e for e in analyze_source("s.py", base + tail) if e.operation == "sign" and e.receiver.algorithm == "EC"][0]
        r = load_policy().apply(classify(ev), ev.hybrid_apis, ev.hybrid_combined)
        assert r.target_class == expected, (tail, r.target_class)
