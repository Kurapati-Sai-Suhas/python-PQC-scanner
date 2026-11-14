"""Synthetic case pyca-rsa-key-decrypt / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.decrypt(ct, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return _handle(key, data, sig, ct, peer_public, alg)
