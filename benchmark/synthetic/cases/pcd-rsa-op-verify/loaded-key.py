"""Synthetic case pcd-rsa-op-verify / loaded-key (pqscan synthetic generator 1.0). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def run(data, sig, ct, peer_public, alg, pem):
    material = RSA.import_key(pem)
    r0 = pkcs1_15.new(material.publickey()).verify(SHA256.new(data), sig)
    return (r0,)
