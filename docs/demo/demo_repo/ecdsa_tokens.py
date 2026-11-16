# DEMONSTRATION FIXTURE — synthetic, written for this demo.
# Never imported or executed; it exists only to be scanned by pqscan. Contains no key material.
"""ECDSA (P-256) signing of session tokens (synthetic example)."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


def sign_token(token: bytes) -> bytes:
    token_key = ec.generate_private_key(ec.SECP256R1())
    return token_key.sign(token, ec.ECDSA(hashes.SHA256()))
