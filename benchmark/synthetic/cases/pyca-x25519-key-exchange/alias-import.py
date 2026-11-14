"""Synthetic case pyca-x25519-key-exchange / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x25519 as _x25519_mod


def run(data, sig, ct, peer_public, alg):
    signing_key = _x25519_mod.X25519PrivateKey.generate()
    r0 = signing_key.exchange(peer_public)
    return (r0,)
