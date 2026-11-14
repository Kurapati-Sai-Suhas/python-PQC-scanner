"""Synthetic case pcd-rsa-key-sign-pss / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss


def _make_key():
    return RSA.generate(3072)


def run(data, sig, ct, peer_public, alg):
    key = _make_key()
    r0 = pss.new(key).sign(SHA256.new(data))
    return (r0,)
