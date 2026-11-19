"""Synthetic case pyca-ed448-op-sign / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448


def _new_key(k, data, sig, ct, peer_public, alg):
    return k.sign(data)


def run(data, sig, ct, peer_public, alg):
    material = ed448.Ed448PrivateKey.generate()
    return _new_key(material, data, sig, ct, peer_public, alg)
