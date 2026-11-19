"""Synthetic case pyca-rsa-op-sign-v15 / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _create(k, data, sig, ct, peer_public, alg):
    return k.sign(data, padding.PKCS1v15(), hashes.SHA256())


def run(data, sig, ct, peer_public, alg):
    k = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return _create(k, data, sig, ct, peer_public, alg)
