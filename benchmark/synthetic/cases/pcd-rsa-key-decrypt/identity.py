"""Synthetic case pcd-rsa-key-decrypt / identity (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def run(data, sig, ct, peer_public, alg):
    sk = RSA.generate(3072)
    r0 = PKCS1_OAEP.new(sk).decrypt(ct)
    return (r0,)
