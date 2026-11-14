"""Synthetic case pyca-ec-key-exchange / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


class Session:
    def __init__(self):
        self._key = ec.generate_private_key(ec.SECP256R1())

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self._key.exchange(ec.ECDH(), peer_public)
        return (r0,)
