"""Synthetic case pcd-ecc-op-verify / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _make_key(k, data, sig, ct, peer_public, alg):
    return DSS.new(k.public_key(), "fips-186-3").verify(SHA256.new(data), sig)


def run(data, sig, ct, peer_public, alg):
    signing_key = ECC.generate(curve="P-256")
    return _make_key(signing_key, data, sig, ct, peer_public, alg)
