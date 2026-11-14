"""Synthetic case pcd-rsa-key-sign-pss / class-method (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss


class Engine:
    def __init__(self):
        self._material = RSA.generate(3072)

    def act(self, data, sig, ct, peer_public, alg):
        r0 = pss.new(self._material).sign(SHA256.new(data))
        return (r0,)
