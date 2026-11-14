"""Synthetic case neg-pyca-chacha-decrypt / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


def run(data, sig, ct, peer_public, alg):
    aead = ChaCha20Poly1305(ChaCha20Poly1305.generate_key())
    r0 = aead.decrypt(sig[:12], ct, None)
    return r0
