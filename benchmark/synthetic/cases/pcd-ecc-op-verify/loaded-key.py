"""Synthetic case pcd-ecc-op-verify / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


def run(data, sig, ct, peer_public, alg, pem):
    sk = ECC.import_key(pem)
    r0 = DSS.new(sk.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
    return (r0,)
