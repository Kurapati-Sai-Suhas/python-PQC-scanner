"""Synthetic case pcd-rsa-key-export / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA


def _process(k, data, sig, ct, peer_public, alg):
    r0 = k.export_key()
    return (r0,)


HANDLERS = {"default": _process, "A": _process}


def run(data, sig, ct, peer_public, alg):
    signing_key = RSA.generate(3072)
    return HANDLERS["default"](signing_key, data, sig, ct, peer_public, alg)
