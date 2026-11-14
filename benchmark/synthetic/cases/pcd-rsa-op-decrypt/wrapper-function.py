"""Synthetic case pcd-rsa-op-decrypt / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def _build(k, data, sig, ct, peer_public, alg):
    return PKCS1_OAEP.new(k).decrypt(ct)


def run(data, sig, ct, peer_public, alg):
    sk = RSA.generate(3072)
    return _build(sk, data, sig, ct, peer_public, alg)
