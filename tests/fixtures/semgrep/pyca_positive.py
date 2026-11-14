"""Module A positive fixture — PyCA cryptography. Every line that must be matched carries
the marker syntax (hash, the word expect, a colon, rule ids); lines without a marker must produce no finding."""
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding, x25519, x448, ed25519, dh
from cryptography.hazmat.primitives.asymmetric import mlkem
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import pkcs12, load_pem_private_key as lppk
from cryptography import x509
import cryptography.hazmat.primitives.asymmetric.rsa as rsa_mod


def keygen():
    k1 = rsa.generate_private_key(public_exponent=65537, key_size=2048)  # expect: pqscan.pyca.rsa.keygen
    k2 = rsa_mod.generate_private_key(public_exponent=65537, key_size=3072)  # expect: pqscan.pyca.rsa.keygen
    k3 = ec.generate_private_key(ec.SECP256R1())  # expect: pqscan.pyca.ec.keygen
    k4 = ec.derive_private_key(12345, ec.SECP384R1())  # expect: pqscan.pyca.ec.derive
    k5 = x25519.X25519PrivateKey.generate()  # expect: pqscan.pyca.x25519.keygen
    k6 = x448.X448PrivateKey.generate()  # expect: pqscan.pyca.x25519.keygen
    k7 = ed25519.Ed25519PrivateKey.generate()  # expect: pqscan.pyca.ed25519.keygen
    params = dh.generate_parameters(generator=2, key_size=2048)  # expect: pqscan.pyca.dh.parameters
    return k1, k2, k3, k4, k5, k6, k7, params


def construct(n, e, d, p, q, x, y):
    pub = rsa.RSAPublicNumbers(e, n)  # expect: pqscan.pyca.rsa.construct
    priv = rsa.RSAPrivateNumbers(p, q, d, 1, 1, 1, pub).private_key()  # expect: pqscan.pyca.rsa.construct
    ecpub = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()  # expect: pqscan.pyca.ec.construct
    ecpt = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), b"\x04")  # expect: pqscan.pyca.ec.construct
    xpub = x25519.X25519PublicKey.from_public_bytes(b"\x00" * 32)  # expect: pqscan.pyca.x25519.keygen
    return pub, priv, ecpub, ecpt, xpub


def loaders(data, password):
    a = serialization.load_pem_private_key(data, password=password)  # expect: pqscan.pyca.loader.pem
    b = lppk(data, password=None)  # expect: pqscan.pyca.loader.pem
    c = serialization.load_pem_public_key(data)  # expect: pqscan.pyca.loader.pem
    d = serialization.load_der_private_key(data, password=None)  # expect: pqscan.pyca.loader.der
    e = serialization.load_der_public_key(data)  # expect: pqscan.pyca.loader.der
    f = serialization.load_ssh_private_key(data, password=None)  # expect: pqscan.pyca.loader.ssh
    g = serialization.load_ssh_public_key(data)  # expect: pqscan.pyca.loader.ssh
    h = pkcs12.load_key_and_certificates(data, password)  # expect: pqscan.pyca.loader.pkcs12
    i = x509.load_pem_x509_certificate(data)  # expect: pqscan.pyca.loader.x509
    j = x509.load_der_x509_certificate(data).public_key()  # expect: pqscan.pyca.loader.x509
    return a, b, c, d, e, f, g, h, i, j


class Holder:
    def __init__(self, key):
        self.key = key

    def ops(self, msg, sig, peer):
        s = self.key.sign(msg, padding.PKCS1v15(), hashes.SHA256())  # expect: pqscan.common.method.candidate
        self.key.public_key().verify(sig, msg, padding.PSS(padding.MGF1(hashes.SHA256()), 32), hashes.SHA256())  # expect: pqscan.common.method.candidate
        shared = self.key.exchange(ec.ECDH(), peer)  # expect: pqscan.common.method.candidate
        ct = self.key.public_key().encrypt(msg, padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None))  # expect: pqscan.common.method.candidate
        pt = self.key.decrypt(ct, padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None))  # expect: pqscan.common.method.candidate
        return s, shared, pt


def hybrid():
    kem = mlkem.MLKEM768PrivateKey.generate()  # expect: pqscan.pyca.pqc.presence
    return kem
