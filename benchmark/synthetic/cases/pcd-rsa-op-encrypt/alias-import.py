"""Synthetic case pcd-rsa-op-encrypt / alias-import (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP as _pkcs1_oaep_mod
from Crypto.PublicKey import RSA as _rsa_mod


def run(data, sig, ct, peer_public, alg):
    k = _rsa_mod.generate(3072)
    r0 = _pkcs1_oaep_mod.new(k.publickey()).encrypt(data)
    return (r0,)
