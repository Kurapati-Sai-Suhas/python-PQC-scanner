"""Synthetic case pcd-ecc-key-signverify / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def run(data, sig, ct, peer_public, alg, pem):
    kp = ECC.import_key(pem)
    r0 = DSS.new(kp, "fips-186-3").sign(SHA256.new(data))
    r1 = DSS.new(kp.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
    return (r0, r1)
