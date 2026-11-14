"""Synthetic case pyca-rsa-key-export / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg):
    kp = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    r0 = kp.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
