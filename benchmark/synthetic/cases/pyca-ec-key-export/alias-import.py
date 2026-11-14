"""Synthetic case pyca-ec-key-export / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec as _ec_mod
from cryptography.hazmat.primitives import serialization as _serialization_mod


def run(data, sig, ct, peer_public, alg):
    key = _ec_mod.generate_private_key(_ec_mod.SECP256R1())
    r0 = key.private_bytes(_serialization_mod.Encoding.PEM, _serialization_mod.PrivateFormat.PKCS8, _serialization_mod.NoEncryption())
    return (r0,)
