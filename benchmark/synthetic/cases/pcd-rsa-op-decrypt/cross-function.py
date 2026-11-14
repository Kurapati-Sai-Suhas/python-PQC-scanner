"""Synthetic case pcd-rsa-op-decrypt / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = PKCS1_OAEP.new(k).decrypt(ct)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    signing_key = RSA.generate(3072)
    return _handle(signing_key, data, sig, ct, peer_public, alg)
