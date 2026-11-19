"""Synthetic benchmark generator (Dataset A; evaluation protocol Sec. 2, checklist B3).

    python -m pqscan.bench.synth --out benchmark/synthetic [--seed 20261113]

Writes a deterministic dataset:

* `cases/<base_case>/<operator>.py` : one small Python module per instance (never imported or executed);
* `sites.jsonl`                      : one site record per instance, valid against `docs/benchmark/benchmark_schema.json`;
* `manifest.json`                    : generator version and source hash, seed, base-case split, and per-instance
                                       provenance (base case, operator, file SHA-256);
* `validation_subset.csv`            : a blind 20% sample (site locations only, no labels) for the external annotator.

Each base case is a small idiom (key generation with its consumers, an operation, or a negative). Its ground
truth follows `docs/specification/role_taxonomy.md`:
* key sites inherit the role of their type-valid consumers (rule 1);
* consumers of two families selected at runtime give UNKNOWN / INDETERMINATE (rule 2);
* export-only keys give KEY_MATERIAL_ONLY (rule 3);
* operations fix their own role (rule 4);
* negatives are NONE and ineligible (rule 8).

Six semantics-preserving operators (`identity`, `alias-import`, `wrapper-function`, `class-method`,
`cross-function`, `dict-dispatch`) keep the role and assessability of the base case. `loaded-key` replaces
key generation with PEM loading. It is an evidence-condition change, not an invariance operator, and is
listed separately in the manifest.

Variants of one base case are correlated, so every statistic clusters on `base_case`. Base cases, not
instances, are split into `synthetic-dev` and `synthetic-holdout`, so no variant of a held-out base case is
seen during development.
"""
from __future__ import annotations
import argparse, csv, dataclasses, hashlib, json, random, re, sys
from pathlib import Path

GENERATOR_VERSION = "1.1"   # 1.1 (2026-11-19, owner decision G02): obvious_from_name null on negatives
DEFAULT_SEED = 20261113
OPERATORS = ("identity", "alias-import", "wrapper-function", "class-method", "cross-function", "dict-dispatch")
EVIDENCE_CHANGE = "loaded-key"
NEGATIVE_OPERATORS = ("identity", "alias-import", "wrapper-function", "class-method")
PARAMS = "data, sig, ct, peer_public, alg"
SITE = "  #@SITE"

# name -> import statement; alias-import rewrites "import X" to "import X as _x_mod"
MODULES = {
    "rsa": "from cryptography.hazmat.primitives.asymmetric import rsa",
    "ec": "from cryptography.hazmat.primitives.asymmetric import ec",
    "x25519": "from cryptography.hazmat.primitives.asymmetric import x25519",
    "x448": "from cryptography.hazmat.primitives.asymmetric import x448",
    "ed25519": "from cryptography.hazmat.primitives.asymmetric import ed25519",
    "ed448": "from cryptography.hazmat.primitives.asymmetric import ed448",
    "padding": "from cryptography.hazmat.primitives.asymmetric import padding",
    "hashes": "from cryptography.hazmat.primitives import hashes",
    "serialization": "from cryptography.hazmat.primitives import serialization",
    "AESGCM": "from cryptography.hazmat.primitives.ciphers.aead import AESGCM",
    "ChaCha20Poly1305": "from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305",
    "Fernet": "from cryptography.fernet import Fernet",
    "RSA": "from Crypto.PublicKey import RSA",
    "ECC": "from Crypto.PublicKey import ECC",
    "pkcs1_15": "from Crypto.Signature import pkcs1_15",
    "pss": "from Crypto.Signature import pss",
    "DSS": "from Crypto.Signature import DSS",
    "PKCS1_OAEP": "from Crypto.Cipher import PKCS1_OAEP",
    "PKCS1_v1_5": "from Crypto.Cipher import PKCS1_v1_5",
    "AES": "from Crypto.Cipher import AES",
    "SHA256": "from Crypto.Hash import SHA256",
}
MACROS = {
    "<PSS>": "{padding}.PSS(mgf={padding}.MGF1({hashes}.SHA256()), salt_length={padding}.PSS.MAX_LENGTH)",
    "<OAEP>": "{padding}.OAEP(mgf={padding}.MGF1(algorithm={hashes}.SHA256()), algorithm={hashes}.SHA256(), label=None)",
}

