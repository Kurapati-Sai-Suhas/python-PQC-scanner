"""Synthetic case pyca-ed25519-op-verify / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _build(k, data, sig, ct, peer_public, alg):
    return k.public_key().verify(sig, data)


def run(data, sig, ct, peer_public, alg):
    kp = ed25519.Ed25519PrivateKey.generate()
    return _build(kp, data, sig, ct, peer_public, alg)
