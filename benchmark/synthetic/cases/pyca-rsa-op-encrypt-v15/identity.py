"""Synthetic case pyca-rsa-op-encrypt-v15 / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def run(data, sig, ct, peer_public, alg):
    priv = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    r0 = priv.public_key().encrypt(data, padding.PKCS1v15())
    return (r0,)
