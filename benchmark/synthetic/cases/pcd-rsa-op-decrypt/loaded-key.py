"""Synthetic case pcd-rsa-op-decrypt / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def run(data, sig, ct, peer_public, alg, pem):
    key = RSA.import_key(pem)
    r0 = PKCS1_OAEP.new(key).decrypt(ct)
    return (r0,)
