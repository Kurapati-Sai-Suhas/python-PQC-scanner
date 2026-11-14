"""Synthetic case pyca-x448-key-exchange / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(peer_public)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    signing_key = x448.X448PrivateKey.generate()
    return _handle(signing_key, data, sig, ct, peer_public, alg)
