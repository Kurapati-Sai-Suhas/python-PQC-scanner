"""Synthetic case pcd-rsa-key-runtime / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _make_key():
    return RSA.generate(3072)


def run(data, sig, ct, peer_public, alg):
    key = _make_key()
    if alg == "A":
        r0 = pkcs1_15.new(key).sign(SHA256.new(data))
    else:
        r0 = PKCS1_OAEP.new(key).decrypt(ct)
    return r0
