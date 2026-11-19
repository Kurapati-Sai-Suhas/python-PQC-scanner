"""Synthetic case pcd-ecc-key-sign / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = DSS.new(k, "fips-186-3").sign(SHA256.new(data))
    return (r0,)


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    priv = ECC.generate(curve="P-256")
    return HANDLERS["default"](priv, data, sig, ct, peer_public, alg)
