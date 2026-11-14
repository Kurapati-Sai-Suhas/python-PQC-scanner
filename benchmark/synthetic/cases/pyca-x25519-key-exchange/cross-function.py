"""Synthetic case pyca-x25519-key-exchange / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x25519


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(peer_public)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    sk = x25519.X25519PrivateKey.generate()
    return _apply(sk, data, sig, ct, peer_public, alg)
