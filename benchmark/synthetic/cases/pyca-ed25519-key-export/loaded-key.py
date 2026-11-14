"""Synthetic case pyca-ed25519-key-export / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    kp = serialization.load_pem_private_key(pem, password=None)
    r0 = kp.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
