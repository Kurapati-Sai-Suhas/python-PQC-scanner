"""Synthetic case pyca-ed25519-key-signverify / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


class Session:
    def __init__(self):
        self._material = ed25519.Ed25519PrivateKey.generate()

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self._material.sign(data)
        r1 = self._material.public_key().verify(sig, data)
        return (r0, r1)
