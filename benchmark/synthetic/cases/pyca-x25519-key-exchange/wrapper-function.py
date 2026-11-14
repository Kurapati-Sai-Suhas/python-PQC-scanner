"""Synthetic case pyca-x25519-key-exchange / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x25519


def _new_key():
    return x25519.X25519PrivateKey.generate()


def run(data, sig, ct, peer_public, alg):
    signing_key = _new_key()
    r0 = signing_key.exchange(peer_public)
    return (r0,)
