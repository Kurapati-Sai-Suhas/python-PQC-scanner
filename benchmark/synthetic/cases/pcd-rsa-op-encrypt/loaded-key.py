"""Synthetic case pcd-rsa-op-encrypt / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def run(data, sig, ct, peer_public, alg, pem):
    signing_key = RSA.import_key(pem)
    r0 = PKCS1_OAEP.new(signing_key.publickey()).encrypt(data)
    return (r0,)
