"""Synthetic case pyca-rsa-key-runtime / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization


def run(data, sig, ct, peer_public, alg, pem):
    kp = serialization.load_pem_private_key(pem, password=None)
    if alg == "A":
        r0 = kp.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    else:
        r0 = kp.decrypt(ct, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return r0
