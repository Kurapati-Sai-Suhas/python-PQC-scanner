"""Synthetic case pyca-ed25519-key-export / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed25519_mod
from cryptography.hazmat.primitives import serialization as _serialization_mod


def run(data, sig, ct, peer_public, alg):
    key = _ed25519_mod.Ed25519PrivateKey.generate()
    r0 = key.private_bytes(_serialization_mod.Encoding.PEM, _serialization_mod.PrivateFormat.PKCS8, _serialization_mod.NoEncryption())
    return (r0,)
