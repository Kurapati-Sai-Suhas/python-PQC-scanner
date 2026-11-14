"""Synthetic case pyca-ec-op-exchange / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(ec.ECDH(), peer_public)
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    k = ec.generate_private_key(ec.SECP256R1())
    return HANDLERS["default"](k, data, sig, ct, peer_public, alg)
