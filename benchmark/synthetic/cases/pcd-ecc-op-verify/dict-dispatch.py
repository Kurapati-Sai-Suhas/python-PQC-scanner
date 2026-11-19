"""Synthetic case pcd-ecc-op-verify / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = DSS.new(k.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
    return (r0,)


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    signing_key = ECC.generate(curve="P-256")
    return HANDLERS["default"](signing_key, data, sig, ct, peer_public, alg)
