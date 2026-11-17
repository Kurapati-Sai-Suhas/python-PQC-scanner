"""Synthetic worked example for the manuscript (Sec. VI-F). Written for the paper. It is not taken from the pilot,
a benchmark repository or a test repository. It is only parsed by pqscan, never executed or imported.

Expected behaviour (verified by running pqscan; see docs/paper/example/README.md):
  K1  load_pem_private_key: key material whose consumers are found through a wrapper and an attribute
  O1  self._key.sign(..., PSS, ...): an operation whose receiver is traced to K1
  O2  key.sign(..., PKCS1v15, ...): an operation whose key arrives as an unresolved parameter, so it abstains
  K2  generate_private_key returned to unknown callers: no consumer in scope, so it abstains
  K3  one key consumed by sign AND decrypt (two families), so UNKNOWN and it abstains
"""
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa as rsa_alias        # import alias


def _load_signing_key(pem: bytes):                                               # private wrapper
    return serialization.load_pem_private_key(pem, password=None)               # K1


class TokenSigner:
    def __init__(self, pem: bytes):
        self._key = _load_signing_key(pem)                                       # wrapper result -> attribute

    def sign(self, payload: bytes) -> bytes:
        return self._key.sign(                                                    # O1
            payload,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )


def sign_with(key, payload: bytes) -> bytes:
    return key.sign(payload, padding.PKCS1v15(), hashes.SHA256())                # O2: key is a parameter


def make_key():
    return rsa_alias.generate_private_key(public_exponent=65537, key_size=3072)  # K2: returned, no in-module consumer


class Envelope:
    def __init__(self):
        self._k = rsa_alias.generate_private_key(public_exponent=65537, key_size=3072)   # K3

    def seal_signature(self, message: bytes) -> bytes:
        return self._k.sign(message, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                                 salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())

    def open(self, ciphertext: bytes) -> bytes:
        return self._k.decrypt(ciphertext, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                                                        algorithm=hashes.SHA256(), label=None))
