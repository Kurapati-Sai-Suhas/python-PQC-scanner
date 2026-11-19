"""Synthetic case pcd-rsa-op-encrypt-v15 / cross-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = PKCS1_v1_5.new(k.publickey()).encrypt(data)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    key = RSA.generate(3072)
    return _handle(key, data, sig, ct, peer_public, alg)
