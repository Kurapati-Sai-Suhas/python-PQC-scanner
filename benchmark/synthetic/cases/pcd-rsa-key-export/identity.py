"""Synthetic case pcd-rsa-key-export / identity (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA


def run(data, sig, ct, peer_public, alg):
    priv = RSA.generate(3072)
    r0 = priv.export_key()
    return (r0,)
