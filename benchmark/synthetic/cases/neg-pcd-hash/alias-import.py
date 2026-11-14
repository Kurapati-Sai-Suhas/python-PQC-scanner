"""Synthetic case neg-pcd-hash / alias-import (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Hash import SHA256 as _sha256_mod


def run(data, sig, ct, peer_public, alg):
    r0 = _sha256_mod.new(data).hexdigest()
    return r0
