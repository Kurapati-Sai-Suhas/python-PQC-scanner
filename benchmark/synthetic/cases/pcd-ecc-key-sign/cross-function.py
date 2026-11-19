"""Synthetic case pcd-ecc-key-sign / cross-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _process(k, data, sig, ct, peer_public, alg):
    r0 = DSS.new(k, "fips-186-3").sign(SHA256.new(data))
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    kp = ECC.generate(curve="P-256")
    return _process(kp, data, sig, ct, peer_public, alg)
