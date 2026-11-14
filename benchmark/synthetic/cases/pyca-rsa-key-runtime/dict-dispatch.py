"""Synthetic case pyca-rsa-key-runtime / dict-dispatch (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _handle(k, data, sig, ct, peer_public, alg):
    if alg == "A":
        r0 = k.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    else:
        r0 = k.decrypt(ct, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return r0


HANDLERS = {"default": _handle, "A": _handle}


def run(data, sig, ct, peer_public, alg):
    sk = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return HANDLERS[alg](sk, data, sig, ct, peer_public, alg)
