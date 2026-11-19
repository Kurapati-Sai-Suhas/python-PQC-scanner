"""Synthetic case pyca-ec-key-runtime / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _apply(k, data, sig, ct, peer_public, alg):
    if alg == "A":
        r0 = k.sign(data, ec.ECDSA(hashes.SHA256()))
    else:
        r0 = k.exchange(ec.ECDH(), peer_public)
    return r0


HANDLERS = {"default": _apply, "A": _apply}


def run(data, sig, ct, peer_public, alg):
    priv = ec.generate_private_key(ec.SECP256R1())
    return HANDLERS[alg](priv, data, sig, ct, peer_public, alg)
