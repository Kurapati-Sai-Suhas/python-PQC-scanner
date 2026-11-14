"""Synthetic case pyca-rsa-op-sign-v15 / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def run(data, sig, ct, peer_public, alg):
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    r0 = key.sign(data, padding.PKCS1v15(), hashes.SHA256())
    return (r0,)
