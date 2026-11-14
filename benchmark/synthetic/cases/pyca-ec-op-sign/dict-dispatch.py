"""Synthetic case pyca-ec-op-sign / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _handle(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data, ec.ECDSA(hashes.SHA256()))
    return (r0,)


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    material = ec.generate_private_key(ec.SECP256R1())
    return HANDLERS["default"](material, data, sig, ct, peer_public, alg)
