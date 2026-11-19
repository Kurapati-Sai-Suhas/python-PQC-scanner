"""Synthetic case pyca-rsa-op-encrypt-v15 / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    k = serialization.load_pem_private_key(pem, password=None)
    r0 = k.public_key().encrypt(data, padding.PKCS1v15())
    return (r0,)
