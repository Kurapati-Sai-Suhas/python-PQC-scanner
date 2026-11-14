"""Synthetic case pyca-rsa-op-sign-v15 / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


class Session:
    def __init__(self):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.key.sign(data, padding.PKCS1v15(), hashes.SHA256())
        return (r0,)
