"""Synthetic case pyca-ec-op-verify / identity (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def run(data, sig, ct, peer_public, alg):
    priv = ec.generate_private_key(ec.SECP256R1())
    r0 = priv.public_key().verify(sig, data, ec.ECDSA(hashes.SHA256()))
    return (r0,)
