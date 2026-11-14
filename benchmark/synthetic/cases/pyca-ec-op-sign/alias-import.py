"""Synthetic case pyca-ec-op-sign / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec as _ec_mod
from cryptography.hazmat.primitives import hashes as _hashes_mod


def run(data, sig, ct, peer_public, alg):
    signing_key = _ec_mod.generate_private_key(_ec_mod.SECP256R1())
    r0 = signing_key.sign(data, _ec_mod.ECDSA(_hashes_mod.SHA256()))
    return (r0,)
