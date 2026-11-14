"""Module B — import resolution and receiver typing on small, labelled snippets."""
from __future__ import annotations
import ast
import pytest
from pqscan.semantic.imports import ImportMap
from pqscan.semantic.model import KeyType, SignerObject, CipherObject, CertType, Unknown, Multi
from pqscan.semantic.typer import ModuleTyper
from pqscan.models import Provenance


def typer(src: str) -> ModuleTyper:
    return ModuleTyper(ast.parse(src), src.splitlines())


# ---------------------------------------------------------------- imports
def test_import_map_resolves_aliases():
    src = ("import cryptography.hazmat.primitives.asymmetric.rsa as R\n"
           "from cryptography.hazmat.primitives import serialization as ser\n"
           "from cryptography.hazmat.primitives.serialization import load_pem_private_key as lppk\n"
           "from Crypto.PublicKey import RSA\n"
           "import Cryptodome.Signature.pkcs1_15\n")
    im = ImportMap.from_module(ast.parse(src))
    assert im.resolve("R.generate_private_key") == "cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key"
    assert im.resolve("ser.load_der_private_key") == "cryptography.hazmat.primitives.serialization.load_der_private_key"
    assert im.resolve("lppk") == "cryptography.hazmat.primitives.serialization.load_pem_private_key"
    assert im.resolve("RSA.import_key") == "Crypto.PublicKey.RSA.import_key"
    assert im.resolve("Cryptodome.Signature.pkcs1_15.new") == "Cryptodome.Signature.pkcs1_15.new"
    assert im.resolve("unrelated.thing") is None


# ---------------------------------------------------------------- typing of key-producing calls
@pytest.mark.parametrize("expr, alg, private, prov", [
    ("rsa.generate_private_key(65537, 2048)", "RSA", True, Provenance.GENERATED),
    ("ec.generate_private_key(ec.SECP256R1())", "EC", True, Provenance.GENERATED),
    ("ec.derive_private_key(5, ec.SECP256R1())", "EC", True, Provenance.CONSTRUCTED),
    ("x25519.X25519PrivateKey.generate()", "X25519", True, Provenance.GENERATED),
    ("x25519.X25519PublicKey.from_public_bytes(b'')", "X25519", False, Provenance.CONSTRUCTED),
    ("serialization.load_pem_private_key(d, None)", "ANY", True, Provenance.LOADED_PEM),
    ("serialization.load_pem_public_key(d)", "ANY", False, Provenance.LOADED_PEM),
    ("serialization.load_der_private_key(d, None)", "ANY", True, Provenance.LOADED_DER),
    ("serialization.load_ssh_private_key(d, None)", "ANY", True, Provenance.LOADED_SSH),
    ("rsa.RSAPrivateNumbers(p, q, d, 1, 1, 1, pub).private_key()", "RSA", True, Provenance.CONSTRUCTED),
    ("rsa.RSAPublicNumbers(e, n).public_key()", "RSA", False, Provenance.CONSTRUCTED),
    ("ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), b'')", "EC", False, Provenance.CONSTRUCTED),
    ("x509.load_pem_x509_certificate(d).public_key()", "ANY", False, Provenance.LOADED_CERTIFICATE),
    ("RSA.generate(2048)", "RSA", True, Provenance.GENERATED),
    ("RSA.import_key(pem)", "RSA", None, Provenance.LOADED_PEM),
    ("RSA.construct((n, e))", "RSA", None, Provenance.CONSTRUCTED),
    ("ECC.generate(curve='P-256')", "EC", True, Provenance.GENERATED),
    ("RSA.import_key(pem).publickey()", "RSA", False, Provenance.LOADED_PEM),
])
def test_type_of_key_producing_calls(expr, alg, private, prov):
    src = ("from cryptography.hazmat.primitives.asymmetric import rsa, ec, x25519\n"
           "from cryptography.hazmat.primitives import serialization\n"
           "from cryptography import x509\n"
           "from Crypto.PublicKey import RSA, ECC\n"
           f"def f(d, p, q, e, n, pub, pem):\n    k = {expr}\n    return k\n")
    t = typer(src)
    fn = t.function("f")
    ty = t.type_of_name("k", fn)
    assert isinstance(ty, KeyType), ty
    assert ty.algorithm == alg and ty.private is private and ty.provenance == prov


def test_public_key_of_private_is_public_same_algorithm():
    src = ("from cryptography.hazmat.primitives.asymmetric import ec\n"
           "def f():\n    k = ec.generate_private_key(ec.SECP384R1())\n    p = k.public_key()\n    return p\n")
    t = typer(src); fn = t.function("f")
    ty = t.type_of_name("p", fn)
    assert isinstance(ty, KeyType) and ty.algorithm == "EC" and ty.private is False and ty.provenance == Provenance.GENERATED


