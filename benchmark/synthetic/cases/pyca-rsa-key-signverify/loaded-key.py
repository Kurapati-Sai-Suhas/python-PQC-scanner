"""Synthetic case pyca-rsa-key-signverify / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    key = serialization.load_pem_private_key(pem, password=None)
    r0 = key.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    r1 = key.public_key().verify(sig, data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    return (r0, r1)