# --------------------------------------------------------------------- snippets
GEN = {"RSA": "{rsa}.generate_private_key(public_exponent=65537, key_size=3072)",
       "EC": "{ec}.generate_private_key({ec}.SECP256R1())",
       "X25519": "{x25519}.X25519PrivateKey.generate()", "X448": "{x448}.X448PrivateKey.generate()",
       "Ed25519": "{ed25519}.Ed25519PrivateKey.generate()", "Ed448": "{ed448}.Ed448PrivateKey.generate()",
       "c-RSA": "{RSA}.generate(3072)", "c-EC": '{ECC}.generate(curve="P-256")'}
LOAD = {"pyca": "{serialization}.load_pem_private_key(pem, password=None)",
        "c-RSA": "{RSA}.import_key(pem)", "c-EC": "{ECC}.import_key(pem)"}
EXPORT = {"pyca": "{K}.private_bytes({serialization}.Encoding.PEM, {serialization}.PrivateFormat.PKCS8, {serialization}.NoEncryption())",
          "c-RSA": "{K}.export_key()", "c-EC": '{K}.export_key(format="PEM")'}
OPS = {
    "rsa-sign": "{K}.sign(data, <PSS>, {hashes}.SHA256())",
    "rsa-sign-v15": "{K}.sign(data, {padding}.PKCS1v15(), {hashes}.SHA256())",
    "rsa-verify": "{K}.public_key().verify(sig, data, <PSS>, {hashes}.SHA256())",
    "rsa-encrypt": "{K}.public_key().encrypt(data, <OAEP>)",
    "rsa-encrypt-v15": "{K}.public_key().encrypt(data, {padding}.PKCS1v15())",
    "rsa-decrypt": "{K}.decrypt(ct, <OAEP>)",
    "ec-sign": "{K}.sign(data, {ec}.ECDSA({hashes}.SHA256()))",
    "ec-verify": "{K}.public_key().verify(sig, data, {ec}.ECDSA({hashes}.SHA256()))",
    "ec-exchange": "{K}.exchange({ec}.ECDH(), peer_public)",
    "x-exchange": "{K}.exchange(peer_public)",
    "ed-sign": "{K}.sign(data)",
    "ed-verify": "{K}.public_key().verify(sig, data)",
    "c-sign": "{pkcs1_15}.new({K}).sign({SHA256}.new(data))",
    "c-sign-pss": "{pss}.new({K}).sign({SHA256}.new(data))",
    "c-verify": "{pkcs1_15}.new({K}.publickey()).verify({SHA256}.new(data), sig)",
    "c-encrypt": "{PKCS1_OAEP}.new({K}.publickey()).encrypt(data)",
    "c-encrypt-v15": "{PKCS1_v1_5}.new({K}.publickey()).encrypt(data)",
    "c-decrypt": "{PKCS1_OAEP}.new({K}).decrypt(ct)",
    "ecc-sign": '{DSS}.new({K}, "fips-186-3").sign({SHA256}.new(data))',
    "ecc-verify": '{DSS}.new({K}.public_key(), "fips-186-3").verify({SHA256}.new(data), sig)',
}
OP_ROLE = {"sign": "SIGN", "verify": "VERIFY", "encrypt": "PK_ENCRYPT", "decrypt": "PK_DECRYPT", "exchange": "KEY_ESTABLISHMENT"}
FAMILY = {"SIGN": "SIGN", "VERIFY": "SIGN", "KEY_ESTABLISHMENT": "KE", "PK_ENCRYPT": "ENC", "PK_DECRYPT": "ENC"}
SINGLE_PURPOSE = {"X25519", "X448", "Ed25519", "Ed448"}


def _op_role(op: str) -> str:
    return OP_ROLE[next(k for k in OP_ROLE if f"-{k}" in op)]


def _op_method(op: str) -> str:
    return next(k for k in OP_ROLE if f"-{k}" in op)


