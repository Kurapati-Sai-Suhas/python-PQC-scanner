"""Synthetic case pyca-x448-op-exchange / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import x448


def _process(k, data, sig, ct, peer_public, alg):
    r0 = k.exchange(peer_public)
    return (r0,)


HANDLERS = {"default": _process, "A": _process}


def run(data, sig, ct, peer_public, alg):
    sk = x448.X448PrivateKey.generate()
    return HANDLERS["default"](sk, data, sig, ct, peer_public, alg)
