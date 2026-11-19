"""Synthetic case neg-pyca-ecdsa-object / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _apply(data, sig, ct, peer_public, alg):
    r0 = ec.ECDSA(hashes.SHA256())
    return r0


def run(data, sig, ct, peer_public, alg):
    return _apply(data, sig, ct, peer_public, alg)
