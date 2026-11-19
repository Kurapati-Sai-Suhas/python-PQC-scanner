"""Synthetic case pyca-x448-key-exchange / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448


def _make_key():
    return x448.X448PrivateKey.generate()


def run(data, sig, ct, peer_public, alg):
    key = _make_key()
    r0 = key.exchange(peer_public)
    return (r0,)
