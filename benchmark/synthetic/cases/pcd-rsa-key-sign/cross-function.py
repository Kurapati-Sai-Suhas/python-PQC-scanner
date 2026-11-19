"""Synthetic case pcd-rsa-key-sign / cross-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = pkcs1_15.new(k).sign(SHA256.new(data))
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    k = RSA.generate(3072)
    return _handle(k, data, sig, ct, peer_public, alg)
