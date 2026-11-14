"""Synthetic case pyca-x448-op-exchange / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448


def _make_key(k, data, sig, ct, peer_public, alg):
    return k.exchange(peer_public)


def run(data, sig, ct, peer_public, alg):
    kp = x448.X448PrivateKey.generate()
    return _make_key(kp, data, sig, ct, peer_public, alg)
