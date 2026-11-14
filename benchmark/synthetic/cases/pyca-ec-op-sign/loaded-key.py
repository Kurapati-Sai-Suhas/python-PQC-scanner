"""Synthetic case pyca-ec-op-sign / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    key = serialization.load_pem_private_key(pem, password=None)
    r0 = key.sign(data, ec.ECDSA(hashes.SHA256()))
    return (r0,)
