"""Synthetic case pyca-ec-op-verify / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _process(k, data, sig, ct, peer_public, alg):
    r0 = k.public_key().verify(sig, data, ec.ECDSA(hashes.SHA256()))
    return (r0,)


HANDLERS = {"default": _process, "A": _process}


def run(data, sig, ct, peer_public, alg):
    sk = ec.generate_private_key(ec.SECP256R1())
    return HANDLERS["default"](sk, data, sig, ct, peer_public, alg)
