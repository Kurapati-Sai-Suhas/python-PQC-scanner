# DEMONSTRATION FIXTURE — synthetic, written for this demo.
# Never imported or executed; it exists only to be scanned by pqscan. Contains no key material.
"""X25519 and ECDH (P-384) key agreement (synthetic example)."""
from cryptography.hazmat.primitives.asymmetric import ec, x25519


def x25519_shared_secret() -> bytes:
    ours = x25519.X25519PrivateKey.generate()
    theirs = x25519.X25519PrivateKey.generate()
    return ours.exchange(theirs.public_key())


def ecdh_shared_secret() -> bytes:
    ours = ec.generate_private_key(ec.SECP384R1())
    theirs = ec.generate_private_key(ec.SECP384R1())
    return ours.exchange(ec.ECDH(), theirs.public_key())
