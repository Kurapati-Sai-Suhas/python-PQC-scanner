"""Synthetic case pcd-ecc-key-sign / class-method (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256


class Engine:
    def __init__(self):
        self._material = ECC.generate(curve="P-256")

    def act(self, data, sig, ct, peer_public, alg):
        r0 = DSS.new(self._material, "fips-186-3").sign(SHA256.new(data))
        return (r0,)
