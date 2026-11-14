"""Synthetic case pyca-ec-op-sign / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _create(k, data, sig, ct, peer_public, alg):
    return k.sign(data, ec.ECDSA(hashes.SHA256()))


def run(data, sig, ct, peer_public, alg):
    key = ec.generate_private_key(ec.SECP256R1())
    return _create(key, data, sig, ct, peer_public, alg)
