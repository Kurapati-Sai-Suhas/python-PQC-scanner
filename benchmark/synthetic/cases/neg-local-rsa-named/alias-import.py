"""Synthetic case neg-local-rsa-named / alias-import (pqscan synthetic generator 1.0). Never executed."""


def rsa_sign(payload):
    return payload[::-1]

def run(data, sig, ct, peer_public, alg):
    r0 = rsa_sign(data)
    return r0
