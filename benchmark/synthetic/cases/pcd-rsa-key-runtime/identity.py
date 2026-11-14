"""Synthetic case pcd-rsa-key-runtime / identity (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def run(data, sig, ct, peer_public, alg):
    signing_key = RSA.generate(3072)
    if alg == "A":
        r0 = pkcs1_15.new(signing_key).sign(SHA256.new(data))
    else:
        r0 = PKCS1_OAEP.new(signing_key).decrypt(ct)
    return r0
