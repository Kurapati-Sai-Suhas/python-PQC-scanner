"""Synthetic case pyca-ed25519-key-export / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    sk = ed25519.Ed25519PrivateKey.generate()
    return HANDLERS["default"](sk, data, sig, ct, peer_public, alg)
