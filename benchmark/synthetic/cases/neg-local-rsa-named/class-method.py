"""Synthetic case neg-local-rsa-named / class-method (pqscan synthetic generator 1.1). Never executed."""


def rsa_sign(payload):
    return payload[::-1]

class Backend:
    def act(self, data, sig, ct, peer_public, alg):
        r0 = rsa_sign(data)
        return r0
