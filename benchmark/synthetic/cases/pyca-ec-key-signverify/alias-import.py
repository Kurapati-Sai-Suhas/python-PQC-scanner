"""Synthetic case pyca-ec-key-signverify / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec as _ec_mod
from cryptography.hazmat.primitives import hashes as _hashes_mod


def run(data, sig, ct, peer_public, alg):
    sk = _ec_mod.generate_private_key(_ec_mod.SECP256R1())
    r0 = sk.sign(data, _ec_mod.ECDSA(_hashes_mod.SHA256()))
    r1 = sk.public_key().verify(sig, data, _ec_mod.ECDSA(_hashes_mod.SHA256()))
    return (r0, r1)
