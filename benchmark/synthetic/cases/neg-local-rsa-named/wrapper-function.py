"""Synthetic case neg-local-rsa-named / wrapper-function (pqscan synthetic generator 1.1). Never executed."""


def rsa_sign(payload):
    return payload[::-1]

def _use(data, sig, ct, peer_public, alg):
    r0 = rsa_sign(data)
    return r0


def run(data, sig, ct, peer_public, alg):
    return _use(data, sig, ct, peer_public, alg)
