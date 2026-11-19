"""Synthetic case pyca-x25519-op-exchange / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x25519


def _create(k, data, sig, ct, peer_public, alg):
    return k.exchange(peer_public)


def run(data, sig, ct, peer_public, alg):
    key = x25519.X25519PrivateKey.generate()
    return _create(key, data, sig, ct, peer_public, alg)
