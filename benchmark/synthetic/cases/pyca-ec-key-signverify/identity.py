"""Synthetic case pyca-ec-key-signverify / identity (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def run(data, sig, ct, peer_public, alg):
    material = ec.generate_private_key(ec.SECP256R1())
    r0 = material.sign(data, ec.ECDSA(hashes.SHA256()))
    r1 = material.public_key().verify(sig, data, ec.ECDSA(hashes.SHA256()))
    return (r0, r1)
