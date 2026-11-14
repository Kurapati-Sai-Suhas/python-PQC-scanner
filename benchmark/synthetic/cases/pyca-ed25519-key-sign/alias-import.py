"""Synthetic case pyca-ed25519-key-sign / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed25519_mod


def run(data, sig, ct, peer_public, alg):
    key = _ed25519_mod.Ed25519PrivateKey.generate()
    r0 = key.sign(data)
    return (r0,)
