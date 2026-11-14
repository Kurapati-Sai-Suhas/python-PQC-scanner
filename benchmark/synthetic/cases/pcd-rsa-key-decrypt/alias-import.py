"""Synthetic case pcd-rsa-key-decrypt / alias-import (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP as _pkcs1_oaep_mod
from Crypto.PublicKey import RSA as _rsa_mod


def run(data, sig, ct, peer_public, alg):
    signing_key = _rsa_mod.generate(3072)
    r0 = _pkcs1_oaep_mod.new(signing_key).decrypt(ct)
    return (r0,)
