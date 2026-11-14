"""Synthetic case pyca-rsa-op-decrypt / alias-import (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes as _hashes_mod
from cryptography.hazmat.primitives.asymmetric import padding as _padding_mod
from cryptography.hazmat.primitives.asymmetric import rsa as _rsa_mod


def run(data, sig, ct, peer_public, alg):
    sk = _rsa_mod.generate_private_key(public_exponent=65537, key_size=3072)
    r0 = sk.decrypt(ct, _padding_mod.OAEP(mgf=_padding_mod.MGF1(algorithm=_hashes_mod.SHA256()), algorithm=_hashes_mod.SHA256(), label=None))
    return (r0,)
