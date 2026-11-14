"""Synthetic case pcd-rsa-op-encrypt-v15 / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = PKCS1_v1_5.new(k.publickey()).encrypt(data)
    return (r0,)


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    priv = RSA.generate(3072)
    return HANDLERS["default"](priv, data, sig, ct, peer_public, alg)
