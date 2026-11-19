"""Synthetic case pyca-rsa-key-export / cross-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    sk = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return _apply(sk, data, sig, ct, peer_public, alg)
