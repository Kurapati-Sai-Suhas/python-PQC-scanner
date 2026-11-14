"""Synthetic case pcd-rsa-op-sign-pss / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss


def _use(k, data, sig, ct, peer_public, alg):
    r0 = pss.new(k).sign(SHA256.new(data))
    return (r0,)


HANDLERS = {"default": _use, "A": _use}


def run(data, sig, ct, peer_public, alg):
    k = RSA.generate(3072)
    return HANDLERS["default"](k, data, sig, ct, peer_public, alg)
