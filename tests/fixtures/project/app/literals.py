import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

REGISTRY = {}


def leak_paths(c):
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    REGISTRY["LITERAL_TARGET_QX7"] = k
    getattr(__import__("vendorlib_LITERAL_CALLEE_QX7"), "use")(k)
    return k.decrypt(base64.b64decode("LITERAL_ARG_QX7_U0VDUkVU"), padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None))
