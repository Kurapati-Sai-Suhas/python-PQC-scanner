"""Synthetic case pyca-ed25519-key-export / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


class Session:
    def __init__(self):
        self.private_key = ed25519.Ed25519PrivateKey.generate()

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.private_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        return (r0,)
