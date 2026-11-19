"""Synthetic case pyca-ec-key-sign / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _use(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data, ec.ECDSA(hashes.SHA256()))
    return (r0,)


HANDLERS = {"default": _use, "A": _use}


def run(data, sig, ct, peer_public, alg):
    k = ec.generate_private_key(ec.SECP256R1())
    return HANDLERS["default"](k, data, sig, ct, peer_public, alg)
