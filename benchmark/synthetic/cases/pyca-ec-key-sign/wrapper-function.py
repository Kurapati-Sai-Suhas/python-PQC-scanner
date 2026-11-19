"""Synthetic case pyca-ec-key-sign / wrapper-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _new_key():
    return ec.generate_private_key(ec.SECP256R1())


def run(data, sig, ct, peer_public, alg):
    priv = _new_key()
    r0 = priv.sign(data, ec.ECDSA(hashes.SHA256()))
    return (r0,)
