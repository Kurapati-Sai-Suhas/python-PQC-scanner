"""Synthetic case pyca-ed25519-op-verify / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    kp = serialization.load_pem_private_key(pem, password=None)
    r0 = kp.public_key().verify(sig, data)
    return (r0,)