@dataclasses.dataclass(frozen=True)
class Base:
    id: str
    library: str                  # pyca | pycryptodome | unknown | out-of-scope:<name>
    algorithm: str                # schema enum
    kind: str                     # key | op | neg
    gen: str = ""                 # key in GEN
    uses: tuple[str, ...] = ()    # op names (OPS) or "export"; for kind=op the first is the site
    runtime: bool = False         # uses[0] / uses[1] selected by the runtime `alg` parameter
    prelude: tuple[str, ...] = () # module-level lines (negatives)
    setup: tuple[str, ...] = ()   # statements before the negative site
    neg_site: str = ""            # negative site expression (or comment when it starts with '#')
    neg_api: str = ""
    note: str = ""

    @property
    def lib_key(self) -> str:
        return "pyca" if self.library == "pyca" else ("c-RSA" if self.algorithm == "RSA" else "c-EC")


def _key(id, lib, alg, gen, uses, runtime=False, note=""):
    return Base(id, lib, alg, "key", gen, tuple(uses), runtime, note=note)


def _op(id, lib, alg, gen, op, note=""):
    return Base(id, lib, alg, "op", gen, (op,), note=note)


def _neg(id, lib, alg, site, api, setup=(), prelude=(), note=""):
    return Base(id, lib, alg, "neg", neg_site=site, neg_api=api, setup=tuple(setup), prelude=tuple(prelude), note=note)


