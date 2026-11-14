"""Synthetic case pyca-ed25519-op-verify / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed25519_mod


def run(data, sig, ct, peer_public, alg):
    signing_key = _ed25519_mod.Ed25519PrivateKey.generate()
    r0 = signing_key.public_key().verify(sig, data)
    return (r0,)
