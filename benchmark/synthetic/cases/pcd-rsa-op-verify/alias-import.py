"""Synthetic case pcd-rsa-op-verify / alias-import (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA as _rsa_mod
from Crypto.Hash import SHA256 as _sha256_mod
from Crypto.Signature import pkcs1_15 as _pkcs1_15_mod


def run(data, sig, ct, peer_public, alg):
    key = _rsa_mod.generate(3072)
    r0 = _pkcs1_15_mod.new(key.publickey()).verify(_sha256_mod.new(data), sig)
    return (r0,)
