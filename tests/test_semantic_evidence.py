"""Module B — argument resolution, bounded consumer tracing and evidence assembly, on the idioms
observed in the H1 pilot (paramiko key classes, KEX classes, python-jose backends)."""
from __future__ import annotations
from pathlib import Path
import pytest
from pqscan.semantic.evidence import analyze_source
from pqscan.models import Provenance

PARAMIKO_LIKE = '''
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import serialization, hashes

class RSAKey:
    def __init__(self, key=None, data=None):
        self.key = None
        if key is not None:
            self.key = key
        elif data is not None:
            self.key = serialization.load_der_private_key(data, password=None)

    def sign_ssh_data(self, data):
        return self.key.sign(data, padding=padding.PKCS1v15(), algorithm=hashes.SHA512())

    def verify_ssh_sig(self, data, sig):
        key = self.key
        if isinstance(key, rsa.RSAPrivateKey):
            key = key.public_key()
        key.verify(sig, data, padding.PKCS1v15(), hashes.SHA512())

    @staticmethod
    def generate(bits):
        key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
        return RSAKey(key=key)


class KexECDH:
    curve = ec.SECP256R1()

    def _generate_key_pair(self):
        self.P = ec.generate_private_key(self.curve)
        self.Q = self.P.public_key()

    def _parse_init(self, peer):
        K = self.P.exchange(ec.ECDH(), peer)
        return K


def load_only(path, password):
    loaded = serialization.load_ssh_private_key(path.read_bytes(), password=password)
    if isinstance(loaded, rsa.RSAPrivateKey):
        return "rsa"
    return "other"
'''

JOSE_LIKE = '''
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

class ECKey:
    def __init__(self, key):
        if isinstance(key, bytes):
            try:
                key = load_pem_public_key(key)
            except ValueError:
                key = load_pem_private_key(key, password=None)
        self.prepared_key = key

    def sign(self, msg):
        return self.prepared_key.sign(msg, ec.ECDSA(hashes.SHA256()))

    def verify(self, msg, sig):
        self.prepared_key.verify(sig, msg, ec.ECDSA(hashes.SHA256()))


class RSAKeyObj:
    RSA1_5 = padding.PKCS1v15()
    RSA_OAEP = padding.OAEP(padding.MGF1(hashes.SHA1()), hashes.SHA1(), None)

    def __init__(self, key, algorithm):
        self.padding = {"RSA1_5": self.RSA1_5, "RSA-OAEP": self.RSA_OAEP}.get(algorithm)
        self.prepared_key = load_pem_private_key(key, password=None)

    def sign(self, msg):
        return self.prepared_key.sign(msg, padding.PKCS1v15(), hashes.SHA256())

    def wrap_key(self, key_data):
        return self.prepared_key.encrypt(key_data, self.padding)

    def unwrap_key(self, wrapped):
        return self.prepared_key.decrypt(wrapped, self.padding)
'''


def by_line(evs, line):
    hits = [e for e in evs if e.candidate.location.line == line]
    assert hits, f"no evidence at line {line}: {[e.candidate.location.line for e in evs]}"
    return hits[0]


@pytest.fixture(scope="module")
def paramiko_ev():
    return analyze_source("paramiko_like.py", PARAMIKO_LIKE)


@pytest.fixture(scope="module")
def jose_ev():
    return analyze_source("jose_like.py", JOSE_LIKE)


def line_of(src: str, needle: str) -> int:
    for i, l in enumerate(src.splitlines(), 1):
        if needle in l:
            return i
    raise AssertionError(needle)


# ---------------------------------------------------------------- operations: receiver + args
def test_rsa_sign_on_attribute_receiver(paramiko_ev):
    e = by_line(paramiko_ev, line_of(PARAMIKO_LIKE, "self.key.sign("))
    assert e.site_kind == "operation" and e.operation == "sign"
    assert e.receiver.algorithm == "RSA" and e.receiver.private is True
    assert e.receiver.proximate == Provenance.ATTRIBUTE
    assert set(e.receiver.provenances) == {Provenance.GENERATED, Provenance.LOADED_DER, Provenance.PARAMETER}
    assert e.args.padding == "PKCS1v15" and e.args.hash == "SHA512"


