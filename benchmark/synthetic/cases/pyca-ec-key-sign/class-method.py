"""Synthetic case pyca-ec-key-sign / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


class Service:
    def __init__(self):
        self.key = ec.generate_private_key(ec.SECP256R1())

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.key.sign(data, ec.ECDSA(hashes.SHA256()))
        return (r0,)
