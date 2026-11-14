"""Synthetic case neg-pyca-fernet-encrypt / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.fernet import Fernet


def _use(data, sig, ct, peer_public, alg):
    box = Fernet(Fernet.generate_key())
    r0 = box.encrypt(data)
    return r0


def run(data, sig, ct, peer_public, alg):
    return _use(data, sig, ct, peer_public, alg)
