"""Synthetic case pyca-ed25519-key-export / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def _build():
    return ed25519.Ed25519PrivateKey.generate()


def run(data, sig, ct, peer_public, alg):
    material = _build()
    r0 = material.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
