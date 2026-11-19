"""Synthetic case pyca-ec-key-exchange / cross-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(ec.ECDH(), peer_public)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    k = ec.generate_private_key(ec.SECP256R1())
    return _handle(k, data, sig, ct, peer_public, alg)
