"""Synthetic case pcd-ecc-key-export / alias-import (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import ECC as _ecc_mod


def run(data, sig, ct, peer_public, alg):
    material = _ecc_mod.generate(curve="P-256")
    r0 = material.export_key(format="PEM")
    return (r0,)
