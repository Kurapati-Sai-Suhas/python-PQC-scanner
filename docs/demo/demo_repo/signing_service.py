# DEMONSTRATION FIXTURE — synthetic, written for this demo.
# Never imported or executed; it exists only to be scanned by pqscan. Contains no key material.
"""RSA-PSS signing and verification of release manifests (synthetic example)."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def sign_and_check_manifest(manifest: bytes) -> bytes:
    signing_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    pss = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    signature = signing_key.sign(manifest, pss, hashes.SHA256())
    verify_key = signing_key.public_key()
    verify_key.verify(signature, manifest, pss, hashes.SHA256())
    return signature
