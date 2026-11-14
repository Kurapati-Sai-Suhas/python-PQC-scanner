"""Synthetic case pyca-ec-op-verify / cross-function (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def _process(k, data, sig, ct, peer_public, alg):
    r0 = k.public_key().verify(sig, data, ec.ECDSA(hashes.SHA256()))
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    sk = ec.generate_private_key(ec.SECP256R1())
    return _process(sk, data, sig, ct, peer_public, alg)
