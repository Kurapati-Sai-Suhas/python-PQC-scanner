"""Synthetic case pyca-ed25519-op-sign / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


class Client:
    def __init__(self):
        self._key = ed25519.Ed25519PrivateKey.generate()

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self._key.sign(data)
        return (r0,)
