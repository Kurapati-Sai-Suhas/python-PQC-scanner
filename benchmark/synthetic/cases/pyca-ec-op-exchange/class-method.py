"""Synthetic case pyca-ec-op-exchange / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


class Engine:
    def __init__(self):
        self._material = ec.generate_private_key(ec.SECP256R1())

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self._material.exchange(ec.ECDH(), peer_public)
        return (r0,)
