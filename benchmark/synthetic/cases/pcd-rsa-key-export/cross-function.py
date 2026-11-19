"""Synthetic case pcd-rsa-key-export / cross-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.export_key()
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    key = RSA.generate(3072)
    return _handle(key, data, sig, ct, peer_public, alg)
