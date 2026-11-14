"""Synthetic case pyca-ec-key-runtime / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _process(k, data, sig, ct, peer_public, alg):
    if alg == "A":
        r0 = k.sign(data, ec.ECDSA(hashes.SHA256()))
    else:
        r0 = k.exchange(ec.ECDH(), peer_public)
    return r0


def run(data, sig, ct, peer_public, alg):
    kp = ec.generate_private_key(ec.SECP256R1())
    return _process(kp, data, sig, ct, peer_public, alg)
