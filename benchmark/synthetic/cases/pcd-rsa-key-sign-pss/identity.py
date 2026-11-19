"""Synthetic case pcd-rsa-key-sign-pss / identity (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss


def run(data, sig, ct, peer_public, alg):
    priv = RSA.generate(3072)
    r0 = pss.new(priv).sign(SHA256.new(data))
    return (r0,)
