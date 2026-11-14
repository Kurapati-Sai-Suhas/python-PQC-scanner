from cryptography.hazmat.primitives.asymmetric import ec
def test_k():
    k = ec.generate_private_key(ec.SECP256R1())
    return k.sign(b"x", ec.ECDSA(__import__("cryptography.hazmat.primitives.hashes", fromlist=["SHA256"]).SHA256()))
