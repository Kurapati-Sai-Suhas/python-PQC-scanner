"""Synthetic case neg-pyca-chacha-decrypt / alias-import (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305 as _chacha20poly1305_mod


def run(data, sig, ct, peer_public, alg):
    aead = _chacha20poly1305_mod(_chacha20poly1305_mod.generate_key())
    r0 = aead.decrypt(sig[:12], ct, None)
    return r0
