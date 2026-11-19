"""Synthetic case pyca-ed448-key-sign / alias-import (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448 as _ed448_mod


def run(data, sig, ct, peer_public, alg):
    k = _ed448_mod.Ed448PrivateKey.generate()
    r0 = k.sign(data)
    return (r0,)
