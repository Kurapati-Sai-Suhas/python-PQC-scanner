"""Synthetic case pcd-rsa-op-sign-pss / class-method (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss


class Session:
    def __init__(self):
        self.private_key = RSA.generate(3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = pss.new(self.private_key).sign(SHA256.new(data))
        return (r0,)
