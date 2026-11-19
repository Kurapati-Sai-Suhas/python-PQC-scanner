"""Synthetic case pyca-ec-op-verify / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _make_key(k, data, sig, ct, peer_public, alg):
    return k.public_key().verify(sig, data, ec.ECDSA(hashes.SHA256()))


def run(data, sig, ct, peer_public, alg):
    signing_key = ec.generate_private_key(ec.SECP256R1())
    return _make_key(signing_key, data, sig, ct, peer_public, alg)
