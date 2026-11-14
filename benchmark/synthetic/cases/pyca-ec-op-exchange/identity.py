"""Synthetic case pyca-ec-op-exchange / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


def run(data, sig, ct, peer_public, alg):
    key = ec.generate_private_key(ec.SECP256R1())
    r0 = key.exchange(ec.ECDH(), peer_public)
    return (r0,)
