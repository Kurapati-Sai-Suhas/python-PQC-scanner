"""Synthetic case pyca-ed448-key-sign / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed448


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data)
    return (r0,)


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    signing_key = ed448.Ed448PrivateKey.generate()
    return HANDLERS["default"](signing_key, data, sig, ct, peer_public, alg)
