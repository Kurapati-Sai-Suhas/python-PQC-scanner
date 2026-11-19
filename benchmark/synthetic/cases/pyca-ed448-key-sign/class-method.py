"""Synthetic case pyca-ed448-key-sign / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448


class Backend:
    def __init__(self):
        self._material = ed448.Ed448PrivateKey.generate()

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self._material.sign(data)
        return (r0,)
