"""Synthetic case pyca-ed448-op-sign / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448 as _ed448_mod


def run(data, sig, ct, peer_public, alg):
    priv = _ed448_mod.Ed448PrivateKey.generate()
    r0 = priv.sign(data)
    return (r0,)
