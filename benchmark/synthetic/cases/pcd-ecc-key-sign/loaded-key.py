"""Synthetic case pcd-ecc-key-sign / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def run(data, sig, ct, peer_public, alg, pem):
    priv = ECC.import_key(pem)
    r0 = DSS.new(priv, "fips-186-3").sign(SHA256.new(data))
    return (r0,)
