"""Knowledge table: fully qualified API -> what value it produces. This is the only place where
library APIs are enumerated for typing; it mirrors docs/specification/api_coverage.md."""
from __future__ import annotations
from dataclasses import dataclass
from ..models import Provenance

PYCA_ASYM = "cryptography.hazmat.primitives.asymmetric."
PYCA_SER = "cryptography.hazmat.primitives.serialization."


@dataclass(frozen=True)
class KeyFactory:
    algorithm: str
    private: bool | None
    provenance: Provenance
    library: str = "pyca"
    row: str = ""


KEY_FACTORIES: dict[str, KeyFactory] = {
    # --- pyca key generation / derivation / construction
    PYCA_ASYM + "rsa.generate_private_key": KeyFactory("RSA", True, Provenance.GENERATED, row="C1"),
    PYCA_ASYM + "rsa.RSAPrivateNumbers.private_key": KeyFactory("RSA", True, Provenance.CONSTRUCTED, row="C2"),
    PYCA_ASYM + "rsa.RSAPublicNumbers.public_key": KeyFactory("RSA", False, Provenance.CONSTRUCTED, row="C2"),
    PYCA_ASYM + "ec.generate_private_key": KeyFactory("EC", True, Provenance.GENERATED, row="C7"),
    PYCA_ASYM + "ec.derive_private_key": KeyFactory("EC", True, Provenance.CONSTRUCTED, row="C8"),
    PYCA_ASYM + "ec.EllipticCurvePublicKey.from_encoded_point": KeyFactory("EC", False, Provenance.CONSTRUCTED, row="C9"),
    PYCA_ASYM + "ec.EllipticCurvePublicNumbers.public_key": KeyFactory("EC", False, Provenance.CONSTRUCTED, row="C9"),
    PYCA_ASYM + "ec.EllipticCurvePrivateNumbers.private_key": KeyFactory("EC", True, Provenance.CONSTRUCTED, row="C9"),
    PYCA_ASYM + "x25519.X25519PrivateKey.generate": KeyFactory("X25519", True, Provenance.GENERATED, row="C13"),
    PYCA_ASYM + "x25519.X25519PrivateKey.from_private_bytes": KeyFactory("X25519", True, Provenance.CONSTRUCTED, row="C13"),
    PYCA_ASYM + "x25519.X25519PublicKey.from_public_bytes": KeyFactory("X25519", False, Provenance.CONSTRUCTED, row="C13"),
    PYCA_ASYM + "x448.X448PrivateKey.generate": KeyFactory("X448", True, Provenance.GENERATED, row="C13"),
    PYCA_ASYM + "x448.X448PrivateKey.from_private_bytes": KeyFactory("X448", True, Provenance.CONSTRUCTED, row="C13"),
    PYCA_ASYM + "x448.X448PublicKey.from_public_bytes": KeyFactory("X448", False, Provenance.CONSTRUCTED, row="C13"),
    PYCA_ASYM + "ed25519.Ed25519PrivateKey.generate": KeyFactory("Ed25519", True, Provenance.GENERATED, row="C15"),
    PYCA_ASYM + "ed25519.Ed25519PrivateKey.from_private_bytes": KeyFactory("Ed25519", True, Provenance.CONSTRUCTED, row="C15"),
    PYCA_ASYM + "ed25519.Ed25519PublicKey.from_public_bytes": KeyFactory("Ed25519", False, Provenance.CONSTRUCTED, row="C15"),
    PYCA_ASYM + "ed448.Ed448PrivateKey.generate": KeyFactory("Ed448", True, Provenance.GENERATED, row="C15"),
    PYCA_ASYM + "ed448.Ed448PrivateKey.from_private_bytes": KeyFactory("Ed448", True, Provenance.CONSTRUCTED, row="C15"),
    PYCA_ASYM + "ed448.Ed448PublicKey.from_public_bytes": KeyFactory("Ed448", False, Provenance.CONSTRUCTED, row="C15"),
    PYCA_ASYM + "dh.DHPrivateNumbers.private_key": KeyFactory("DH", True, Provenance.CONSTRUCTED, row="C16"),
    PYCA_ASYM + "dh.DHPublicNumbers.public_key": KeyFactory("DH", False, Provenance.CONSTRUCTED, row="C16"),
    # --- pyca loaders (algorithm unknown until typed by isinstance/annotation/usage)
    PYCA_SER + "load_pem_private_key": KeyFactory("ANY", True, Provenance.LOADED_PEM, row="C17"),
    PYCA_SER + "load_pem_public_key": KeyFactory("ANY", False, Provenance.LOADED_PEM, row="C17"),
    PYCA_SER + "load_der_private_key": KeyFactory("ANY", True, Provenance.LOADED_DER, row="C18"),
    PYCA_SER + "load_der_public_key": KeyFactory("ANY", False, Provenance.LOADED_DER, row="C18"),
    PYCA_SER + "load_ssh_private_key": KeyFactory("ANY", True, Provenance.LOADED_SSH, row="C19"),
    PYCA_SER + "load_ssh_public_key": KeyFactory("ANY", False, Provenance.LOADED_SSH, row="C19"),
    PYCA_SER + "load_ssh_public_identity": KeyFactory("ANY", False, Provenance.LOADED_SSH, row="C19"),
    # --- PyCryptodome (both roots)
    "Crypto.PublicKey.RSA.generate": KeyFactory("RSA", True, Provenance.GENERATED, "pycryptodome", "D1"),
    "Crypto.PublicKey.RSA.import_key": KeyFactory("RSA", None, Provenance.LOADED_PEM, "pycryptodome", "D2"),
    "Crypto.PublicKey.RSA.importKey": KeyFactory("RSA", None, Provenance.LOADED_PEM, "pycryptodome", "D2"),
    "Crypto.PublicKey.RSA.construct": KeyFactory("RSA", None, Provenance.CONSTRUCTED, "pycryptodome", "D3"),
    "Crypto.PublicKey.ECC.generate": KeyFactory("EC", True, Provenance.GENERATED, "pycryptodome", "D4"),
    "Crypto.PublicKey.ECC.import_key": KeyFactory("EC", None, Provenance.LOADED_PEM, "pycryptodome", "D4"),
    "Crypto.PublicKey.ECC.construct": KeyFactory("EC", None, Provenance.CONSTRUCTED, "pycryptodome", "D4"),
    "Crypto.PublicKey.DSA.generate": KeyFactory("DSA", True, Provenance.GENERATED, "pycryptodome", "D12"),
    "Crypto.PublicKey.DSA.import_key": KeyFactory("DSA", None, Provenance.LOADED_PEM, "pycryptodome", "D12"),
}
for _k in [k for k in KEY_FACTORIES if k.startswith("Crypto.")]:
    KEY_FACTORIES["Cryptodome." + _k[len("Crypto."):]] = KEY_FACTORIES[_k]

