"""Synthetic case pcd-ecc-key-export / cross-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import ECC


def _use(k, data, sig, ct, peer_public, alg):
    r0 = k.export_key(format="PEM")
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    k = ECC.generate(curve="P-256")
    return _use(k, data, sig, ct, peer_public, alg)
