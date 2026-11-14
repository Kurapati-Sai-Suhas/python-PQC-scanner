"""Synthetic case neg-pyca-isinstance / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import rsa as _rsa_mod


def run(data, sig, ct, peer_public, alg):
    r0 = isinstance(data, _rsa_mod.RSAPrivateKey)
    return r0
