"""Synthetic case neg-out-of-scope-ecdsa / alias-import (pqscan synthetic generator 1.1). Never executed."""


from ecdsa import SigningKey, NIST256p

def run(data, sig, ct, peer_public, alg):
    r0 = SigningKey.generate(curve=NIST256p)
    return r0
