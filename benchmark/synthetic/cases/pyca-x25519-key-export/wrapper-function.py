"""Synthetic case pyca-x25519-key-export / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519


def _new_key():
    return x25519.X25519PrivateKey.generate()


def run(data, sig, ct, peer_public, alg):
    material = _new_key()
    r0 = material.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
