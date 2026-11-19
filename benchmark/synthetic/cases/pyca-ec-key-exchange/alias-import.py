"""Synthetic case pyca-ec-key-exchange / alias-import (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec as _ec_mod


def run(data, sig, ct, peer_public, alg):
    material = _ec_mod.generate_private_key(_ec_mod.SECP256R1())
    r0 = material.exchange(_ec_mod.ECDH(), peer_public)
    return (r0,)
