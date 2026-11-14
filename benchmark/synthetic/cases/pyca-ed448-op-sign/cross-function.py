"""Synthetic case pyca-ed448-op-sign / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448


def _use(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    priv = ed448.Ed448PrivateKey.generate()
    return _use(priv, data, sig, ct, peer_public, alg)
