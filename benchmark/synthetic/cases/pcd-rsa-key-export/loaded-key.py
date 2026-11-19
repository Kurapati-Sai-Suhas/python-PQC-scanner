"""Synthetic case pcd-rsa-key-export / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA


def run(data, sig, ct, peer_public, alg, pem):
    priv = RSA.import_key(pem)
    r0 = priv.export_key()
    return (r0,)
