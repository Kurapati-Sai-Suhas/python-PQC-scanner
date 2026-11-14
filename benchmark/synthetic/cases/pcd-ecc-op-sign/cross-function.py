"""Synthetic case pcd-ecc-op-sign / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _process(k, data, sig, ct, peer_public, alg):
    r0 = DSS.new(k, "fips-186-3").sign(SHA256.new(data))
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    sk = ECC.generate(curve="P-256")
    return _process(sk, data, sig, ct, peer_public, alg)
