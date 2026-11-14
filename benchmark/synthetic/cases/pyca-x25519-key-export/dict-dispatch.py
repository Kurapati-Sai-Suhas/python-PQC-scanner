"""Synthetic case pyca-x25519-key-export / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    k = x25519.X25519PrivateKey.generate()
    return HANDLERS["default"](k, data, sig, ct, peer_public, alg)
