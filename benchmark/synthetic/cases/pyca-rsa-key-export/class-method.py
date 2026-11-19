"""Synthetic case pyca-rsa-key-export / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


class Service:
    def __init__(self):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        return (r0,)
