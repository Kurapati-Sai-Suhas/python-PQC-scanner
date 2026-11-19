"""Synthetic case pcd-rsa-key-signverify / loaded-key (pqscan synthetic generator 1.1). Never executed."""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15


def run(data, sig, ct, peer_public, alg, pem):
    priv = RSA.import_key(pem)
    r0 = pkcs1_15.new(priv).sign(SHA256.new(data))
    r1 = pkcs1_15.new(priv.publickey()).verify(SHA256.new(data), sig)
    return (r0, r1)
