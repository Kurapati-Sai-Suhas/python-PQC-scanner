"""Fixture application module for end-to-end tests. Contains a test-only PEM literal that must never
appear in any output."""
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import hashes, serialization

EMBEDDED = b"""-----BEGIN PRIVATE KEY-----
MIIBVQIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEAtestonlytestonlytestonlytestonly
-----END PRIVATE KEY-----"""


class Signer:
    def __init__(self):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=3072)

    def sign(self, msg):
        return self.key.sign(msg, padding.PSS(padding.MGF1(hashes.SHA256()), 32), hashes.SHA256())


class Agreement:
    def start(self):
        self.priv = ec.generate_private_key(ec.SECP384R1())

    def shared(self, peer):
        return self.priv.exchange(ec.ECDH(), peer)


def wrap(pem, cek):
    pub = serialization.load_pem_public_key(pem)
    return pub.encrypt(cek, padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None))


def unknown_use(key, data):
    return key.sign(data)