# Numbers constructors: the object is not a key yet; `.private_key()` / `.public_key()` makes one.
NUMBERS_CLASSES = {
    PYCA_ASYM + "rsa.RSAPrivateNumbers", PYCA_ASYM + "rsa.RSAPublicNumbers",
    PYCA_ASYM + "ec.EllipticCurvePrivateNumbers", PYCA_ASYM + "ec.EllipticCurvePublicNumbers",
    PYCA_ASYM + "dh.DHPrivateNumbers", PYCA_ASYM + "dh.DHPublicNumbers",
}

CERT_LOADERS = {"cryptography.x509.load_pem_x509_certificate", "cryptography.x509.load_der_x509_certificate"}

SIGNER_MODULES = {"Signature.pkcs1_15": "pkcs1_15", "Signature.pss": "pss", "Signature.DSS": "DSS", "Signature.eddsa": "eddsa",
                  "Signature.PKCS1_v1_5": "PKCS1_v1_5", "Signature.PKCS1_PSS": "PKCS1_PSS"}
CIPHER_MODULES = {"Cipher.PKCS1_OAEP": "PKCS1_OAEP", "Cipher.PKCS1_v1_5": "PKCS1_v1_5"}

# Type names usable in annotations / isinstance guards
KEY_CLASS_TYPES: dict[str, tuple[str, bool | None]] = {
    PYCA_ASYM + "rsa.RSAPrivateKey": ("RSA", True), PYCA_ASYM + "rsa.RSAPublicKey": ("RSA", False),
    PYCA_ASYM + "ec.EllipticCurvePrivateKey": ("EC", True), PYCA_ASYM + "ec.EllipticCurvePublicKey": ("EC", False),
    PYCA_ASYM + "x25519.X25519PrivateKey": ("X25519", True), PYCA_ASYM + "x25519.X25519PublicKey": ("X25519", False),
    PYCA_ASYM + "x448.X448PrivateKey": ("X448", True), PYCA_ASYM + "x448.X448PublicKey": ("X448", False),
    PYCA_ASYM + "ed25519.Ed25519PrivateKey": ("Ed25519", True), PYCA_ASYM + "ed25519.Ed25519PublicKey": ("Ed25519", False),
    PYCA_ASYM + "ed448.Ed448PrivateKey": ("Ed448", True), PYCA_ASYM + "ed448.Ed448PublicKey": ("Ed448", False),
    PYCA_ASYM + "dh.DHPrivateKey": ("DH", True), PYCA_ASYM + "dh.DHPublicKey": ("DH", False),
    "Crypto.PublicKey.RSA.RsaKey": ("RSA", None), "Crypto.PublicKey.ECC.EccKey": ("EC", None),
    "Cryptodome.PublicKey.RSA.RsaKey": ("RSA", None), "Cryptodome.PublicKey.ECC.EccKey": ("EC", None),
}

