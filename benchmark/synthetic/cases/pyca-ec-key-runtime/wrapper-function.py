"""Synthetic case pyca-ec-key-runtime / wrapper-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _make_key():
    return ec.generate_private_key(ec.SECP256R1())


def run(data, sig, ct, peer_public, alg):
    kp = _make_key()
    if alg == "A":
        r0 = kp.sign(data, ec.ECDSA(hashes.SHA256()))
    else:
        r0 = kp.exchange(ec.ECDH(), peer_public)
    return r0
