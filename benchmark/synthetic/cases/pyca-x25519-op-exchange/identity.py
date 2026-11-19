"""Synthetic case pyca-x25519-op-exchange / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x25519


def run(data, sig, ct, peer_public, alg):
    key = x25519.X25519PrivateKey.generate()
    r0 = key.exchange(peer_public)
    return (r0,)
