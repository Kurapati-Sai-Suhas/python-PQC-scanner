"""Synthetic case pcd-ecc-key-export / identity (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import ECC


def run(data, sig, ct, peer_public, alg):
    kp = ECC.generate(curve="P-256")
    r0 = kp.export_key(format="PEM")
    return (r0,)
