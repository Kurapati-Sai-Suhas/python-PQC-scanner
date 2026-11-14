"""Synthetic case pyca-ed25519-key-export / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg):
    signing_key = ed25519.Ed25519PrivateKey.generate()
    r0 = signing_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
