# DEMONSTRATION FIXTURE — synthetic, written for this demo.
# Never imported or executed; it exists only to be scanned by pqscan. Contains no key material.
"""Legacy PyCryptodome code: RSA PKCS#1 v1.5 signatures and PKCS#1 OAEP encryption (synthetic example)."""
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


def legacy_sign(message: bytes) -> bytes:
    key = RSA.generate(3072)
    digest = SHA256.new(message)
    return pkcs1_15.new(key).sign(digest)


def legacy_encrypt(session_key: bytes) -> bytes:
    key = RSA.generate(3072)
    cipher = PKCS1_OAEP.new(key.publickey())
    return cipher.encrypt(session_key)
