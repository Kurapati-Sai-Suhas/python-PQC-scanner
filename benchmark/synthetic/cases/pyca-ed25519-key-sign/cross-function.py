"""Synthetic case pyca-ed25519-key-sign / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _process(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    material = ed25519.Ed25519PrivateKey.generate()
    return _process(material, data, sig, ct, peer_public, alg)
