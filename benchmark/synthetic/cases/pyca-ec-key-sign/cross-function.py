"""Synthetic case pyca-ec-key-sign / cross-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data, ec.ECDSA(hashes.SHA256()))
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    signing_key = ec.generate_private_key(ec.SECP256R1())
    return _handle(signing_key, data, sig, ct, peer_public, alg)
