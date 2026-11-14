"""Synthetic case pcd-rsa-op-encrypt / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = PKCS1_OAEP.new(k.publickey()).encrypt(data)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    kp = RSA.generate(3072)
    return _apply(kp, data, sig, ct, peer_public, alg)