def test_pycryptodome_signer_and_cipher_objects():
    src = ("from Crypto.PublicKey import RSA\nfrom Crypto.Signature import pkcs1_15\nfrom Crypto.Cipher import PKCS1_OAEP\n"
           "def f(pem):\n    k = RSA.import_key(pem)\n    s = pkcs1_15.new(k)\n    c = PKCS1_OAEP.new(k)\n    return s, c\n")
    t = typer(src); fn = t.function("f")
    s, c = t.type_of_name("s", fn), t.type_of_name("c", fn)
    assert isinstance(s, SignerObject) and s.scheme == "pkcs1_15" and isinstance(s.key, KeyType) and s.key.algorithm == "RSA"
    assert isinstance(c, CipherObject) and c.scheme == "PKCS1_OAEP" and c.key.algorithm == "RSA"


# ---------------------------------------------------------------- attributes, parameters, multi
def test_self_attribute_typed_from_class_wide_assignments():
    src = ("from cryptography.hazmat.primitives.asymmetric import rsa\n"
           "class K:\n"
           "    def __init__(self):\n        self.key = None\n"
           "    def gen(self):\n        self.key = rsa.generate_private_key(65537, 2048)\n"
           "    def use(self, m):\n        return self.key.sign(m)\n")
    t = typer(src); fn = t.function("K.use")
    ty = t.type_of_expr(ast.parse("self.key").body[0].value, fn)
    assert isinstance(ty, KeyType) and ty.algorithm == "RSA" and ty.provenance == Provenance.GENERATED
    assert ty.proximate == Provenance.ATTRIBUTE


def test_self_attribute_with_two_origins_is_multi():
    src = ("from cryptography.hazmat.primitives.asymmetric import rsa\nfrom cryptography.hazmat.primitives import serialization\n"
           "class K:\n"
           "    def gen(self):\n        self.key = rsa.generate_private_key(65537, 2048)\n"
           "    def load(self, d):\n        self.key = serialization.load_der_private_key(d, None)\n"
           "    def use(self, m):\n        return self.key.sign(m)\n")
    t = typer(src); fn = t.function("K.use")
    ty = t.type_of_expr(ast.parse("self.key").body[0].value, fn)
    assert isinstance(ty, Multi)
    kinds = {(o.algorithm, o.provenance) for o in ty.options}
    assert kinds == {("RSA", Provenance.GENERATED), ("ANY", Provenance.LOADED_DER)}
    assert ty.proximate == Provenance.ATTRIBUTE


def test_parameter_with_annotation_or_isinstance_guard():
    src = ("from cryptography.hazmat.primitives.asymmetric import rsa, ec\n"
           "def a(key: rsa.RSAPrivateKey, m):\n    return key.sign(m)\n"
           "def b(key, m):\n    if isinstance(key, ec.EllipticCurvePublicKey):\n        return key.verify(m)\n"
           "def c(key, m):\n    return key.sign(m)\n")
    t = typer(src)
    ta = t.type_of_name("key", t.function("a"))
    assert isinstance(ta, KeyType) and ta.algorithm == "RSA" and ta.private is True and ta.proximate == Provenance.PARAMETER
    tb = t.type_of_name("key", t.function("b"))
    assert isinstance(tb, KeyType) and tb.algorithm == "EC" and tb.private is False
    tc = t.type_of_name("key", t.function("c"))
    assert isinstance(tc, Unknown) and tc.proximate == Provenance.PARAMETER


def test_unknown_callee_and_non_key_values():
    src = ("from cryptography.hazmat.primitives.ciphers.aead import AESGCM\n"
           "def f(k, x):\n    c = AESGCM(k)\n    y = helper(x)\n    return c, y\n")
    t = typer(src); fn = t.function("f")
    assert isinstance(t.type_of_name("c", fn), Unknown)
    assert t.type_of_name("c", fn).reason == "non-public-key object"
    assert isinstance(t.type_of_name("y", fn), Unknown)


def test_one_level_local_call_return_typing():
    src = ("from cryptography.hazmat.primitives.asymmetric import ec\n"
           "def make():\n    return ec.generate_private_key(ec.SECP256R1())\n"
           "def f():\n    k = make()\n    return k\n")
    t = typer(src); fn = t.function("f")
    ty = t.type_of_name("k", fn)
    assert isinstance(ty, KeyType) and ty.algorithm == "EC" and ty.provenance == Provenance.GENERATED
    assert ty.via_call == "make"
