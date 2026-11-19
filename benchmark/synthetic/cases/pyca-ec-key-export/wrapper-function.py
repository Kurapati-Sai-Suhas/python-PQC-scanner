"""Synthetic case pyca-ec-key-export / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


def _build():
    return ec.generate_private_key(ec.SECP256R1())


def run(data, sig, ct, peer_public, alg):
    signing_key = _build()
    r0 = signing_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
