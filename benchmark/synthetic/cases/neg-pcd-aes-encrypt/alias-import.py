"""Synthetic case neg-pcd-aes-encrypt / alias-import (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import AES as _aes_mod


def run(data, sig, ct, peer_public, alg):
    r0 = _aes_mod.new(sig[:16], _aes_mod.MODE_GCM).encrypt(data)
    return r0
