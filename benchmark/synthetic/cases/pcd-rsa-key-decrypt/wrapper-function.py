"""Synthetic case pcd-rsa-key-decrypt / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def _new_key():
    return RSA.generate(3072)


def run(data, sig, ct, peer_public, alg):
    k = _new_key()
    r0 = PKCS1_OAEP.new(k).decrypt(ct)
    return (r0,)
