"""Synthetic case pcd-rsa-key-decrypt / cross-function (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def _use(k, data, sig, ct, peer_public, alg):
    r0 = PKCS1_OAEP.new(k).decrypt(ct)
    return (r0,)


def run(data, sig, ct, peer_public, alg):
    kp = RSA.generate(3072)
    return _use(kp, data, sig, ct, peer_public, alg)
