"""Synthetic case pyca-ec-op-sign / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def run(data, sig, ct, peer_public, alg):
    sk = ec.generate_private_key(ec.SECP256R1())
    r0 = sk.sign(data, ec.ECDSA(hashes.SHA256()))
    return (r0,)
