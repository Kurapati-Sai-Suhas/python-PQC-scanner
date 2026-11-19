"""Synthetic case pcd-rsa-key-decrypt / class-method (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class Session:
    def __init__(self):
        self.key = RSA.generate(3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = PKCS1_OAEP.new(self.key).decrypt(ct)
        return (r0,)
