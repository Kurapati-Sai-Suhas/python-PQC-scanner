"""Synthetic case pcd-ecc-op-verify / identity (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def run(data, sig, ct, peer_public, alg):
    material = ECC.generate(curve="P-256")
    r0 = DSS.new(material.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
    return (r0,)
