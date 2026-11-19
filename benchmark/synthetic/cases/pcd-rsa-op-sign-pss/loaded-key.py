"""Synthetic case pcd-rsa-op-sign-pss / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pss


def run(data, sig, ct, peer_public, alg, pem):
    signing_key = RSA.import_key(pem)
    r0 = pss.new(signing_key).sign(SHA256.new(data))
    return (r0,)
