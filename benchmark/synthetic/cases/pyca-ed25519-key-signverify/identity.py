"""Synthetic case pyca-ed25519-key-signverify / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def run(data, sig, ct, peer_public, alg):
    signing_key = ed25519.Ed25519PrivateKey.generate()
    r0 = signing_key.sign(data)
    r1 = signing_key.public_key().verify(sig, data)
    return (r0, r1)
