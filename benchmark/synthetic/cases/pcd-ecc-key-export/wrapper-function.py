"""Synthetic case pcd-ecc-key-export / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import ECC


def _new_key():
    return ECC.generate(curve="P-256")


def run(data, sig, ct, peer_public, alg):
    material = _new_key()
    r0 = material.export_key(format="PEM")
    return (r0,)
