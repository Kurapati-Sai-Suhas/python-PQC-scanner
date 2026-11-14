"""Synthetic case neg-pcd-aes-encrypt / identity (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import AES


def run(data, sig, ct, peer_public, alg):
    r0 = AES.new(sig[:16], AES.MODE_GCM).encrypt(data)
    return r0
