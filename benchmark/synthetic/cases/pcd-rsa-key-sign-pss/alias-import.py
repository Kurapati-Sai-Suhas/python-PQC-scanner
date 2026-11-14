"""Synthetic case pcd-rsa-key-sign-pss / alias-import (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA as _rsa_mod
from Crypto.Hash import SHA256 as _sha256_mod
from Crypto.Signature import pss as _pss_mod


def run(data, sig, ct, peer_public, alg):
    k = _rsa_mod.generate(3072)
    r0 = _pss_mod.new(k).sign(_sha256_mod.new(data))
    return (r0,)
