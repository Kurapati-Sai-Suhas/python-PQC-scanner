"""Synthetic case pyca-rsa-op-decrypt / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


class Session:
    def __init__(self):
        self._key = rsa.generate_private_key(public_exponent=65537, key_size=3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self._key.decrypt(ct, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        return (r0,)
