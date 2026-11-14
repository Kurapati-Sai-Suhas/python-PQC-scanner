"""Synthetic case pyca-ed448-key-sign / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448


def run(data, sig, ct, peer_public, alg):
    priv = ed448.Ed448PrivateKey.generate()
    r0 = priv.sign(data)
    return (r0,)
