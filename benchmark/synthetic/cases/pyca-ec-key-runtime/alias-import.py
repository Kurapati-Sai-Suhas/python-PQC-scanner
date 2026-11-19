"""Synthetic case pyca-ec-key-runtime / alias-import (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec as _ec_mod
from cryptography.hazmat.primitives import hashes as _hashes_mod


def run(data, sig, ct, peer_public, alg):
    priv = _ec_mod.generate_private_key(_ec_mod.SECP256R1())
    if alg == "A":
        r0 = priv.sign(data, _ec_mod.ECDSA(_hashes_mod.SHA256()))
    else:
        r0 = priv.exchange(_ec_mod.ECDH(), peer_public)
    return r0
