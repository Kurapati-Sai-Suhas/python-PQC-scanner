"""Synthetic case neg-pyca-chacha-decrypt / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


class Engine:
    def act(self, data, sig, ct, peer_public, alg):
        aead = ChaCha20Poly1305(ChaCha20Poly1305.generate_key())
        r0 = aead.decrypt(sig[:12], ct, None)
        return r0
