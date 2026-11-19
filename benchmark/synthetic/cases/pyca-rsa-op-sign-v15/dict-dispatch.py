"""Synthetic case pyca-rsa-op-sign-v15 / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data, padding.PKCS1v15(), hashes.SHA256())
    return (r0,)


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    k = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return HANDLERS["default"](k, data, sig, ct, peer_public, alg)
