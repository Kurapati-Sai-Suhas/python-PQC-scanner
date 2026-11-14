"""Synthetic case pcd-ecc-op-sign / identity (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def run(data, sig, ct, peer_public, alg):
    key = ECC.generate(curve="P-256")
    r0 = DSS.new(key, "fips-186-3").sign(SHA256.new(data))
    return (r0,)
