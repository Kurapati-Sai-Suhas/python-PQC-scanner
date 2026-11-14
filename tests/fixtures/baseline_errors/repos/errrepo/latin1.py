from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
def f(m):
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return k.sign(m, padding.PKCS1v15(), hashes.SHA256())
# café latin-1 byte