def test_rsa_verify_on_local_derived_public_key(paramiko_ev):
    e = by_line(paramiko_ev, line_of(PARAMIKO_LIKE, "key.verify(sig"))
    assert e.operation == "verify" and e.receiver.algorithm == "RSA"
    # `key = self.key; if isinstance(key, RSAPrivateKey): key = key.public_key()` — proving the key is
    # public at the verify call needs path-sensitive reasoning, which the bounded, flow-insensitive
    # design does not do (documented limitation). The union of both definitions is private-or-public.
    assert e.receiver.private is None
    assert e.args.padding == "PKCS1v15"


def test_ec_exchange_receiver_and_ecdh_argument(paramiko_ev):
    e = by_line(paramiko_ev, line_of(PARAMIKO_LIKE, "self.P.exchange("))
    assert e.operation == "exchange" and e.receiver.algorithm == "EC" and e.args.ecdh is True
    assert e.receiver.curve == "SECP256R1"
    assert set(e.receiver.provenances) == {Provenance.GENERATED}


def test_ecdsa_argument_and_multi_provenance_loader_receiver(jose_ev):
    e = by_line(jose_ev, line_of(JOSE_LIKE, "self.prepared_key.sign(msg, ec.ECDSA"))
    assert e.operation == "sign" and e.args.ecdsa is True and e.args.hash == "SHA256"
    assert e.receiver.algorithm == "ANY"  # loaded, algorithm not visible statically
    assert set(e.receiver.provenances) == {Provenance.LOADED_PEM, Provenance.PARAMETER}


def test_padding_from_attribute_dict_is_multi(jose_ev):
    e = by_line(jose_ev, line_of(JOSE_LIKE, "self.prepared_key.encrypt("))
    assert e.operation == "encrypt" and e.args.padding == "multi{OAEP|PKCS1v15}"


# ---------------------------------------------------------------- key material: consumers
def test_keygen_returned_through_constructor_has_signature_consumers(paramiko_ev):
    e = by_line(paramiko_ev, line_of(PARAMIKO_LIKE, "rsa.generate_private_key("))
    assert e.site_kind == "key-material" and e.receiver.algorithm == "RSA" and e.receiver.provenance == Provenance.GENERATED
    assert e.receiver.key_size is None  # `bits` is a parameter, not a literal
    assert e.consumers.families == {"SIG"} and e.consumers.escapes is False
    assert any("RSAKey" in p for p in e.consumers.paths)


def test_loader_in_constructor_assigned_to_attribute(paramiko_ev):
    e = by_line(paramiko_ev, line_of(PARAMIKO_LIKE, "load_der_private_key(data"))
    assert e.site_kind == "key-material" and e.receiver.provenance == Provenance.LOADED_DER
    assert e.consumers.families == {"SIG"}


def test_ephemeral_ec_key_consumed_by_exchange_in_other_method(paramiko_ev):
    e = by_line(paramiko_ev, line_of(PARAMIKO_LIKE, "ec.generate_private_key(self.curve)"))
    assert e.consumers.families == {"KE"} and e.consumers.escapes is False


def test_loader_used_only_for_isinstance_has_no_consumers(paramiko_ev):
    e = by_line(paramiko_ev, line_of(PARAMIKO_LIKE, "load_ssh_private_key("))
    assert e.consumers.families == set() and e.consumers.escapes is False


def test_jose_rsa_loader_reaches_two_families(jose_ev):
    e = by_line(jose_ev, line_of(JOSE_LIKE, "self.prepared_key = load_pem_private_key(key"))
    assert e.consumers.families == {"SIG", "PKE"}


def test_jose_ec_loaders_reach_signature_family_only(jose_ev):
    pub = by_line(jose_ev, line_of(JOSE_LIKE, "key = load_pem_public_key(key)"))
    priv = by_line(jose_ev, line_of(JOSE_LIKE, "key = load_pem_private_key(key, password=None)"))
    assert pub.consumers.families == {"SIG"} and priv.consumers.families == {"SIG"}
    assert pub.receiver.private is False and priv.receiver.private is True


