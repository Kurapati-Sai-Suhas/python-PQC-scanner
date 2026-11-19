"""Synthetic case neg-pyca-fernet-encrypt / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.fernet import Fernet


def run(data, sig, ct, peer_public, alg):
    box = Fernet(Fernet.generate_key())
    r0 = box.encrypt(data)
    return r0
