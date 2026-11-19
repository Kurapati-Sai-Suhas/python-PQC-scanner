"""Synthetic case pyca-x25519-key-exchange / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    key = serialization.load_pem_private_key(pem, password=None)
    r0 = key.exchange(peer_public)
    return (r0,)
