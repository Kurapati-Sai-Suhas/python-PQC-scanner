"""Synthetic case pyca-ec-key-runtime / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    kp = serialization.load_pem_private_key(pem, password=None)
    if alg == "A":
        r0 = kp.sign(data, ec.ECDSA(hashes.SHA256()))
    else:
        r0 = kp.exchange(ec.ECDH(), peer_public)
    return r0
