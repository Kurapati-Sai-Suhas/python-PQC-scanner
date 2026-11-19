"""Synthetic case pcd-rsa-key-runtime / class-method (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


class Session:
    def __init__(self):
        self.key = RSA.generate(3072)

    def act(self, data, sig, ct, peer_public, alg):
        if alg == "A":
            r0 = pkcs1_15.new(self.key).sign(SHA256.new(data))
        else:
            r0 = PKCS1_OAEP.new(self.key).decrypt(ct)
        return r0
