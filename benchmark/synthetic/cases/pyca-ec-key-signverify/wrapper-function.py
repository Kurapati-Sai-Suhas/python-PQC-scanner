"""Synthetic case pyca-ec-key-signverify / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _new_key():
    return ec.generate_private_key(ec.SECP256R1())


def run(data, sig, ct, peer_public, alg):
    kp = _new_key()
    r0 = kp.sign(data, ec.ECDSA(hashes.SHA256()))
    r1 = kp.public_key().verify(sig, data, ec.ECDSA(hashes.SHA256()))
    return (r0, r1)
