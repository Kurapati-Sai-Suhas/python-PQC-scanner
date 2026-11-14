"""Synthetic case neg-pyca-aesgcm-encrypt / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM as _aesgcm_mod


def run(data, sig, ct, peer_public, alg):
    aead = _aesgcm_mod(_aesgcm_mod.generate_key(bit_length=256))
    r0 = aead.encrypt(sig[:12], data, None)
    return r0
