"""Synthetic case pcd-ecc-key-signverify / identity (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def run(data, sig, ct, peer_public, alg):
    sk = ECC.generate(curve="P-256")
    r0 = DSS.new(sk, "fips-186-3").sign(SHA256.new(data))
    r1 = DSS.new(sk.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
    return (r0, r1)
