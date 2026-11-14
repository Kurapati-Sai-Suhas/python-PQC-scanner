"""Synthetic case neg-pyca-pss-object / class-method (pqscan synthetic generator 1.0). Never executed."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class Engine:
    def act(self, data, sig, ct, peer_public, alg):
        r0 = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
        return r0
