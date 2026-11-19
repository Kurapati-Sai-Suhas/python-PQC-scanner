"""Synthetic case neg-pyca-isinstance / class-method (pqscan synthetic generator 1.1). Never executed."""
from cryptography.hazmat.primitives.asymmetric import rsa


class Backend:
    def act(self, data, sig, ct, peer_public, alg):
        r0 = isinstance(data, rsa.RSAPrivateKey)
        return r0
