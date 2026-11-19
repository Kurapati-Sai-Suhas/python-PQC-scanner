"""Synthetic case pcd-rsa-key-signverify / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _build():
    return RSA.generate(3072)


def run(data, sig, ct, peer_public, alg):
    signing_key = _build()
    r0 = pkcs1_15.new(signing_key).sign(SHA256.new(data))
    r1 = pkcs1_15.new(signing_key.publickey()).verify(SHA256.new(data), sig)
    return (r0, r1)
