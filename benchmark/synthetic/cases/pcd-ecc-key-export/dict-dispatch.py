"""Synthetic case pcd-ecc-key-export / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import ECC


def _process(k, data, sig, ct, peer_public, alg):
    r0 = k.export_key(format="PEM")
    return (r0,)


HANDLERS = {"default": _process, "A": _process}


def run(data, sig, ct, peer_public, alg):
    kp = ECC.generate(curve="P-256")
    return HANDLERS["default"](kp, data, sig, ct, peer_public, alg)
