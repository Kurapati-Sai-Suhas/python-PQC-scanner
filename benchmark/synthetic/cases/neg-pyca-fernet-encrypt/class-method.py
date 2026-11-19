"""Synthetic case neg-pyca-fernet-encrypt / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.fernet import Fernet


class Service:
    def act(self, data, sig, ct, peer_public, alg):
        box = Fernet(Fernet.generate_key())
        r0 = box.encrypt(data)
        return r0
