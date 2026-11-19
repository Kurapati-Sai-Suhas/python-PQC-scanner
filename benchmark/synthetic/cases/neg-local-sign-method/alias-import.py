"""Synthetic case neg-local-sign-method / alias-import (pqscan synthetic generator 1.1). Never executed."""


class Token:
    def sign(self, payload):
        return payload[::-1]

def run(data, sig, ct, peer_public, alg):
    r0 = Token().sign(data)
    return r0
