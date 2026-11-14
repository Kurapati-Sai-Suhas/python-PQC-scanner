"""Synthetic case neg-pyca-aesgcm-encrypt / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _apply(data, sig, ct, peer_public, alg):
    aead = AESGCM(AESGCM.generate_key(bit_length=256))
    r0 = aead.encrypt(sig[:12], data, None)
    return r0


def run(data, sig, ct, peer_public, alg):
    return _apply(data, sig, ct, peer_public, alg)
