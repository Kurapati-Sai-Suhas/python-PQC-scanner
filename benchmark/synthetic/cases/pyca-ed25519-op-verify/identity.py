"""Synthetic case pyca-ed25519-op-verify / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def run(data, sig, ct, peer_public, alg):
    k = ed25519.Ed25519PrivateKey.generate()
    r0 = k.public_key().verify(sig, data)
    return (r0,)
