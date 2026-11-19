"""Synthetic case pyca-ec-key-exchange / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


def run(data, sig, ct, peer_public, alg):
    sk = ec.generate_private_key(ec.SECP256R1())
    r0 = sk.exchange(ec.ECDH(), peer_public)
    return (r0,)
