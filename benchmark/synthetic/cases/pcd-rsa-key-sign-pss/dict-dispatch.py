"""Synthetic case pcd-rsa-key-sign-pss / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = pss.new(k).sign(SHA256.new(data))
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    signing_key = RSA.generate(3072)
    return HANDLERS["default"](signing_key, data, sig, ct, peer_public, alg)
