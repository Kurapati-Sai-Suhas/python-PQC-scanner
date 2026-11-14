"""Synthetic case pcd-ecc-op-sign / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = DSS.new(k, "fips-186-3").sign(SHA256.new(data))
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    key = ECC.generate(curve="P-256")
    return HANDLERS["default"](key, data, sig, ct, peer_public, alg)
