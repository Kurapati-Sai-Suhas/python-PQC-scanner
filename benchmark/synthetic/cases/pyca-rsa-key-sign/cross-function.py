"""Synthetic case pyca-rsa-key-sign / cross-function (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def _use(k, data, sig, ct, peer_public, alg):
    r0 = k.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    material = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return _use(material, data, sig, ct, peer_public, alg)