# ---------------------------------------------------------------- negatives and PyCryptodome
def test_non_public_key_receiver_is_flagged():
    src = ("from cryptography.hazmat.primitives.ciphers.aead import AESGCM\n"
           "def f(k, n, d):\n    c = AESGCM(k)\n    return c.encrypt(n, d, None)\n")
    e = analyze_source("x.py", src)[0]
    assert e.site_kind == "not-public-key"


def test_pycryptodome_signer_chain_and_cipher_object():
    src = ("from Crypto.PublicKey import RSA\nfrom Crypto.Signature import pkcs1_15\nfrom Crypto.Cipher import PKCS1_OAEP\n"
           "from Crypto.Hash import SHA256\n"
           "def f(pem, m, data):\n    k = RSA.import_key(pem)\n    s = pkcs1_15.new(k).sign(SHA256.new(m))\n"
           "    c = PKCS1_OAEP.new(k)\n    return s, c.encrypt(data)\n")
    evs = analyze_source("p.py", src)
    ops = {e.operation: e for e in evs if e.site_kind == "operation"}
    assert ops["sign"].receiver.algorithm == "RSA" and ops["sign"].receiver.library == "pycryptodome"
    assert ops["sign"].args.padding == "pkcs1_15"
    assert ops["encrypt"].receiver.algorithm == "RSA" and ops["encrypt"].args.padding == "PKCS1_OAEP"
    km = [e for e in evs if e.site_kind == "key-material"][0]
    assert km.consumers.families == {"SIG", "PKE"}


def test_hybrid_context_detected():
    src = ("from cryptography.hazmat.primitives.asymmetric import x25519, mlkem\n"
           "class Kex:\n    def start(self):\n        self.x = x25519.X25519PrivateKey.generate()\n        self.k = mlkem.MLKEM768PrivateKey.generate()\n"
           "    def ex(self, peer):\n        return self.x.exchange(peer)\n")
    evs = analyze_source("h.py", src)
    e = [x for x in evs if x.operation == "exchange"][0]
    assert e.hybrid_context is True and e.receiver.algorithm == "X25519"


def test_unresolved_parameter_receiver():
    src = ("from cryptography.hazmat.primitives.asymmetric import padding\nfrom cryptography.hazmat.primitives import hashes\n"
           "def s(key, m):\n    return key.sign(m, padding.PKCS1v15(), hashes.SHA256())\n")
    e = analyze_source("u.py", src)[0]
    assert e.site_kind == "operation" and e.receiver.algorithm is None and e.receiver.proximate == Provenance.PARAMETER
    assert e.args.padding == "PKCS1v15"


# ---------------------------------------------------------------- real-code idioms found in the pilot repositories
TUPLE_PAIR = '''
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

class ECDSAKey:
    def __init__(self, vals=None):
        self.signing_key = None
        self.verifying_key = None
        if vals is not None:
            self.signing_key, self.verifying_key = vals

    def sign(self, data):
        return self.signing_key.sign(data, ec.ECDSA(hashes.SHA256()))

    def verify(self, sig, data):
        self.verifying_key.verify(sig, data, ec.ECDSA(hashes.SHA256()))

    @classmethod
    def generate(cls, curve=ec.SECP256R1()):
        private_key = ec.generate_private_key(curve)
        return ECDSAKey(vals=(private_key, private_key.public_key()))
'''


def test_key_pair_passed_as_tuple_and_unpacked_into_attributes():
    evs = analyze_source("t.py", TUPLE_PAIR)
    km = by_line(evs, line_of(TUPLE_PAIR, "ec.generate_private_key(curve)"))
    assert km.consumers.families == {"SIG"} and km.consumers.escapes is False
    sign = by_line(evs, line_of(TUPLE_PAIR, "self.signing_key.sign("))
    assert sign.receiver.algorithm == "EC" and Provenance.GENERATED in sign.receiver.provenances


JWK_TWO_STEP = '''
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

class ECKey:
    def __init__(self, key):
        if isinstance(key, dict):
            self.prepared_key = self._process_jwk(key)
            return
        self.prepared_key = key

    def _process_jwk(self, jwk_dict):
        public = ec.EllipticCurvePublicNumbers(1, 2, ec.SECP256R1())
        if "d" in jwk_dict:
            private = ec.EllipticCurvePrivateNumbers(3, public)
            return private.private_key()
        return public.public_key()

    def public_key(self):
        return self.__class__(self.prepared_key.public_key())

    def sign(self, msg):
        return self.prepared_key.sign(msg, ec.ECDSA(hashes.SHA256()))
'''


