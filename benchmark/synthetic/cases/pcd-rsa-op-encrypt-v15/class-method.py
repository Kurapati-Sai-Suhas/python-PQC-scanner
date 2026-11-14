"""Synthetic case pcd-rsa-op-encrypt-v15 / class-method (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


class Session:
    def __init__(self):
        self.key = RSA.generate(3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = PKCS1_v1_5.new(self.key.publickey()).encrypt(data)
        return (r0,)
