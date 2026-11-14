"""Synthetic case pyca-rsa-key-sign / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _new_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=3072)


def run(data, sig, ct, peer_public, alg):
    priv = _new_key()
    r0 = priv.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    return (r0,)
