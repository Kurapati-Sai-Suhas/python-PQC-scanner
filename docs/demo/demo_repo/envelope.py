# DEMONSTRATION FIXTURE — synthetic, written for this demo.
# Never imported or executed; it exists only to be scanned by pqscan. Contains no key material.
"""RSA-OAEP key transport: wrap and unwrap a symmetric content key (synthetic example)."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def wrap_and_unwrap(content_key: bytes) -> bytes:
    recipient_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    oaep = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    wrapped = recipient_key.public_key().encrypt(content_key, oaep)
    return recipient_key.decrypt(wrapped, oaep)
