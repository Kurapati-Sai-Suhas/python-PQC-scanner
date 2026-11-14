"""Synthetic case pcd-rsa-key-export / alias-import (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA as _rsa_mod


def run(data, sig, ct, peer_public, alg):
    material = _rsa_mod.generate(3072)
    r0 = material.export_key()
    return (r0,)
