"""Synthetic case neg-pyca-pss-object / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def _handle(data, sig, ct, peer_public, alg):
    r0 = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    return r0


def run(data, sig, ct, peer_public, alg):
    return _handle(data, sig, ct, peer_public, alg)
