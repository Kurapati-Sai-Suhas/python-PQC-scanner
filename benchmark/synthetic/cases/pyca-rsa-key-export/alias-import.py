"""Synthetic case pyca-rsa-key-export / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import rsa as _rsa_mod
from cryptography.hazmat.primitives import serialization as _serialization_mod


def run(data, sig, ct, peer_public, alg):
    kp = _rsa_mod.generate_private_key(public_exponent=65537, key_size=3072)
    r0 = kp.private_bytes(_serialization_mod.Encoding.PEM, _serialization_mod.PrivateFormat.PKCS8, _serialization_mod.NoEncryption())
    return (r0,)
