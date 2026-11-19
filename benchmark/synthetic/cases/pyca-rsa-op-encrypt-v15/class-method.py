"""Synthetic case pyca-rsa-op-encrypt-v15 / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


class Service:
    def __init__(self):
        self._key = rsa.generate_private_key(public_exponent=65537, key_size=3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self._key.public_key().encrypt(data, padding.PKCS1v15())
        return (r0,)
