"""Synthetic case pyca-ed25519-op-sign / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _use(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data)
    return (r0,)


HANDLERS = {"default": _use, "A": _use}


def run(data, sig, ct, peer_public, alg):
    material = ed25519.Ed25519PrivateKey.generate()
    return HANDLERS["default"](material, data, sig, ct, peer_public, alg)
