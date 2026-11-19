"""Synthetic case pcd-rsa-op-encrypt / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def _create(k, data, sig, ct, peer_public, alg):
    return PKCS1_OAEP.new(k.publickey()).encrypt(data)


def run(data, sig, ct, peer_public, alg):
    priv = RSA.generate(3072)
    return _create(priv, data, sig, ct, peer_public, alg)
