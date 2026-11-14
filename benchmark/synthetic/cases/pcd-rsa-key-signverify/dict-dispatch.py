"""Synthetic case pcd-rsa-key-signverify / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _process(k, data, sig, ct, peer_public, alg):
    r0 = pkcs1_15.new(k).sign(SHA256.new(data))
    r1 = pkcs1_15.new(k.publickey()).verify(SHA256.new(data), sig)
    return (r0, r1)


HANDLERS = {"default": _process, "A": _process}


def run(data, sig, ct, peer_public, alg):
    signing_key = RSA.generate(3072)
    return HANDLERS["default"](signing_key, data, sig, ct, peer_public, alg)
