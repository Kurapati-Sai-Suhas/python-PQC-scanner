"""Synthetic case pyca-x25519-key-exchange / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x25519


class Backend:
    def __init__(self):
        self.key = x25519.X25519PrivateKey.generate()

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.key.exchange(peer_public)
        return (r0,)
