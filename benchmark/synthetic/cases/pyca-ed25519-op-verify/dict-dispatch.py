"""Synthetic case pyca-ed25519-op-verify / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.public_key().verify(sig, data)
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    material = ed25519.Ed25519PrivateKey.generate()
    return HANDLERS["default"](material, data, sig, ct, peer_public, alg)
