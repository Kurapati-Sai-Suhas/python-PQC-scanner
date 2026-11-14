"""Synthetic case pyca-x25519-key-export / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519


def run(data, sig, ct, peer_public, alg):
    k = x25519.X25519PrivateKey.generate()
    r0 = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
