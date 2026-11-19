"""Synthetic case neg-pyca-isinstance / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import rsa


def run(data, sig, ct, peer_public, alg):
    r0 = isinstance(data, rsa.RSAPrivateKey)
    return r0
