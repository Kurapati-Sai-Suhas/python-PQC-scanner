"""Synthetic case pyca-x25519-op-exchange / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x25519


def _process(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(peer_public)
    return (r0,)


HANDLERS = {"default": _process, "A": _process}


def run(data, sig, ct, peer_public, alg):
    material = x25519.X25519PrivateKey.generate()
    return HANDLERS["default"](material, data, sig, ct, peer_public, alg)
