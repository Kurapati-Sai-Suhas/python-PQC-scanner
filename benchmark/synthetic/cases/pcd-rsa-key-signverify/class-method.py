"""Synthetic case pcd-rsa-key-signverify / class-method (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


class Service:
    def __init__(self):
        self.key = RSA.generate(3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = pkcs1_15.new(self.key).sign(SHA256.new(data))
        r1 = pkcs1_15.new(self.key.publickey()).verify(SHA256.new(data), sig)
        return (r0, r1)
