"""Synthetic case pyca-rsa-key-decrypt / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _build():
    return rsa.generate_private_key(public_exponent=65537, key_size=3072)


def run(data, sig, ct, peer_public, alg):
    priv = _build()
    r0 = priv.decrypt(ct, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return (r0,)
