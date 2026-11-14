"""Synthetic case pcd-rsa-op-encrypt-v15 / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def _build(k, data, sig, ct, peer_public, alg):
    return PKCS1_v1_5.new(k.publickey()).encrypt(data)


def run(data, sig, ct, peer_public, alg):
    k = RSA.generate(3072)
    return _build(k, data, sig, ct, peer_public, alg)
