"""Synthetic case pyca-ed25519-key-export / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    sk = ed25519.Ed25519PrivateKey.generate()
    return _handle(sk, data, sig, ct, peer_public, alg)
