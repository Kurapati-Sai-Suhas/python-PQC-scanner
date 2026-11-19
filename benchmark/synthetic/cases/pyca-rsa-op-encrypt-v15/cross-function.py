"""Synthetic case pyca-rsa-op-encrypt-v15 / cross-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _use(k, data, sig, ct, peer_public, alg):
    r0 = k.public_key().encrypt(data, padding.PKCS1v15())
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return _use(key, data, sig, ct, peer_public, alg)
