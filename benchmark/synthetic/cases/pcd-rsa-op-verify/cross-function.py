"""Synthetic case pcd-rsa-op-verify / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = pkcs1_15.new(k.publickey()).verify(SHA256.new(data), sig)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    key = RSA.generate(3072)
    return _apply(key, data, sig, ct, peer_public, alg)
