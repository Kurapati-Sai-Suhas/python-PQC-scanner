"""Synthetic case pyca-ed448-key-sign / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448


def _new_key():
    return ed448.Ed448PrivateKey.generate()


def run(data, sig, ct, peer_public, alg):
    signing_key = _new_key()
    r0 = signing_key.sign(data)
    return (r0,)
