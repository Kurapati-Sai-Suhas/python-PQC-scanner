"""Synthetic case pcd-ecc-op-verify / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _process(k, data, sig, ct, peer_public, alg):
    r0 = DSS.new(k.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    kp = ECC.generate(curve="P-256")
    return _process(kp, data, sig, ct, peer_public, alg)
