"""Synthetic case pcd-rsa-op-sign / class-method (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


class Client:
    def __init__(self):
        self.key = RSA.generate(3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = pkcs1_15.new(self.key).sign(SHA256.new(data))
        return (r0,)
