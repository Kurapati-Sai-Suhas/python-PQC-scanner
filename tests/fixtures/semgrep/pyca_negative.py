"""Module A negative fixture — PyCA imports present, but no line here is an eligible
candidate except the ones explicitly marked. Parameter objects, type references,
comments and docstrings must not be reported."""
from cryptography.hazmat.primitives.asymmetric import padding, ec, rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

RSA1_5 = padding.PKCS1v15()          # parameter object only — not a candidate
RSA_OAEP = padding.OAEP(padding.MGF1(hashes.SHA1()), hashes.SHA1(), None)
CURVES = {"P-256": ec.SECP256R1, "P-384": ec.SECP384R1}
ECDSA_SHA256 = ec.ECDSA(hashes.SHA256())


def is_rsa(key):
    # rsa.generate_private_key is mentioned in this comment but never called
    return isinstance(key, rsa.RSAPrivateKey)


def aead(key, nonce, data):
    cipher = AESGCM(key)
    # symmetric encrypt/decrypt on an AEAD object: method-shaped, so it IS a candidate
    # (Module B must later reject it as a non-public-key receiver)
    ct = cipher.encrypt(nonce, data, None)  # expect: pqscan.common.method.candidate
    return cipher.decrypt(nonce, ct, None)  # expect: pqscan.common.method.candidate


def docstring_mention():
    """Call ec.generate_private_key(ec.SECP256R1()) to make a key. (docstring only)"""
    return "sign verify exchange"
