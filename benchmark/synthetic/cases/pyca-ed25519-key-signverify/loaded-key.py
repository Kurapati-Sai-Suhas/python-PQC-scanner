"""Synthetic case pyca-ed25519-key-signverify / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    kp = serialization.load_pem_private_key(pem, password=None)
    r0 = kp.sign(data)
    r1 = kp.public_key().verify(sig, data)
    return (r0, r1)
