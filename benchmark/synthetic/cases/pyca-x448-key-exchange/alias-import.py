"""Synthetic case pyca-x448-key-exchange / alias-import (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448 as _x448_mod


def run(data, sig, ct, peer_public, alg):
    signing_key = _x448_mod.X448PrivateKey.generate()
    r0 = signing_key.exchange(peer_public)
    return (r0,)
