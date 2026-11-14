"""Synthetic case pyca-ed448-op-sign / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data)
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    material = ed448.Ed448PrivateKey.generate()
    return HANDLERS["default"](material, data, sig, ct, peer_public, alg)
