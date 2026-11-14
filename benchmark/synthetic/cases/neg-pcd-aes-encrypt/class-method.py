"""Synthetic case neg-pcd-aes-encrypt / class-method (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import AES


class Backend:
    def act(self, data, sig, ct, peer_public, alg):
        r0 = AES.new(sig[:16], AES.MODE_GCM).encrypt(data)
        return r0
