"""Synthetic case neg-pyca-ecdsa-object / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec as _ec_mod
from cryptography.hazmat.primitives import hashes as _hashes_mod


def run(data, sig, ct, peer_public, alg):
    r0 = _ec_mod.ECDSA(_hashes_mod.SHA256())
    return r0
