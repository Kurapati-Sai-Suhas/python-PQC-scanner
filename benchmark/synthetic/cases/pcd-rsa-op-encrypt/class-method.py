"""Synthetic case pcd-rsa-op-encrypt / class-method (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class Client:
    def __init__(self):
        self.private_key = RSA.generate(3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = PKCS1_OAEP.new(self.private_key.publickey()).encrypt(data)
        return (r0,)
