"""Synthetic case pcd-ecc-key-signverify / class-method (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


class Engine:
    def __init__(self):
        self.private_key = ECC.generate(curve="P-256")

    def act(self, data, sig, ct, peer_public, alg):
        r0 = DSS.new(self.private_key, "fips-186-3").sign(SHA256.new(data))
        r1 = DSS.new(self.private_key.public_key(), "fips-186-3").verify(SHA256.new(data), sig)
        return (r0, r1)
