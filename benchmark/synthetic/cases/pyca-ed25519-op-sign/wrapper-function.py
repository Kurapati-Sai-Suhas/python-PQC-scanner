"""Synthetic case pyca-ed25519-op-sign / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _make_key(k, data, sig, ct, peer_public, alg):
    return k.sign(data)


def run(data, sig, ct, peer_public, alg):
    material = ed25519.Ed25519PrivateKey.generate()
    return _make_key(material, data, sig, ct, peer_public, alg)
