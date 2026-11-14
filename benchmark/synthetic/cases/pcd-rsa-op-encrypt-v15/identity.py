"""Synthetic case pcd-rsa-op-encrypt-v15 / identity (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def run(data, sig, ct, peer_public, alg):
    signing_key = RSA.generate(3072)
    r0 = PKCS1_v1_5.new(signing_key.publickey()).encrypt(data)
    return (r0,)
