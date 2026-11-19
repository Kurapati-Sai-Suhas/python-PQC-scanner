"""Synthetic case neg-pyca-fernet-encrypt / alias-import (pqscan synthetic generator 1.1). Never executed."""
from cryptography.fernet import Fernet as _fernet_mod


def run(data, sig, ct, peer_public, alg):
    box = _fernet_mod(_fernet_mod.generate_key())
    r0 = box.encrypt(data)
    return r0
