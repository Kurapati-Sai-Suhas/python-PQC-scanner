"""Synthetic case neg-local-sign-method / class-method (pqscan synthetic generator 1.0). Never executed."""


class Token:
    def sign(self, payload):
        return payload[::-1]

class Engine:
    def act(self, data, sig, ct, peer_public, alg):
        r0 = Token().sign(data)
        return r0
