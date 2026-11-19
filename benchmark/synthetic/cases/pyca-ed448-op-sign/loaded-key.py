"""Synthetic case pyca-ed448-op-sign / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    material = serialization.load_pem_private_key(pem, password=None)
    r0 = material.sign(data)
    return (r0,)
