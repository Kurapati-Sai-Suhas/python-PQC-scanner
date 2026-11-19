"""Synthetic case pcd-ecc-key-sign / alias-import (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Signature import DSS as _dss_mod
from Crypto.PublicKey import ECC as _ecc_mod
from Crypto.Hash import SHA256 as _sha256_mod


def run(data, sig, ct, peer_public, alg):
    k = _ecc_mod.generate(curve="P-256")
    r0 = _dss_mod.new(k, "fips-186-3").sign(_sha256_mod.new(data))
    return (r0,)
