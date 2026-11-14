"""Synthetic case pcd-rsa-op-sign / identity (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def run(data, sig, ct, peer_public, alg):
    kp = RSA.generate(3072)
    r0 = pkcs1_15.new(kp).sign(SHA256.new(data))
    return (r0,)