BASE_CASES: tuple[Base, ...] = (
    # pyca RSA
    _key("pyca-rsa-key-sign", "pyca", "RSA", "RSA", ["rsa-sign"]),
    _key("pyca-rsa-key-signverify", "pyca", "RSA", "RSA", ["rsa-sign", "rsa-verify"]),
    _key("pyca-rsa-key-decrypt", "pyca", "RSA", "RSA", ["rsa-decrypt"]),
    _key("pyca-rsa-key-export", "pyca", "RSA", "RSA", ["export"]),
    _key("pyca-rsa-key-runtime", "pyca", "RSA", "RSA", ["rsa-sign", "rsa-decrypt"], runtime=True),
    _op("pyca-rsa-op-sign", "pyca", "RSA", "RSA", "rsa-sign"),
    _op("pyca-rsa-op-sign-v15", "pyca", "RSA", "RSA", "rsa-sign-v15", "PKCS1v15 padding is shared with encryption; the method fixes the role"),
    _op("pyca-rsa-op-verify", "pyca", "RSA", "RSA", "rsa-verify"),
    _op("pyca-rsa-op-encrypt", "pyca", "RSA", "RSA", "rsa-encrypt"),
    _op("pyca-rsa-op-encrypt-v15", "pyca", "RSA", "RSA", "rsa-encrypt-v15"),
    _op("pyca-rsa-op-decrypt", "pyca", "RSA", "RSA", "rsa-decrypt"),
    # pyca EC
    _key("pyca-ec-key-sign", "pyca", "EC", "EC", ["ec-sign"]),
    _key("pyca-ec-key-signverify", "pyca", "EC", "EC", ["ec-sign", "ec-verify"]),
    _key("pyca-ec-key-exchange", "pyca", "EC", "EC", ["ec-exchange"]),
    _key("pyca-ec-key-export", "pyca", "EC", "EC", ["export"]),
    _key("pyca-ec-key-runtime", "pyca", "EC", "EC", ["ec-sign", "ec-exchange"], runtime=True),
    _op("pyca-ec-op-sign", "pyca", "EC", "EC", "ec-sign"),
    _op("pyca-ec-op-verify", "pyca", "EC", "EC", "ec-verify"),
    _op("pyca-ec-op-exchange", "pyca", "EC", "EC", "ec-exchange"),
    # pyca X25519 / X448 / Ed25519 / Ed448
    _key("pyca-x25519-key-exchange", "pyca", "X25519", "X25519", ["x-exchange"]),
    _key("pyca-x25519-key-export", "pyca", "X25519", "X25519", ["export"]),
    _op("pyca-x25519-op-exchange", "pyca", "X25519", "X25519", "x-exchange"),
    _key("pyca-x448-key-exchange", "pyca", "X448", "X448", ["x-exchange"]),
    _op("pyca-x448-op-exchange", "pyca", "X448", "X448", "x-exchange"),
    _key("pyca-ed25519-key-sign", "pyca", "Ed25519", "Ed25519", ["ed-sign"]),
    _key("pyca-ed25519-key-signverify", "pyca", "Ed25519", "Ed25519", ["ed-sign", "ed-verify"]),
    _key("pyca-ed25519-key-export", "pyca", "Ed25519", "Ed25519", ["export"]),
    _op("pyca-ed25519-op-sign", "pyca", "Ed25519", "Ed25519", "ed-sign"),
    _op("pyca-ed25519-op-verify", "pyca", "Ed25519", "Ed25519", "ed-verify"),
    _key("pyca-ed448-key-sign", "pyca", "Ed448", "Ed448", ["ed-sign"]),
    _op("pyca-ed448-op-sign", "pyca", "Ed448", "Ed448", "ed-sign"),
    # PyCryptodome RSA
    _key("pcd-rsa-key-sign", "pycryptodome", "RSA", "c-RSA", ["c-sign"]),
    _key("pcd-rsa-key-sign-pss", "pycryptodome", "RSA", "c-RSA", ["c-sign-pss"]),
    _key("pcd-rsa-key-signverify", "pycryptodome", "RSA", "c-RSA", ["c-sign", "c-verify"]),
    _key("pcd-rsa-key-decrypt", "pycryptodome", "RSA", "c-RSA", ["c-decrypt"]),
    _key("pcd-rsa-key-export", "pycryptodome", "RSA", "c-RSA", ["export"]),
    _key("pcd-rsa-key-runtime", "pycryptodome", "RSA", "c-RSA", ["c-sign", "c-decrypt"], runtime=True),
    _op("pcd-rsa-op-sign", "pycryptodome", "RSA", "c-RSA", "c-sign"),
    _op("pcd-rsa-op-sign-pss", "pycryptodome", "RSA", "c-RSA", "c-sign-pss"),
    _op("pcd-rsa-op-verify", "pycryptodome", "RSA", "c-RSA", "c-verify"),
    _op("pcd-rsa-op-encrypt", "pycryptodome", "RSA", "c-RSA", "c-encrypt"),
    _op("pcd-rsa-op-encrypt-v15", "pycryptodome", "RSA", "c-RSA", "c-encrypt-v15"),
    _op("pcd-rsa-op-decrypt", "pycryptodome", "RSA", "c-RSA", "c-decrypt"),
    # PyCryptodome ECC
    _key("pcd-ecc-key-sign", "pycryptodome", "EC", "c-EC", ["ecc-sign"]),
    _key("pcd-ecc-key-signverify", "pycryptodome", "EC", "c-EC", ["ecc-sign", "ecc-verify"]),
    _key("pcd-ecc-key-export", "pycryptodome", "EC", "c-EC", ["export"]),
    _op("pcd-ecc-op-sign", "pycryptodome", "EC", "c-EC", "ecc-sign"),
    _op("pcd-ecc-op-verify", "pycryptodome", "EC", "c-EC", "ecc-verify"),
    # negatives (eligible = false, gt_role = NONE)
    _neg("neg-pyca-pss-object", "pyca", "RSA", "<PSS>", "padding.PSS", note="padding object on its own"),
    _neg("neg-pyca-ecdsa-object", "pyca", "EC", "{ec}.ECDSA({hashes}.SHA256())", "ec.ECDSA", note="signature-algorithm object on its own"),
    _neg("neg-pyca-isinstance", "pyca", "RSA", "isinstance(data, {rsa}.RSAPrivateKey)", "isinstance", note="type reference"),
    _neg("neg-pyca-aesgcm-encrypt", "pyca", "other", "aead.encrypt(sig[:12], data, None)", "AESGCM.encrypt",
         setup=["aead = {AESGCM}({AESGCM}.generate_key(bit_length=256))"], note="AEAD encrypt, not public-key"),
    _neg("neg-pyca-chacha-decrypt", "pyca", "other", "aead.decrypt(sig[:12], ct, None)", "ChaCha20Poly1305.decrypt",
         setup=["aead = {ChaCha20Poly1305}({ChaCha20Poly1305}.generate_key())"], note="AEAD decrypt, not public-key"),
    _neg("neg-pyca-fernet-encrypt", "pyca", "other", "box.encrypt(data)", "Fernet.encrypt",
         setup=["box = {Fernet}({Fernet}.generate_key())"], note="symmetric token encryption"),
    _neg("neg-local-sign-method", "unknown", "other", "Token().sign(data)", "Token.sign",
         prelude=["class Token:", "    def sign(self, payload):", "        return payload[::-1]"], note="unrelated .sign method"),
    _neg("neg-local-rsa-named", "unknown", "other", "rsa_sign(data)", "rsa_sign",
         prelude=["def rsa_sign(payload):", "    return payload[::-1]"], note="crypto-like name, no cryptography"),
    _neg("neg-string-literal", "unknown", "other", '"rsa.generate_private_key(public_exponent=65537, key_size=2048)"', "string literal",
         note="API name inside a string"),
    _neg("neg-comment", "unknown", "other", "# key = rsa.generate_private_key(public_exponent=65537, key_size=2048)", "comment",
         note="API name inside a comment"),
    _neg("neg-out-of-scope-ecdsa", "out-of-scope:ecdsa", "EC", "SigningKey.generate(curve=NIST256p)", "ecdsa.SigningKey.generate",
         prelude=["from ecdsa import SigningKey, NIST256p"], note="python-ecdsa is outside the supported libraries"),
    _neg("neg-pcd-aes-encrypt", "pycryptodome", "other", "{AES}.new(sig[:16], {AES}.MODE_GCM).encrypt(data)", "AES.new(...).encrypt",
         note="symmetric cipher"),
    _neg("neg-pcd-hash", "pycryptodome", "other", "{SHA256}.new(data).hexdigest()", "SHA256.new", note="hash only"),
)

