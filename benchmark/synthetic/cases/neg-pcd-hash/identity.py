"""Synthetic case neg-pcd-hash / identity (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Hash import SHA256


def run(data, sig, ct, peer_public, alg):
    r0 = SHA256.new(data).hexdigest()
    return r0
