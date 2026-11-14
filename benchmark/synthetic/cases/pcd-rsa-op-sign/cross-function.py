"""Synthetic case pcd-rsa-op-sign / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = pkcs1_15.new(k).sign(SHA256.new(data))
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    kp = RSA.generate(3072)
    return _apply(kp, data, sig, ct, peer_public, alg)
