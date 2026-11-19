"""Synthetic case pyca-ed25519-op-sign / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def run(data, sig, ct, peer_public, alg):
    priv = ed25519.Ed25519PrivateKey.generate()
    r0 = priv.sign(data)
    return (r0,)
