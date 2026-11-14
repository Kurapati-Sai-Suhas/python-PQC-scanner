"""Synthetic case pyca-ec-op-verify / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


class Session:
    def __init__(self):
        self._material = ec.generate_private_key(ec.SECP256R1())

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self._material.public_key().verify(sig, data, ec.ECDSA(hashes.SHA256()))
        return (r0,)
