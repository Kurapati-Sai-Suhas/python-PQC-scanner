"""Synthetic case pyca-ec-key-exchange / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


def _make_key():
    return ec.generate_private_key(ec.SECP256R1())


def run(data, sig, ct, peer_public, alg):
    key = _make_key()
    r0 = key.exchange(ec.ECDH(), peer_public)
    return (r0,)