def test_two_step_numbers_construction_returned_to_private_caller():
    evs = analyze_source("j.py", JWK_TWO_STEP)
    priv = by_line(evs, line_of(JWK_TWO_STEP, "return private.private_key()"))
    assert priv.site_kind == "key-material" and priv.receiver.algorithm == "EC"
    assert priv.receiver.provenance == Provenance.LOADED_JWK
    # returned from a private helper to `self.prepared_key = self._process_jwk(key)`: traced through the return.
    # `self.prepared_key = key` also stores an externally supplied key, so the attribute's consumers are not
    # exclusively this key's: recorded as incomplete evidence (escape), which caps the role at T2.
    assert priv.consumers.families == {"SIG"}
    assert priv.consumers.escapes is True and any("rebound to an unresolved value" in n for n in priv.consumers.escape_notes)
    assert not any("returned from" in n for n in priv.consumers.escape_notes)


def test_self_class_constructor_is_the_same_class():
    evs = analyze_source("j.py", JWK_TWO_STEP)
    sign = by_line(evs, line_of(JWK_TWO_STEP, "self.prepared_key.sign("))
    assert Provenance.LOADED_JWK in sign.receiver.provenances and Provenance.PARAMETER in sign.receiver.provenances
    pub = by_line(evs, line_of(JWK_TWO_STEP, "return public.public_key()"))
    assert not any("__class__" in n for n in pub.consumers.escape_notes)


PEER_KEY = '''
from cryptography.hazmat.primitives.asymmetric import ec

class Kex:
    def start(self):
        self.P = ec.generate_private_key(ec.SECP256R1())
        self.Q_C = self.P.public_key()

    def finish(self, other):
        return other.exchange(ec.ECDH(), self.Q_C)
'''


def test_public_half_used_as_peer_key_counts_as_key_agreement():
    evs = analyze_source("k.py", PEER_KEY)
    km = by_line(evs, line_of(PEER_KEY, "ec.generate_private_key("))
    assert km.consumers.families == {"KE"} and km.consumers.escapes is False


def test_public_function_return_is_an_escape():
    src = ("from cryptography.hazmat.primitives.asymmetric import rsa\n"
           "def make_key():\n    return rsa.generate_private_key(65537, 2048)\n")
    km = analyze_source("m.py", src)[0]
    assert km.consumers.escapes is True and km.consumers.families == set()


def test_classes_inside_module_level_if_block_are_analysed():
    src = ("try:\n    from cryptography.hazmat.primitives.asymmetric import ec\n    has_crypto = True\nexcept ImportError:\n    has_crypto = False\n"
           "if has_crypto:\n    class ECAlg:\n        def prepare(self):\n            self.k = ec.generate_private_key(ec.SECP256R1())\n"
           "        def run(self, peer):\n            return self.k.exchange(ec.ECDH(), peer)\n")
    evs = analyze_source("g.py", src)
    km = [e for e in evs if e.site_kind == "key-material"][0]
    assert km.function == "ECAlg.prepare" and km.consumers.families == {"KE"} and km.consumers.escapes is False


def test_inherited_helper_method_is_resolved_and_same_family_algorithms_merge():
    src = ("from cryptography.hazmat.primitives.asymmetric import ed25519, ed448\n"
           "class Base:\n    def check(self, key):\n        return isinstance(key, ed25519.Ed25519PrivateKey)\n"
           "class OKP(Base):\n    def __init__(self, big):\n"
           "        self.k = ed448.Ed448PrivateKey.generate() if big else ed25519.Ed25519PrivateKey.generate()\n"
           "        self.check(self.k)\n    def s(self, m):\n        return self.k.sign(m)\n")
    evs = analyze_source("o.py", src)
    op = [e for e in evs if e.operation == "sign"][0]
    assert op.receiver.algorithm == "EdDSA"
    km = [e for e in evs if e.site_kind == "key-material"]
    assert km and all(not e.consumers.escapes for e in km) and all(e.consumers.families == {"SIG"} for e in km)
