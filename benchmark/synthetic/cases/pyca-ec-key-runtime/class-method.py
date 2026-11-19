"""Synthetic case pyca-ec-key-runtime / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


class Client:
    def __init__(self):
        self.key = ec.generate_private_key(ec.SECP256R1())

    def act(self, data, sig, ct, peer_public, alg):
        if alg == "A":
            r0 = self.key.sign(data, ec.ECDSA(hashes.SHA256()))
        else:
            r0 = self.key.exchange(ec.ECDH(), peer_public)
        return r0
