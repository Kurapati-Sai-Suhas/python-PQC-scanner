"""Synthetic case pyca-ed25519-op-sign / alias-import (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed25519_mod


def run(data, sig, ct, peer_public, alg):
    sk = _ed25519_mod.Ed25519PrivateKey.generate()
    r0 = sk.sign(data)
    return (r0,)
