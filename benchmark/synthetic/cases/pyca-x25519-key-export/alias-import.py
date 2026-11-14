"""Synthetic case pyca-x25519-key-export / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import serialization as _serialization_mod
from cryptography.hazmat.primitives.asymmetric import x25519 as _x25519_mod


def run(data, sig, ct, peer_public, alg):
    kp = _x25519_mod.X25519PrivateKey.generate()
    r0 = kp.private_bytes(_serialization_mod.Encoding.PEM, _serialization_mod.PrivateFormat.PKCS8, _serialization_mod.NoEncryption())
    return (r0,)
