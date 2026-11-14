"""Synthetic case neg-pyca-aesgcm-encrypt / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class Session:
    def act(self, data, sig, ct, peer_public, alg):
        aead = AESGCM(AESGCM.generate_key(bit_length=256))
        r0 = aead.encrypt(sig[:12], data, None)
        return r0
