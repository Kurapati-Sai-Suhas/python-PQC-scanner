"""Synthetic case pyca-ec-key-signverify / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _apply(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data, ec.ECDSA(hashes.SHA256()))
    r1 = k.public_key().verify(sig, data, ec.ECDSA(hashes.SHA256()))
    return (r0, r1)


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    k = ec.generate_private_key(ec.SECP256R1())
    return HANDLERS["default"](k, data, sig, ct, peer_public, alg)
