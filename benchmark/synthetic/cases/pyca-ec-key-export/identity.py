"""Synthetic case pyca-ec-key-export / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg):
    kp = ec.generate_private_key(ec.SECP256R1())
    r0 = kp.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
