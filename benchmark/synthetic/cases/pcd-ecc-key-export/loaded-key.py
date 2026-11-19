"""Synthetic case pcd-ecc-key-export / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import ECC


def run(data, sig, ct, peer_public, alg, pem):
    priv = ECC.import_key(pem)
    r0 = priv.export_key(format="PEM")
    return (r0,)