# --------------------------------------------------------------------- labels
API_OF_GEN = {"RSA": "rsa.generate_private_key", "EC": "ec.generate_private_key", "X25519": "X25519PrivateKey.generate",
              "X448": "X448PrivateKey.generate", "Ed25519": "Ed25519PrivateKey.generate", "Ed448": "Ed448PrivateKey.generate",
              "c-RSA": "RSA.generate", "c-EC": "ECC.generate"}
API_OF_OP = {
    "rsa-sign": "RSAPrivateKey.sign", "rsa-sign-v15": "RSAPrivateKey.sign", "rsa-verify": "RSAPublicKey.verify",
    "rsa-encrypt": "RSAPublicKey.encrypt", "rsa-encrypt-v15": "RSAPublicKey.encrypt", "rsa-decrypt": "RSAPrivateKey.decrypt",
    "ec-sign": "EllipticCurvePrivateKey.sign", "ec-verify": "EllipticCurvePublicKey.verify",
    "ec-exchange": "EllipticCurvePrivateKey.exchange", "c-sign": "pkcs1_15.new(...).sign", "c-sign-pss": "pss.new(...).sign",
    "c-verify": "pkcs1_15.new(...).verify", "c-encrypt": "PKCS1_OAEP.new(...).encrypt",
    "c-encrypt-v15": "PKCS1_v1_5.new(...).encrypt", "c-decrypt": "PKCS1_OAEP.new(...).decrypt",
    "ecc-sign": "DSS.new(...).sign", "ecc-verify": "DSS.new(...).verify",
}
API_OF_LOAD = {"pyca": "serialization.load_pem_private_key", "c-RSA": "RSA.import_key", "c-EC": "ECC.import_key"}


