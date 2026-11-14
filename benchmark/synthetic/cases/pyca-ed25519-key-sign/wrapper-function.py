"""Synthetic case pyca-ed25519-key-sign / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _build():
    return ed25519.Ed25519PrivateKey.generate()


def run(data, sig, ct, peer_public, alg):
    signing_key = _build()
    r0 = signing_key.sign(data)
    return (r0,)
