"""Synthetic case pyca-ec-key-sign / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def run(data, sig, ct, peer_public, alg):
    kp = ec.generate_private_key(ec.SECP256R1())
    r0 = kp.sign(data, ec.ECDSA(hashes.SHA256()))
    return (r0,)
