"""Synthetic case pcd-rsa-key-export / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA


def _make_key():
    return RSA.generate(3072)


def run(data, sig, ct, peer_public, alg):
    priv = _make_key()
    r0 = priv.export_key()
    return (r0,)