def labels(b: Base, operator: str) -> dict:
    """Ground truth for one instance (fields of the frozen site schema)."""
    loaded = operator == EVIDENCE_CHANGE
    if b.kind == "neg":
        return {"library": b.library, "algorithm": b.algorithm, "api_call": b.neg_api, "method": "", "key_provenance": "n/a",
                "gt_role": "NONE", "assessability": "DETERMINATE", "eligible": False, "hybrid_component": False,
                "obvious_from_name": None, "evidence_needed": "none", "evidence_scope": "call"}
    algorithm = b.algorithm
    if loaded and b.library == "pyca" and b.algorithm in SINGLE_PURPOSE:
        algorithm = "other"          # a PEM loader does not reveal X25519 vs X448 or Ed25519 vs Ed448
    local_scope = operator in ("identity", "alias-import", EVIDENCE_CHANGE)
    rec = {"library": b.library, "algorithm": algorithm, "hybrid_component": False, "eligible": True}
    if b.kind == "op":
        op = b.uses[0]
        role = _op_role(op)
        api = API_OF_OP.get(op) or {"x-exchange": f"{b.gen}PrivateKey.exchange", "ed-sign": f"{b.gen}PrivateKey.sign",
                                    "ed-verify": f"{b.gen}PublicKey.verify"}[op]
        rec.update({"api_call": api, "method": _op_method(op),
                    "gt_role": role, "assessability": "DETERMINATE", "obvious_from_name": True, "evidence_needed": "none",
                    "evidence_scope": "function" if local_scope else "cross-function"})
        if loaded:
            rec["key_provenance"] = "loaded-PEM"
        elif operator == "class-method":
            rec.update(key_provenance="attribute", ultimate_provenance=["generated"])
        elif local_scope:
            rec["key_provenance"] = "generated"
        else:
            rec.update(key_provenance="parameter", ultimate_provenance=["generated"])
        return rec
    # key site
    rec.update({"api_call": API_OF_LOAD[b.lib_key] if loaded else API_OF_GEN[b.gen],
                "method": "load_pem_private_key" if loaded and b.library == "pyca" else
                          ("import_key" if loaded else ("generate" if b.library == "pycryptodome" or b.gen in SINGLE_PURPOSE else "generate_private_key")),
                "key_provenance": "loaded-PEM" if loaded else "generated"})
    if b.runtime:
        rec.update(gt_role="UNKNOWN", assessability="INDETERMINATE", possible_roles=sorted({_op_role(u) for u in b.uses}),
                   obvious_from_name=False, evidence_needed="runtime-value", evidence_scope="runtime-value")
        return rec
    if b.uses == ("export",):
        rec.update(gt_role="KEY_MATERIAL_ONLY", assessability="DETERMINATE", obvious_from_name=False,
                   evidence_needed="downstream-usage", evidence_scope="function" if local_scope else "cross-function")
        return rec
    roles = [_op_role(u) for u in b.uses]
    assert len({FAMILY[r] for r in roles}) == 1, b.id
    primary = "SIGN" if "SIGN" in roles else roles[0]
    secondary = sorted(set(roles) - {primary})
    single = b.gen in SINGLE_PURPOSE and not loaded
    rec.update(gt_role=primary, assessability="DETERMINATE", obvious_from_name=single,
               evidence_needed="none" if single else "downstream-usage",
               evidence_scope="function" if local_scope else "cross-function")
    if secondary:
        rec["secondary_roles"] = secondary
    return rec


# --------------------------------------------------------------------- rendering
def _names(seed: int, b: Base, operator: str) -> dict[str, str]:
    rng = random.Random(f"{seed}:{b.id}:{operator}")
    return {"var": rng.choice(["key", "k", "priv", "sk", "signing_key", "kp", "material"]),
            "attr": rng.choice(["key", "_key", "private_key", "_material"]),
            "cls": rng.choice(["Service", "Client", "Backend", "Session", "Engine"]),
            "helper": rng.choice(["_new_key", "_make_key", "_build", "_create"]),
            "user": rng.choice(["_use", "_apply", "_handle", "_process"])}


def _expand(s: str) -> str:
    for k, v in MACROS.items():
        s = s.replace(k, v)
    return s


def _use_expr(b: Base, u: str) -> str:
    return _expand(EXPORT[b.lib_key] if u == "export" else OPS[u])


def _uses_block(b: Base, K: str, ind: str, site_first: bool) -> list[str]:
    exprs = [_use_expr(b, u).replace("{K}", K) for u in b.uses]
    mark = SITE if site_first else ""
    if b.runtime:
        return [f'{ind}if alg == "A":', f"{ind}    r0 = {exprs[0]}{mark}", f"{ind}else:", f"{ind}    r0 = {exprs[1]}",
                f"{ind}return r0"]
    out = [f"{ind}r{i} = {e}{mark if i == 0 else ''}" for i, e in enumerate(exprs)]
    rs = ", ".join(f"r{i}" for i in range(len(exprs)))
    return out + [f"{ind}return ({rs},)" if len(exprs) == 1 else f"{ind}return ({rs})"]


