"""Synthetic case pyca-ed25519-key-sign / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


class Session:
    def __init__(self):
        self.private_key = ed25519.Ed25519PrivateKey.generate()

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.private_key.sign(data)
        return (r0,)
