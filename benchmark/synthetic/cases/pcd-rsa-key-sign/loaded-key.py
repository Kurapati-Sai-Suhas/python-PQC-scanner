"""Synthetic case pcd-rsa-key-sign / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def run(data, sig, ct, peer_public, alg, pem):
    material = RSA.import_key(pem)
    r0 = pkcs1_15.new(material).sign(SHA256.new(data))
    return (r0,)
