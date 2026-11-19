"""Synthetic case pcd-rsa-key-export / class-method (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA


class Engine:
    def __init__(self):
        self.key = RSA.generate(3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.key.export_key()
        return (r0,)
