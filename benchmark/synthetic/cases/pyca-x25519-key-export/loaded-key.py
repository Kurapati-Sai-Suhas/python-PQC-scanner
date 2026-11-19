"""Synthetic case pyca-x25519-key-export / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    signing_key = serialization.load_pem_private_key(pem, password=None)
    r0 = signing_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return (r0,)
