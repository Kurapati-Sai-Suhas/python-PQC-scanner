"""Synthetic case pyca-rsa-key-runtime / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


class Session:
    def __init__(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)

    def act(self, data, sig, ct, peer_public, alg):
        if alg == "A":
            r0 = self.private_key.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        else:
            r0 = self.private_key.decrypt(ct, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        return r0
