"""Synthetic case pyca-rsa-op-encrypt-v15 / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _create(k, data, sig, ct, peer_public, alg):
    return k.public_key().encrypt(data, padding.PKCS1v15())


def run(data, sig, ct, peer_public, alg):
    sk = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return _create(sk, data, sig, ct, peer_public, alg)
