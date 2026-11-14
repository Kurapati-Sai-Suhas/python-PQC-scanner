"""Synthetic case pcd-rsa-op-encrypt-v15 / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def run(data, sig, ct, peer_public, alg, pem):
    k = RSA.import_key(pem)
    r0 = PKCS1_v1_5.new(k.publickey()).encrypt(data)
    return (r0,)
