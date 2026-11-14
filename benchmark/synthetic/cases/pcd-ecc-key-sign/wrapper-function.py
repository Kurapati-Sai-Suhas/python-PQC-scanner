"""Synthetic case pcd-ecc-key-sign / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _build():
    return ECC.generate(curve="P-256")


def run(data, sig, ct, peer_public, alg):
    signing_key = _build()
    r0 = DSS.new(signing_key, "fips-186-3").sign(SHA256.new(data))
    return (r0,)
