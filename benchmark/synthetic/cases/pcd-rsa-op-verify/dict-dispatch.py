"""Synthetic case pcd-rsa-op-verify / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _use(k, data, sig, ct, peer_public, alg):
    r0 = pkcs1_15.new(k.publickey()).verify(SHA256.new(data), sig)
    return (r0,)


HANDLERS = {"default": _use, "A": _use}


def run(data, sig, ct, peer_public, alg):
    signing_key = RSA.generate(3072)
    return HANDLERS["default"](signing_key, data, sig, ct, peer_public, alg)
