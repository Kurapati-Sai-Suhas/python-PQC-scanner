"""Synthetic case pcd-ecc-key-signverify / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def _use(k, data, sig, ct, peer_public, alg):
    r0 = DSS.new(k, "fips-186-3").sign(SHA256.new(data))
    r1 = DSS.new(k.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
    return (r0, r1)


def run(data, sig, ct, peer_public, alg):
    material = ECC.generate(curve="P-256")
    return _use(material, data, sig, ct, peer_public, alg)
