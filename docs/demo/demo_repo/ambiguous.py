# DEMONSTRATION FIXTURE — synthetic, written for this demo.
# Never imported or executed; it exists only to be scanned by pqscan. Contains no key material.
"""Deliberately ambiguous cases (synthetic example).

1. `sign_with` receives its key through an untyped parameter and passes no algorithm-specific argument,
   so a static scanner cannot tell whether this is RSA, ECDSA, an HMAC object or something else.
2. `dual_use_key` generates one RSA key that reaches a signature consumer on one branch and a decryption
   consumer on the other, so the key's role depends on which path runs.
"""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def sign_with(key, data):
    return key.sign(data)


def dual_use_key(blob: bytes, mode: str) -> bytes:
    shared_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    if mode == "sign":
        return shared_key.sign(blob, padding.PKCS1v15(), hashes.SHA256())
    return shared_key.decrypt(blob, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
