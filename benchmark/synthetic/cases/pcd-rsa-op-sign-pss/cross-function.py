"""Synthetic case pcd-rsa-op-sign-pss / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = pss.new(k).sign(SHA256.new(data))
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    material = RSA.generate(3072)
    return _handle(material, data, sig, ct, peer_public, alg)
