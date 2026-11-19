"""Synthetic case pcd-rsa-op-sign-pss / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss


def _create(k, data, sig, ct, peer_public, alg):
    return pss.new(k).sign(SHA256.new(data))


def run(data, sig, ct, peer_public, alg):
    sk = RSA.generate(3072)
    return _create(sk, data, sig, ct, peer_public, alg)
