"""Synthetic case pcd-rsa-op-sign / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = pkcs1_15.new(k).sign(SHA256.new(data))
    return (r0,)


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    sk = RSA.generate(3072)
    return HANDLERS["default"](sk, data, sig, ct, peer_public, alg)
