"""Synthetic case pyca-x448-op-exchange / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448


def run(data, sig, ct, peer_public, alg):
    signing_key = x448.X448PrivateKey.generate()
    r0 = signing_key.exchange(peer_public)
    return (r0,)
