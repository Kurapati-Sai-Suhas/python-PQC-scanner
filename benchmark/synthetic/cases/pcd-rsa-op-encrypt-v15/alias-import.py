"""Synthetic case pcd-rsa-op-encrypt-v15 / alias-import (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_v1_5 as _pkcs1_v1_5_mod
from Crypto.PublicKey import RSA as _rsa_mod


def run(data, sig, ct, peer_public, alg):
    kp = _rsa_mod.generate(3072)
    r0 = _pkcs1_v1_5_mod.new(kp.publickey()).encrypt(data)
    return (r0,)
