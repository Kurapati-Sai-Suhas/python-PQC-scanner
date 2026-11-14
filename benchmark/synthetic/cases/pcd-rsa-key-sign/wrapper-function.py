"""Synthetic case pcd-rsa-key-sign / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _build():
    return RSA.generate(3072)


def run(data, sig, ct, peer_public, alg):
    k = _build()
    r0 = pkcs1_15.new(k).sign(SHA256.new(data))
    return (r0,)
