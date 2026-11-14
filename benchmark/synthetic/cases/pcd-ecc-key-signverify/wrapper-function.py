"""Synthetic case pcd-ecc-key-signverify / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _make_key():
    return ECC.generate(curve="P-256")


def run(data, sig, ct, peer_public, alg):
    k = _make_key()
    r0 = DSS.new(k, "fips-186-3").sign(SHA256.new(data))
    r1 = DSS.new(k.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
    return (r0, r1)
