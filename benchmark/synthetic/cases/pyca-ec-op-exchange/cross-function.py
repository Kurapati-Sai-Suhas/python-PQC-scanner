"""Synthetic case pyca-ec-op-exchange / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(ec.ECDH(), peer_public)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    priv = ec.generate_private_key(ec.SECP256R1())
    return _apply(priv, data, sig, ct, peer_public, alg)
