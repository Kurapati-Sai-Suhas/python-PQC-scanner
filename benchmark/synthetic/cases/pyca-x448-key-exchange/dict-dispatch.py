"""Synthetic case pyca-x448-key-exchange / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(peer_public)
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    kp = x448.X448PrivateKey.generate()
    return HANDLERS["default"](kp, data, sig, ct, peer_public, alg)