def _neg_line(b: Base, ind: str) -> list[str]:
    site = _expand(b.neg_site)
    if site.startswith("#"):
        return [f"{ind}{site}{SITE}", f"{ind}r0 = None", f"{ind}return r0"]
    return [f"{ind}r0 = {site}{SITE}", f"{ind}return r0"]


def render(b: Base, operator: str, seed: int) -> tuple[str, int]:
    """Python source of one instance and the 1-based line of its site."""
    n = _names(seed, b, operator)
    key_mark = SITE if b.kind == "key" else ""
    make = _expand(LOAD["pyca" if b.library == "pyca" else b.lib_key] if operator == EVIDENCE_CHANGE else GEN[b.gen]) if b.kind != "neg" else ""
    params = PARAMS + (", pem" if operator == EVIDENCE_CHANGE else "")
    body: list[str] = list(b.prelude) + ([""] if b.prelude else [])
    if b.kind == "neg":
        setup = [_expand(s) for s in b.setup]
        if operator == "wrapper-function":
            # neutral helper names for negatives, so that no name suggests a key
            body += [f"def {n['user']}({PARAMS}):", *[f"    {s}" for s in setup], *_neg_line(b, "    "), "", "",
                     f"def run({PARAMS}):", f"    return {n['user']}({PARAMS})"]
        elif operator == "class-method":
            body += [f"class {n['cls']}:", f"    def act(self, {PARAMS}):", *[f"        {s}" for s in setup], *_neg_line(b, "        ")]
        else:
            body += [f"def run({PARAMS}):", *[f"    {s}" for s in setup], *_neg_line(b, "    ")]
    elif operator in ("identity", "alias-import", EVIDENCE_CHANGE):
        body += [f"def run({params}):", f"    {n['var']} = {make}{key_mark}", *_uses_block(b, n["var"], "    ", b.kind == "op")]
    elif operator == "wrapper-function":
        if b.kind == "key":
            body += [f"def {n['helper']}():", f"    return {make}{SITE}", "", "",
                     f"def run({PARAMS}):", f"    {n['var']} = {n['helper']}()", *_uses_block(b, n["var"], "    ", False)]
        else:
            site = _use_expr(b, b.uses[0]).replace("{K}", "k")
            body += [f"def {n['helper']}(k, {PARAMS}):", f"    return {site}{SITE}", "", "",
                     f"def run({PARAMS}):", f"    {n['var']} = {make}", f"    return {n['helper']}({n['var']}, {PARAMS})"]
    elif operator == "class-method":
        K = f"self.{n['attr']}"
        body += [f"class {n['cls']}:", "    def __init__(self):", f"        {K} = {make}{key_mark}", "",
                 f"    def act(self, {PARAMS}):", *_uses_block(b, K, "        ", b.kind == "op")]
    elif operator in ("cross-function", "dict-dispatch"):
        body += [f"def {n['user']}(k, {PARAMS}):", *_uses_block(b, "k", "    ", b.kind == "op"), "", ""]
        if operator == "dict-dispatch":
            key = "alg" if b.runtime else '"default"'
            body += [f'HANDLERS = {{"default": {n["user"]}, "A": {n["user"]}}}', "", "",
                     f"def run({PARAMS}):", f"    {n['var']} = {make}{key_mark}", f"    return HANDLERS[{key}]({n['var']}, {PARAMS})"]
        else:
            body += [f"def run({PARAMS}):", f"    {n['var']} = {make}{key_mark}", f"    return {n['user']}({n['var']}, {PARAMS})"]
    else:
        raise ValueError(operator)
    text = "\n".join(body)
    used = sorted({m for m in re.findall(r"\{(\w+)\}", text) if m in MODULES})
    alias = operator == "alias-import"
    mods = {m: (f"_{m.lower()}_mod" if alias else m) for m in MODULES}
    imports = [MODULES[m] + (f" as {mods[m]}" if alias else "") for m in used]
    for m in used:
        text = text.replace("{" + m + "}", mods[m])
    header = [f'"""Synthetic case {b.id} / {operator} (pqscan synthetic generator {GENERATOR_VERSION}). Never executed."""']
    lines = header + imports + ["", ""] + text.split("\n")
    site = next(i for i, l in enumerate(lines, 1) if l.endswith(SITE))
    lines[site - 1] = lines[site - 1][: -len(SITE)]
    return "\n".join(lines) + "\n", site


