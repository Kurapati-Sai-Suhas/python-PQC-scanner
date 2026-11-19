"""Synthetic case pyca-ec-key-runtime / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def run(data, sig, ct, peer_public, alg):
    material = ec.generate_private_key(ec.SECP256R1())
    if alg == "A":
        r0 = material.sign(data, ec.ECDSA(hashes.SHA256()))
    else:
        r0 = material.exchange(ec.ECDH(), peer_public)
    return r0
