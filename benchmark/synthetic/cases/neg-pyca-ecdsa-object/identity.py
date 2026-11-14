"""Synthetic case neg-pyca-ecdsa-object / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def run(data, sig, ct, peer_public, alg):
    r0 = ec.ECDSA(hashes.SHA256())
    return r0