# --------------------------------------------------------------------- dataset
def operators_for(b: Base) -> tuple[str, ...]:
    return NEGATIVE_OPERATORS if b.kind == "neg" else OPERATORS + (EVIDENCE_CHANGE,)


def generator_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def base_split(seed: int) -> dict[str, str]:
    """Half of the base cases (stratified by kind) are held out; every variant follows its base case."""
    out = {}
    for kind in ("key", "op", "neg"):
        ids = sorted(b.id for b in BASE_CASES if b.kind == kind)
        random.Random(f"{seed}:split:{kind}").shuffle(ids)
        for i, x in enumerate(ids):
            out[x] = "synthetic-holdout" if i % 2 else "synthetic-dev"
    return out


def generate(out: Path, seed: int = DEFAULT_SEED) -> dict:
    out = Path(out)
    commit = "generator-" + generator_hash()[:12]
    split = base_split(seed)
    records, provenance = [], []
    for b in BASE_CASES:
        for op in operators_for(b):
            src, line = render(b, op, seed)
            rel = f"cases/{b.id}/{op}.py"
            path = out / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(src.encode("utf-8"))
            rec = {"site_id": f"S-{b.id}.{op}", "dataset": "synthetic", "repo": "synthetic", "commit": commit, "file": rel,
                   "line_start": line, "line_end": line, "scope": "app", "base_case": b.id, "transformation": op, **labels(b, op)}
            if b.note:
                rec["notes"] = b.note
            if rec["algorithm"] == "other" and b.kind != "neg":
                rec["notes"] = (rec.get("notes", "") + "; " if rec.get("notes") else "") + "algorithm not determinable from a PEM loader"
            records.append(rec)
            provenance.append({"site_id": rec["site_id"], "base_case": b.id, "operator": op, "kind": b.kind,
                               "evidence_change": op == EVIDENCE_CHANGE, "split": split[b.id], "file": rel,
                               "sha256": hashlib.sha256(src.encode("utf-8")).hexdigest()})
    with (out / "sites.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    subset = validation_subset(provenance, seed)
    with (out / "validation_subset.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site_id", "file", "line_start", "line_end"])
        by_id = {r["site_id"]: r for r in records}
        for sid in subset:
            w.writerow([sid, by_id[sid]["file"], by_id[sid]["line_start"], by_id[sid]["line_end"]])
    manifest = {"generator_version": GENERATOR_VERSION, "generator_sha256": generator_hash(), "seed": seed,
                "operators": list(OPERATORS), "evidence_change": EVIDENCE_CHANGE,
                "counts": {"base_cases": len(BASE_CASES), "instances": len(records),
                           "by_kind": {k: sum(p["kind"] == k for p in provenance) for k in ("key", "op", "neg")}},
                "validation_subset": {"fraction": 0.2, "size": len(subset), "stratified_by": "operator"},
                "split": dict(sorted(split.items())), "instances": provenance}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return manifest


def validation_subset(provenance: list[dict], seed: int, fraction: float = 0.2) -> list[str]:
    """Blind sample for the external annotator: `fraction` of each operator's instances, at least one each."""
    chosen = []
    for op in OPERATORS + (EVIDENCE_CHANGE,):
        ids = sorted(p["site_id"] for p in provenance if p["operator"] == op)
        rng = random.Random(f"{seed}:validation:{op}")
        k = max(1, round(fraction * len(ids)))
        chosen += sorted(rng.sample(ids, k))
    return chosen


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pqscan.bench.synth", description="Generate the synthetic benchmark (Dataset A)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    a = ap.parse_args(argv)
    m = generate(a.out, a.seed)
    print(f"wrote {m['counts']['instances']} instances from {m['counts']['base_cases']} base cases to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
