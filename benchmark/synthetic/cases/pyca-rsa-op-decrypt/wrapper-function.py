"""Synthetic case pyca-rsa-op-decrypt / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _new_key(k, data, sig, ct, peer_public, alg):
    return k.decrypt(ct, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))


def run(data, sig, ct, peer_public, alg):
    sk = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return _new_key(sk, data, sig, ct, peer_public, alg)
