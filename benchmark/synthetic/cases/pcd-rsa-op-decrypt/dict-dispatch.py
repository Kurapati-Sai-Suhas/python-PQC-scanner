"""Synthetic case pcd-rsa-op-decrypt / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = PKCS1_OAEP.new(k).decrypt(ct)
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    priv = RSA.generate(3072)
    return HANDLERS["default"](priv, data, sig, ct, peer_public, alg)
