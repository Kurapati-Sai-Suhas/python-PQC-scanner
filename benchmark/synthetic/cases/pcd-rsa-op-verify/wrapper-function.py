"""Synthetic case pcd-rsa-op-verify / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _make_key(k, data, sig, ct, peer_public, alg):
    return pkcs1_15.new(k.publickey()).verify(SHA256.new(data), sig)


def run(data, sig, ct, peer_public, alg):
    kp = RSA.generate(3072)
    return _make_key(kp, data, sig, ct, peer_public, alg)
