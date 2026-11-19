"""Synthetic case pyca-rsa-op-verify / alias-import (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes as _hashes_mod
from cryptography.hazmat.primitives.asymmetric import padding as _padding_mod
from cryptography.hazmat.primitives.asymmetric import rsa as _rsa_mod


def run(data, sig, ct, peer_public, alg):
    key = _rsa_mod.generate_private_key(public_exponent=65537, key_size=3072)
    r0 = key.public_key().verify(sig, data, _padding_mod.PSS(mgf=_padding_mod.MGF1(_hashes_mod.SHA256()), salt_length=_padding_mod.PSS.MAX_LENGTH), _hashes_mod.SHA256())
    return (r0,)
