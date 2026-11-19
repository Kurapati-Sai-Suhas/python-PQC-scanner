"""Synthetic case pyca-x448-op-exchange / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448


class Service:
    def __init__(self):
        self.private_key = x448.X448PrivateKey.generate()

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.private_key.exchange(peer_public)
        return (r0,)
