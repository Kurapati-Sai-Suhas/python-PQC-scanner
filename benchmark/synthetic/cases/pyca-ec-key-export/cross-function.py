"""Synthetic case pyca-ec-key-export / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    key = ec.generate_private_key(ec.SECP256R1())
    return _apply(key, data, sig, ct, peer_public, alg)
