"""Synthetic case pcd-ecc-key-export / class-method (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import ECC


class Service:
    def __init__(self):
        self.key = ECC.generate(curve="P-256")

    def act(self, data, sig, ct, peer_public, alg):
        r0 = self.key.export_key(format="PEM")
        return (r0,)
