"""Synthetic case pcd-rsa-key-runtime / cross-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def _process(k, data, sig, ct, peer_public, alg):
    if alg == "A":
        r0 = pkcs1_15.new(k).sign(SHA256.new(data))
    else:
        r0 = PKCS1_OAEP.new(k).decrypt(ct)
    return r0


def run(data, sig, ct, peer_public, alg):
    material = RSA.generate(3072)
    return _process(material, data, sig, ct, peer_public, alg)
