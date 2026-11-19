"""Synthetic case neg-pyca-pss-object / alias-import (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes as _hashes_mod
from cryptography.hazmat.primitives.asymmetric import padding as _padding_mod


def run(data, sig, ct, peer_public, alg):
    r0 = _padding_mod.PSS(mgf=_padding_mod.MGF1(_hashes_mod.SHA256()), salt_length=_padding_mod.PSS.MAX_LENGTH)
    return r0
