"""Synthetic case pyca-rsa-op-sign-v15 / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    key = serialization.load_pem_private_key(pem, password=None)
    r0 = key.sign(data, padding.PKCS1v15(), hashes.SHA256())
    return (r0,)
