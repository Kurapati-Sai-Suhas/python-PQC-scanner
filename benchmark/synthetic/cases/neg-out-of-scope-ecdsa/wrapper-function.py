"""Synthetic case neg-out-of-scope-ecdsa / wrapper-function (pqscan synthetic generator 1.1). Never executed."""


from ecdsa import SigningKey, NIST256p

def _handle(data, sig, ct, peer_public, alg):
    r0 = SigningKey.generate(curve=NIST256p)
    return r0


def run(data, sig, ct, peer_public, alg):
    return _handle(data, sig, ct, peer_public, alg)
