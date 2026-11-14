"""Synthetic case pyca-x25519-key-exchange / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x25519


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(peer_public)
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    material = x25519.X25519PrivateKey.generate()
    return HANDLERS["default"](material, data, sig, ct, peer_public, alg)
