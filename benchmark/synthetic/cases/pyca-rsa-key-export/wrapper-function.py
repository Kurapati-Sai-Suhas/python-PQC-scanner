"""Synthetic case pyca-rsa-key-export / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def _build():
    return rsa.generate_private_key(public_exponent=65537, key_size=3072)


def run(data, sig, ct, peer_public, alg):
    signing_key = _build()
    r0 = signing_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
