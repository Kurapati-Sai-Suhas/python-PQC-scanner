"""Synthetic case pyca-rsa-op-encrypt-v15 / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import padding as _padding_mod
from cryptography.hazmat.primitives.asymmetric import rsa as _rsa_mod


def run(data, sig, ct, peer_public, alg):
    material = _rsa_mod.generate_private_key(public_exponent=65537, key_size=3072)
    r0 = material.public_key().encrypt(data, _padding_mod.PKCS1v15())
    return (r0,)
