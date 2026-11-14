"""Synthetic case pyca-ec-key-export / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


class Session:
    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256R1())

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.private_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        return (r0,)
