"""Synthetic case pyca-x448-key-exchange / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448


def run(data, sig, ct, peer_public, alg):
    kp = x448.X448PrivateKey.generate()
    r0 = kp.exchange(peer_public)
    return (r0,)
