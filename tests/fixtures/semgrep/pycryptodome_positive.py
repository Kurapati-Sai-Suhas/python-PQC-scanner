"""Module A positive fixture — PyCryptodome (`Crypto` root) and pycryptodomex (`Cryptodome` root)."""
from Crypto.PublicKey import RSA, ECC, DSA
from Crypto.Signature import pkcs1_15, pss, DSS, eddsa
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Protocol import DH
import Cryptodome.PublicKey.RSA as XRSA
from Cryptodome.Signature import pkcs1_15 as xpkcs


def keys(pem):
    k1 = RSA.generate(2048)  # expect: pqscan.pcd.rsa.keygen
    k2 = RSA.import_key(pem)  # expect: pqscan.pcd.rsa.import
    k3 = RSA.importKey(pem)  # expect: pqscan.pcd.rsa.import
    k4 = RSA.construct((1, 2, 3))  # expect: pqscan.pcd.rsa.construct
    k5 = ECC.generate(curve="P-256")  # expect: pqscan.pcd.ecc.keygen
    k6 = ECC.import_key(pem)  # expect: pqscan.pcd.ecc.import
    k7 = ECC.construct(curve="P-256", d=5)  # expect: pqscan.pcd.ecc.construct
    k8 = DSA.generate(2048)  # expect: pqscan.pcd.dsa.keygen
    k9 = XRSA.generate(2048)  # expect: pqscan.pcd.rsa.keygen
    return k1, k2, k3, k4, k5, k6, k7, k8, k9


def sign_verify(key, msg, sig):
    h = SHA256.new(msg)
    s1 = pkcs1_15.new(key).sign(h)  # expect: pqscan.pcd.signer.new, pqscan.pcd.signer.sign
    signer = pss.new(key)  # expect: pqscan.pcd.signer.new
    s2 = signer.sign(h)  # expect: pqscan.common.method.candidate
    DSS.new(key, "fips-186-3").verify(h, sig)  # expect: pqscan.pcd.signer.new, pqscan.pcd.signer.sign
    v = eddsa.new(key, "rfc8032")  # expect: pqscan.pcd.signer.new
    xpkcs.new(key).verify(h, sig)  # expect: pqscan.pcd.signer.new, pqscan.pcd.signer.sign
    return s1, s2, v


def wrap(key, data):
    ct = PKCS1_OAEP.new(key).encrypt(data)  # expect: pqscan.pcd.cipher.new, pqscan.pcd.cipher.op
    cipher = PKCS1_v1_5.new(key)  # expect: pqscan.pcd.cipher.new
    pt = cipher.decrypt(ct, None)  # expect: pqscan.common.method.candidate
    return pt


def agree(priv, pub):
    return DH.key_agreement(static_priv=priv, static_pub=pub, kdf=lambda x: x)  # expect: pqscan.pcd.dh.key_agreement
