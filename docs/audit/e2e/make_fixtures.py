"""Create the synthetic end-to-end fixtures for docs/audit/e2e/run_e2e.sh (written fresh on every run).

    python make_fixtures.py <dir>

Nothing here is executed by pqscan; the files are only parsed. Two fixture repositories:
  hybrid/     an approved PQ/T hybrid (X25519 + ML-KEM-768 combined in one KDF input) and a dual-stack class that
              computes both but never combines them (must NOT be treated as a hybrid)
  robustness/ files pqscan must survive: syntax error, a null byte, latin-1 bytes, Python 2 syntax, out-of-scope
              libraries (python-rsa, python-ecdsa), a symmetric-only file, and one valid RSA signing site
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
h = root / "hybrid"
r = root / "robustness"
h.mkdir(parents=True, exist_ok=True)
r.mkdir(parents=True, exist_ok=True)

(h / "kex.py").write_text('''import hashlib
from cryptography.hazmat.primitives.asymmetric import x25519, mlkem


class HybridKex:
    """X25519 + ML-KEM-768, secrets combined (approved PQ/T hybrid shape, SP 800-227 Sec. 4.6)."""
    def start(self):
        self.x = x25519.X25519PrivateKey.generate()
        self.k = mlkem.MLKEM768PrivateKey.generate()

    def _classical(self, peer):
        secret = self.x.exchange(peer)
        return secret

    def finish(self, ct, peer):
        k_pq = self.k.decapsulate(ct)
        k_cl = self._classical(peer)
        return hashlib.sha256(k_pq + k_cl).digest()


class DualStack:
    """Both algorithms present, but the classical secret is used on its own: NOT a hybrid."""
    def legacy(self, peer):
        self.k2 = x25519.X25519PrivateKey.generate()
        return hashlib.sha256(self.k2.exchange(peer)).digest()

    def pq(self, pk):
        self.m = mlkem.MLKEM768PrivateKey.generate()
        ss, ct = pk.encapsulate()
        return hashlib.sha256(ss).digest()
''', encoding="utf-8")

(r / "syntax_error.py").write_text("from cryptography.hazmat.primitives.asymmetric import rsa\ndef broken(:\n    pass\n", encoding="utf-8")
(r / "nullbyte.py").write_bytes(b"from cryptography.hazmat.primitives.asymmetric import rsa\nk = rsa.generate_private_key(65537, 2048)\x00\n")
(r / "latin1.py").write_bytes("# -*- coding: latin-1 -*-\n# caf\xe9\nfrom cryptography.hazmat.primitives.asymmetric import ec\n"
                              "k = ec.generate_private_key(ec.SECP256R1())\n".encode("latin-1"))
(r / "py2_syntax.py").write_text("from Crypto.PublicKey import RSA\nprint 'legacy python 2'\nk = RSA.generate(2048)\n", encoding="utf-8")
(r / "out_of_scope.py").write_text("import rsa\nimport ecdsa\npub, priv = rsa.newkeys(2048)\nsk = ecdsa.SigningKey.generate()\n", encoding="utf-8")
(r / "symmetric_only.py").write_text("from cryptography.fernet import Fernet\nf = Fernet(Fernet.generate_key())\ntoken = f.encrypt(b'x')\nf.decrypt(token)\n", encoding="utf-8")
(r / "good.py").write_text('''from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def sign(payload):
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    return key.sign(payload, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32), hashes.SHA256())
''', encoding="utf-8")
print("fixtures written to", root)
