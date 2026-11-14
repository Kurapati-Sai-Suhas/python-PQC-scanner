"""Synthetic case pcd-rsa-key-runtime / alias-import (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP as _pkcs1_oaep_mod
from Crypto.PublicKey import RSA as _rsa_mod
from Crypto.Hash import SHA256 as _sha256_mod
from Crypto.Signature import pkcs1_15 as _pkcs1_15_mod


def run(data, sig, ct, peer_public, alg):
    kp = _rsa_mod.generate(3072)
    if alg == "A":
        r0 = _pkcs1_15_mod.new(kp).sign(_sha256_mod.new(data))
    else:
        r0 = _pkcs1_oaep_mod.new(kp).decrypt(ct)
    return r0
