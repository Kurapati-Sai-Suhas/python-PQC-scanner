"""Synthetic case pyca-rsa-op-decrypt / dict-dispatch (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _process(k, data, sig, ct, peer_public, alg):
    r0 = k.decrypt(ct, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return (r0,)


HANDLERS = {"default": _process, "A": _process}


def run(data, sig, ct, peer_public, alg):
    signing_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return HANDLERS["default"](signing_key, data, sig, ct, peer_public, alg)
