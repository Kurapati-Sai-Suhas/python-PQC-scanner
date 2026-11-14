"""Synthetic case pyca-ed25519-key-signverify / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _make_key():
    return ed25519.Ed25519PrivateKey.generate()


def run(data, sig, ct, peer_public, alg):
    priv = _make_key()
    r0 = priv.sign(data)
    r1 = priv.public_key().verify(sig, data)
    return (r0, r1)
