"""Synthetic case pcd-rsa-op-decrypt / identity (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def run(data, sig, ct, peer_public, alg):
    material = RSA.generate(3072)
    r0 = PKCS1_OAEP.new(material).decrypt(ct)
    return (r0,)
