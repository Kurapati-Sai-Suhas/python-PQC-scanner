"""Synthetic case pcd-rsa-op-encrypt / identity (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def run(data, sig, ct, peer_public, alg):
    key = RSA.generate(3072)
    r0 = PKCS1_OAEP.new(key.publickey()).encrypt(data)
    return (r0,)