# Known non-public-key constructors whose encrypt/decrypt/sign/verify must never be treated as RSA/EC
NON_PK_OBJECTS = {
    "cryptography.hazmat.primitives.ciphers.aead.AESGCM", "cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305",
    "cryptography.hazmat.primitives.ciphers.aead.AESCCM", "cryptography.hazmat.primitives.ciphers.aead.AESOCB3",
    "cryptography.hazmat.primitives.ciphers.aead.AESSIV", "cryptography.hazmat.primitives.ciphers.aead.AESGCMSIV",
    "cryptography.hazmat.primitives.ciphers.Cipher", "cryptography.fernet.Fernet", "cryptography.fernet.MultiFernet",
    "cryptography.hazmat.primitives.hmac.HMAC", "cryptography.hazmat.primitives.cmac.CMAC",
    "Crypto.Cipher.AES.new", "Crypto.Cipher.ChaCha20.new", "Crypto.Cipher.ChaCha20_Poly1305.new", "Crypto.Cipher.DES3.new",
    "Crypto.Hash.HMAC.new", "Crypto.Hash.CMAC.new", "Cryptodome.Cipher.AES.new", "Cryptodome.Hash.HMAC.new",
}

PQC_PREFIXES = (PYCA_ASYM + "mlkem.", PYCA_ASYM + "mldsa.", "oqs.", "pqcrypto.")

# Parameter-object constructors (typed as ParamType; never candidates by themselves)
PARAM_CONSTRUCTORS: dict[str, tuple[str, str]] = {
    PYCA_ASYM + "padding.PKCS1v15": ("padding", "PKCS1v15"),
    PYCA_ASYM + "padding.PSS": ("padding", "PSS"),
    PYCA_ASYM + "padding.OAEP": ("padding", "OAEP"),
    PYCA_ASYM + "padding.MGF1": ("mgf", "MGF1"),
    PYCA_ASYM + "ec.ECDSA": ("sigalg", "ECDSA"),
    PYCA_ASYM + "ec.ECDH": ("kex", "ECDH"),
    PYCA_ASYM + "utils.Prehashed": ("prehashed", "Prehashed"),
}
for _h in ("SHA1", "SHA224", "SHA256", "SHA384", "SHA512", "SHA512_224", "SHA512_256", "SHA3_224", "SHA3_256", "SHA3_384", "SHA3_512",
           "BLAKE2b", "BLAKE2s", "MD5", "SM3", "SHAKE128", "SHAKE256"):
    PARAM_CONSTRUCTORS["cryptography.hazmat.primitives.hashes." + _h] = ("hash", _h)
for _c in ("SECP192R1", "SECP224R1", "SECP256R1", "SECP384R1", "SECP521R1", "SECP256K1", "BrainpoolP256R1", "BrainpoolP384R1",
           "BrainpoolP512R1", "SECT163K1", "SECT233K1", "SECT283K1", "SECT409K1", "SECT571K1"):
    PARAM_CONSTRUCTORS[PYCA_ASYM + "ec." + _c] = ("curve", _c)

OPERATION_METHODS = ("sign", "verify", "exchange", "encrypt", "decrypt")
FAMILY_OF_METHOD = {"sign": "SIG", "verify": "SIG", "exchange": "KE", "encrypt": "PKE", "decrypt": "PKE"}
