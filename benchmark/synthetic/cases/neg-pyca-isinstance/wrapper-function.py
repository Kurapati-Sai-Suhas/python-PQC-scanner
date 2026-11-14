"""Synthetic case neg-pyca-isinstance / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import rsa


def _apply(data, sig, ct, peer_public, alg):
    r0 = isinstance(data, rsa.RSAPrivateKey)
    return r0


def run(data, sig, ct, peer_public, alg):
    return _apply(data, sig, ct, peer_public, alg)
