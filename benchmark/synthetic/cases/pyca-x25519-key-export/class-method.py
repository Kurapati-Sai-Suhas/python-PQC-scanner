"""Synthetic case pyca-x25519-key-export / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519


class Engine:
    def __init__(self):
        self.key = x25519.X25519PrivateKey.generate()

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        return (r0,)
