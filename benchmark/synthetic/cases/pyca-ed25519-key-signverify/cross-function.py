"""Synthetic case pyca-ed25519-key-signverify / cross-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _use(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data)
    r1 = k.public_key().verify(sig, data)
    return (r0, r1)


def run(data, sig, ct, peer_public, alg):
    kp = ed25519.Ed25519PrivateKey.generate()
    return _use(kp, data, sig, ct, peer_public, alg)
