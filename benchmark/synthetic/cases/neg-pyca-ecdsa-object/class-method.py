"""Synthetic case neg-pyca-ecdsa-object / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


class Session:
    def act(self, data, sig, ct, peer_public, alg):
        r0 = ec.ECDSA(hashes.SHA256())
        return r0
