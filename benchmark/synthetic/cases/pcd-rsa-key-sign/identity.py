"""Synthetic case pcd-rsa-key-sign / identity (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def run(data, sig, ct, peer_public, alg):
    sk = RSA.generate(3072)
    r0 = pkcs1_15.new(sk).sign(SHA256.new(data))
    return (r0,)
