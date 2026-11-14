"""Synthetic case pyca-ec-op-exchange / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


def _make_key(k, data, sig, ct, peer_public, alg):
    return k.exchange(ec.ECDH(), peer_public)


def run(data, sig, ct, peer_public, alg):
    signing_key = ec.generate_private_key(ec.SECP256R1())
    return _make_key(signing_key, data, sig, ct, peer_public, alg)
