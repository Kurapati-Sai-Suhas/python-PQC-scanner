"""Synthetic case pyca-ed25519-key-signverify / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed25519_mod


def run(data, sig, ct, peer_public, alg):
    kp = _ed25519_mod.Ed25519PrivateKey.generate()
    r0 = kp.sign(data)
    r1 = kp.public_key().verify(sig, data)
    return (r0, r1)
