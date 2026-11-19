"""Synthetic case pyca-x448-op-exchange / cross-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(peer_public)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    key = x448.X448PrivateKey.generate()
    return _apply(key, data, sig, ct, peer_public, alg)
