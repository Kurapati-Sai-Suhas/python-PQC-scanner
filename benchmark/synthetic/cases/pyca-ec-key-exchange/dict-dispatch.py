"""Synthetic case pyca-ec-key-exchange / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


def _use(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(ec.ECDH(), peer_public)
    return (r0,)


HANDLERS = {"default": _use, "A": _use}


def run(data, sig, ct, peer_public, alg):
    signing_key = ec.generate_private_key(ec.SECP256R1())
    return HANDLERS["default"](signing_key, data, sig, ct, peer_public, alg)
