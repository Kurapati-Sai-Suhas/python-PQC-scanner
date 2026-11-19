"""Synthetic case pyca-ed448-key-sign / cross-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    material = ed448.Ed448PrivateKey.generate()
    return _handle(material, data, sig, ct, peer_public, alg)
