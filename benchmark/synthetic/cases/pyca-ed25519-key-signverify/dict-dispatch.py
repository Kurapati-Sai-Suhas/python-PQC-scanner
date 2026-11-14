"""Synthetic case pyca-ed25519-key-signverify / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ed25519


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data)
    r1 = k.public_key().verify(sig, data)
    return (r0, r1)


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    sk = ed25519.Ed25519PrivateKey.generate()
    return HANDLERS["default"](sk, data, sig, ct, peer_public, alg)
