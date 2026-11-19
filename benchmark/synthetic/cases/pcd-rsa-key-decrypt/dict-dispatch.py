"""Synthetic case pcd-rsa-key-decrypt / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def _process(k, data, sig, ct, peer_public, alg):
    r0 = PKCS1_OAEP.new(k).decrypt(ct)
    return (r0,)


HANDLERS = {"default": _process, "A": _process}


def run(data, sig, ct, peer_public, alg):
    kp = RSA.generate(3072)
    return HANDLERS["default"](kp, data, sig, ct, peer_public, alg)
