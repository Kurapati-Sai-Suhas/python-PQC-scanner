"""Synthetic case pcd-rsa-key-signverify / identity (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def run(data, sig, ct, peer_public, alg):
    signing_key = RSA.generate(3072)
    r0 = pkcs1_15.new(signing_key).sign(SHA256.new(data))
    r1 = pkcs1_15.new(signing_key.publickey()).verify(SHA256.new(data), sig)
    return (r0, r1)
