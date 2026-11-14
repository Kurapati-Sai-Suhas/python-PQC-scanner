"""Synthetic case pyca-x448-key-exchange / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    signing_key = serialization.load_pem_private_key(pem, password=None)
    r0 = signing_key.exchange(peer_public)
    return (r0,)
