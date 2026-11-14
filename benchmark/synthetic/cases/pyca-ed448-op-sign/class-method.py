"""Synthetic case pyca-ed448-op-sign / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448


class Engine:
    def __init__(self):
        self.private_key = ed448.Ed448PrivateKey.generate()

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.private_key.sign(data)
        return (r0,)
