"""Synthetic case pcd-ecc-op-sign / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _build(k, data, sig, ct, peer_public, alg):
    return DSS.new(k, "fips-186-3").sign(SHA256.new(data))


def run(data, sig, ct, peer_public, alg):
    kp = ECC.generate(curve="P-256")
    return _build(kp, data, sig, ct, peer_public, alg)
