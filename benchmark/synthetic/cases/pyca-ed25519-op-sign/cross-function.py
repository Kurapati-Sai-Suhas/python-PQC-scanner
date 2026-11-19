"""Synthetic case pyca-ed25519-op-sign / cross-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    priv = ed25519.Ed25519PrivateKey.generate()
    return _apply(priv, data, sig, ct, peer_public, alg)
