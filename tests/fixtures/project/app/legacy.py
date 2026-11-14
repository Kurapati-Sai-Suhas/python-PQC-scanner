import rsa
from ecdsa import SigningKey


def legacy(msg):
    pub, priv = rsa.newkeys(2048)
    return rsa.sign(msg, priv, "SHA-256"), SigningKey.generate()
