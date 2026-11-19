"""Synthetic case pyca-rsa-op-verify / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _make_key(k, data, sig, ct, peer_public, alg):
    return k.public_key().verify(sig, data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())


def run(data, sig, ct, peer_public, alg):
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return _make_key(key, data, sig, ct, peer_public, alg)
