"""Synthetic case pyca-rsa-op-verify / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    signing_key = serialization.load_pem_private_key(pem, password=None)
    r0 = signing_key.public_key().verify(sig, data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    return (r0,)
