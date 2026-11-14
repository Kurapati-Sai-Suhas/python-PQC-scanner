"""Synthetic case pcd-ecc-key-signverify / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _process(k, data, sig, ct, peer_public, alg):
    r0 = DSS.new(k, "fips-186-3").sign(SHA256.new(data))
    r1 = DSS.new(k.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
    return (r0, r1)


HANDLERS = {"default": _process, "A": _process}


def run(data, sig, ct, peer_public, alg):
    sk = ECC.generate(curve="P-256")
    return HANDLERS["default"](sk, data, sig, ct, peer_public, alg)
