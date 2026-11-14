"""Synthetic case pcd-rsa-key-signverify / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = pkcs1_15.new(k).sign(SHA256.new(data))
    r1 = pkcs1_15.new(k.publickey()).verify(SHA256.new(data), sig)
    return (r0, r1)


def run(data, sig, ct, peer_public, alg):
    material = RSA.generate(3072)
    return _apply(material, data, sig, ct, peer_public, alg)
