# DEMONSTRATION FIXTURE — synthetic, written for this demo.
# Never imported or executed; it exists only to be scanned by pqscan. Contains no key material.
"""An RSA key that is generated and serialised but never used for any operation here (synthetic example).
Its cryptographic role cannot be read from this file: it is inventory only."""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def export_new_public_key() -> bytes:
    archive_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    pem = archive_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem
