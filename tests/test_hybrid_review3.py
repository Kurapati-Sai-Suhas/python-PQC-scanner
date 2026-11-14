"""Independent review round 3: every reviewer probe kept as a regression test.
Positives (genuinely combined secrets/signatures) must be NO_ACTION_HYBRID at every classical site;
negatives (dual-stack, branch alternatives, fallbacks, ciphertext, logging, tuples, custom KEMs, nested
functions, unrelated messages) must never be."""
import pytest
from pqscan.semantic.evidence import analyze_source
from pqscan.roles import classify
from pqscan.policy import load_policy

HDR = """import hashlib, os
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric import ec, mlkem, mldsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
"""

PROBES = {
    'P1a hash(k_pq+k_cl) same fn': (True, '\nclass K:\n    def go(self, peer, pq_pub):\n        self.k = X25519PrivateKey.generate()\n        k_cl = self.k.exchange(peer)\n        k_pq, ct = pq_pub.encapsulate()\n        mlkem.MLKEM768PrivateKey.generate()\n        return hashlib.sha256(k_pq + k_cl).digest()\n'),
    'P1b KDF call with both args (module fn)': (True, '\ndef go(peer, pq_pub):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    ss_c = k.exchange(peer)\n    ss_q, ct = pq_pub.encapsulate()\n    return HKDF(hashes.SHA256(), 32, None, b"").derive(b"".join([ss_q, ss_c]))\n'),
    'P1c f-string': (True, '\ndef go(peer, sk, ct):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    b = sk.decapsulate(ct)\n    return f"{b}{a}"\n'),
    'P1d via helper returning classical': (True, '\nclass K:\n    def _x(self, peer):\n        s = self.k.exchange(peer)\n        return s\n    def setup(self):\n        self.k = X25519PrivateKey.generate()\n        self.m = mlkem.MLKEM768PrivateKey.generate()\n    def fin(self, peer, ct):\n        k_pq = self.m.decapsulate(ct)\n        k_cl = self._x(peer)\n        return hashlib.sha256(k_pq + k_cl).digest()\n'),
    'N1 dual-stack class, separate methods': (False, '\nclass K:\n    def legacy(self, peer):\n        self.k = X25519PrivateKey.generate()\n        return hashlib.sha256(self.k.exchange(peer)).digest()\n    def pq(self, pk):\n        self.m = mlkem.MLKEM768PrivateKey.generate()\n        ss, ct = pk.encapsulate()\n        return hashlib.sha256(ss).digest()\n'),
    'N2 same fn, both computed, not combined': (False, '\ndef go(peer, pk):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss, ct = pk.encapsulate()\n    return hashlib.sha256(a).digest(), ss\n'),
    'N3 branch: same variable from either path': (False, '\ndef derive(peer, pk, use_pq):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    if use_pq:\n        secret, ct = pk.encapsulate()\n    else:\n        secret = k.exchange(peer)\n    return hashlib.sha256(secret).digest()\n'),
    'N4 classical secret + ciphertext (indexing)': (False, '\ndef go(peer, pk):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ct = pk.encapsulate()[1]\n    return hashlib.sha256(a + ct).digest()\n'),
    'N5 classical secret + ciphertext (tuple 2nd elt)': (False, '\ndef go(peer, pk):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss, ct = pk.encapsulate()\n    return hashlib.sha256(a + ct).digest()\n'),
    'N6 classical secret + constant / mlkem pub bytes': (False, '\ndef go(peer):\n    k = X25519PrivateKey.generate()\n    m = mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    return hashlib.sha256(a + b"ctx" + m.public_key().public_bytes_raw()).digest()\n'),
    'N7 logged together': (False, '\nimport logging\ndef go(peer, pk):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss, ct = pk.encapsulate()\n    logging.debug("%d %d", len(a), len(ss))\n    return hashlib.sha256(a).digest()\n'),
    'N8 returned as tuple, used separately': (False, '\ndef go(peer, pk):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss, ct = pk.encapsulate()\n    return (a, ss)\n'),
    'N9 compare only': (False, '\ndef go(peer, pk):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss, ct = pk.encapsulate()\n    send(a); store(ss)\n    return len(a) == len(ss)\n'),
    'N10 non-mlkem encapsulate object (custom RSA-KEM)': (False, '\nclass RsaKem:\n    def encapsulate(self): return (b"x", b"y")\ndef go(peer):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss, ct = RsaKem().encapsulate()\n    return hashlib.sha256(a + ss).digest()\n'),
    'N11 combined in nested fn defined inside': (False, '\ndef go(peer, pk):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    def unused():\n        ss, ct = pk.encapsulate()\n        return ss + a\n    return hashlib.sha256(a).digest()\n'),
    'S1 composite sign (concat) positive': (True, '\nclass S:\n    def __init__(self):\n        self.ec = ec.generate_private_key(ec.SECP256R1())\n        self.pq = mldsa.MLDSA65PrivateKey.generate()\n    def sign(self, m):\n        s1 = self.ec.sign(m, ec.ECDSA(hashes.SHA256()))\n        s2 = self.pq.sign(m)\n        return s1 + s2\n'),
    'S2 sign both, not combined (separate returns)': (False, '\nclass S:\n    def __init__(self):\n        self.ec = ec.generate_private_key(ec.SECP256R1())\n        self.pq = mldsa.MLDSA65PrivateKey.generate()\n    def sign_legacy(self, m):\n        return self.ec.sign(m, ec.ECDSA(hashes.SHA256()))\n    def sign_pq(self, m):\n        return self.pq.sign(m)\n'),
    'S3 same fn, branch-selected sign': (False, '\nclass S:\n    def __init__(self):\n        self.ec = ec.generate_private_key(ec.SECP256R1())\n        self.pq = mldsa.MLDSA65PrivateKey.generate()\n    def sign(self, m, pq):\n        if pq:\n            sig = self.pq.sign(m)\n        else:\n            sig = self.ec.sign(m, ec.ECDSA(hashes.SHA256()))\n        return b"SIG" + sig\n'),
    'S4 verify: branch-selected (either-or) verification': (False, '\nclass V:\n    def __init__(self, ecpub, pqpub):\n        self.ec = ec.generate_private_key(ec.SECP256R1()).public_key()\n        self.pq = mldsa.MLDSA65PrivateKey.generate().public_key()\n    def verify(self, sig, m, alg):\n        if alg == "ecdsa":\n            self.ec.verify(sig, m, ec.ECDSA(hashes.SHA256()))\n        else:\n            self.pq.verify(sig, m)\n'),
    'S5 sign both, log lengths only': (False, '\nimport logging\nclass S:\n    def __init__(self):\n        self.ec = ec.generate_private_key(ec.SECP256R1())\n        self.pq = mldsa.MLDSA65PrivateKey.generate()\n    def sign(self, m):\n        s1 = self.ec.sign(m, ec.ECDSA(hashes.SHA256()))\n        s2 = self.pq.sign(m)\n        logging.info("%d %d", len(s1), len(s2))\n        return s1\n'),
    'S6 composite sign local vars (positive)': (True, '\ndef sign(m):\n    k = ec.generate_private_key(ec.SECP256R1())\n    q = mldsa.MLDSA65PrivateKey.generate()\n    s1 = k.sign(m, ec.ECDSA(hashes.SHA256()))\n    s2 = q.sign(m)\n    return s1 + s2\n'),
    'S7 local: branch-selected verify either-or': (False, '\ndef verify(sig, m, alg, ecpem):\n    k = ec.generate_private_key(ec.SECP256R1()).public_key()\n    q = mldsa.MLDSA65PrivateKey.generate().public_key()\n    if alg == "ecdsa":\n        k.verify(sig, m, ec.ECDSA(hashes.SHA256()))\n    else:\n        q.verify(sig, m)\n'),
    'S8 local: verify with try/except fallback': (False, '\ndef verify(sig, m):\n    k = ec.generate_private_key(ec.SECP256R1()).public_key()\n    q = mldsa.MLDSA65PublicKey.from_public_bytes(b"x")\n    try:\n        q.verify(sig, m)\n        return True\n    except Exception:\n        k.verify(sig, m, ec.ECDSA(hashes.SHA256()))\n        return True\n'),
    'S9 local: sign both, separate outputs': (False, '\ndef sign(m):\n    k = ec.generate_private_key(ec.SECP256R1())\n    q = mldsa.MLDSA65PrivateKey.generate()\n    s1 = k.sign(m, ec.ECDSA(hashes.SHA256()))\n    s2 = q.sign(m)\n    store(s1); store(s2)\n'),
    'S10 local: branch sign same var': (False, '\ndef sign(m, pq):\n    k = ec.generate_private_key(ec.SECP256R1())\n    q = mldsa.MLDSA65PrivateKey.generate()\n    if pq:\n        sig = q.sign(m)\n    else:\n        sig = k.sign(m, ec.ECDSA(hashes.SHA256()))\n    return b"v1" + sig\n'),
    'S11 self attrs composite verify (positive)': (True, '\nclass V:\n    def __init__(self):\n        self.k = ec.generate_private_key(ec.SECP256R1()).public_key()\n        self.q = mldsa.MLDSA65PrivateKey.generate().public_key()\n    def verify(self, s1, s2, m):\n        self.k.verify(s1, m, ec.ECDSA(hashes.SHA256()))\n        self.q.verify(s2, m)\n'),
    'S12 branch-selected verify, typed ML-DSA pub': (False, '\ndef verify(sig, m, alg, raw):\n    k = ec.generate_private_key(ec.SECP256R1()).public_key()\n    q = mldsa.MLDSA65PublicKey.from_public_bytes(raw)\n    if alg == "ecdsa":\n        k.verify(sig, m, ec.ECDSA(hashes.SHA256()))\n    else:\n        q.verify(sig, m)\n'),
    'S13 ECDSA verify of cert + unrelated ML-DSA verify of other msg': (False, '\ndef check(cert_sig, tbs, other_sig, other, raw):\n    k = ec.generate_private_key(ec.SECP256R1()).public_key()\n    k.verify(cert_sig, tbs, ec.ECDSA(hashes.SHA256()))\n    mldsa.MLDSA65PublicKey.from_public_bytes(raw).verify(other_sig, other)\n'),
}


def outcomes(body):
    pol = load_policy()
    out = []
    for ev in analyze_source('p.py', HDR + body):
        if ev.site_kind not in ('operation', 'key-material'):
            continue
        d = classify(ev)
        r = pol.apply(d, ev.hybrid_apis, ev.hybrid_combined)
        out.append((ev.site_kind, ev.operation, r.target_class if r else None))
    return out


@pytest.mark.parametrize('name', sorted(PROBES))
def test_review3_probe(name):
    positive, body = PROBES[name]
    res = outcomes(body)
    assert res, name
    if positive:
        ops = [r for r in res if r[0] == 'operation']
        assert ops and all(r[2] == 'NO_ACTION_HYBRID' for r in ops), (name, res)
    else:
        assert not any(r[2] == 'NO_ACTION_HYBRID' for r in res), (name, res)


def test_discarded_capability_probe_key_is_inventory_only():
    body = ("def is_available():\n    try:\n        X25519PrivateKey.generate()\n        mlkem.MLKEM768PrivateKey.generate()\n"
            "    except Exception:\n        return False\n    return True\n")
    res = outcomes(body)
    assert res == [("key-material", None, "INVENTORY")], res


def test_same_name_in_exclusive_branches_is_not_a_conflict():
    from cryptography.hazmat.primitives.asymmetric import rsa  # noqa: F401  (fixture realism only)
    body = ("from cryptography.hazmat.primitives.asymmetric import rsa, padding\n"
            "def sign(m, use_ec):\n    if use_ec:\n        k = ec.generate_private_key(ec.SECP256R1())\n"
            "        return k.sign(m, ec.ECDSA(hashes.SHA256()))\n    else:\n        k = rsa.generate_private_key(65537, 2048)\n"
            "        return k.sign(m, padding.PKCS1v15(), hashes.SHA256())\n")
    pol = load_policy()
    for ev in analyze_source("p.py", HDR + body):
        if ev.site_kind in ("operation", "key-material"):
            d = classify(ev)
            assert d.role is not None and d.role.value == "SIGN" and not d.conflicts, (ev.candidate.location.line, d.conflicts)
            assert pol.apply(d).target_class == "SIG"


def test_chained_keygen_public_key_encrypt_is_traced():
    body = ("from cryptography.hazmat.primitives.asymmetric import rsa, padding\n"
            "def wrap(cek):\n    return rsa.generate_private_key(65537, 2048).public_key().encrypt(cek, padding.OAEP("
            "padding.MGF1(hashes.SHA256()), hashes.SHA256(), None))\n")
    km = [ev for ev in analyze_source("p.py", HDR + body) if ev.site_kind == "key-material"][0]
    assert km.consumers.families == {"PKE"} and not km.consumers.escapes


def test_ml_dsa_operations_are_not_classical_sites():
    body = "def s(m):\n    q = mldsa.MLDSA65PrivateKey.generate()\n    return q.sign(m)\n"
    assert not [ev for ev in analyze_source("p.py", HDR + body) if ev.site_kind == "operation"]


@pytest.mark.parametrize("text, expected", [
    ("Avoid ML-KEM; use ML-DSA", "SIG"), ("ML-KEM is not suitable here; use ML-DSA", "SIG"),
    ("ML-KEM should not be used; use ML-DSA", "SIG"), ("Not recommended: ML-KEM. Use ML-DSA.", "SIG"),
    ("Use ML-DSA rather than ML-KEM", "SIG"), ("Use ML-DSA instead of ML-KEM", "SIG"),
    ("mlkem768 recommended", "KEM"), ("Use ml-kem-768", "KEM"),
    ("Do not use ML-KEM for signatures; migrate to ML-DSA", "SIG"), ("Not only ML-KEM but also ML-DSA", "DUAL"),
    ("ML-KEM (key establishment) / ML-DSA (signatures)", "DUAL"), ("Shor - migrate to ML-KEM-768", "KEM"),
])
def test_review3_phrasings(text, expected):
    from pqscan.bench.judge import classify_text
    assert classify_text(text) == expected


# ---------------------------------------------------------------- confirmation round: downgrade paths
PROBES_R4 = {
    'A1 combined only for fingerprint; session key classical-only': (False, '\ndef go(peer, raw, ct):\n    k = X25519PrivateKey.generate()\n    m = mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss = m.decapsulate(ct)\n    fp = hashlib.sha256(a + ss).hexdigest()\n    print(fp)\n    return HKDF(hashes.SHA256(), 32, None, b"").derive(a)\n'),
    'A2 early-return downgrade before combine': (False, '\ndef go(peer, ct, legacy):\n    k = X25519PrivateKey.generate()\n    m = mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss = m.decapsulate(ct)\n    if legacy:\n        return hashlib.sha256(a).digest()\n    return hashlib.sha256(ss + a).digest()\n'),
    'A3 shared helper: one hybrid caller, one legacy caller': (False, '\nclass K:\n    def setup(self):\n        self.k = X25519PrivateKey.generate()\n        self.m = mlkem.MLKEM768PrivateKey.generate()\n    def _x(self, peer):\n        s = self.k.exchange(peer)\n        return s\n    def hybrid(self, peer, ct):\n        k_pq = self.m.decapsulate(ct)\n        k_cl = self._x(peer)\n        return hashlib.sha256(k_pq + k_cl).digest()\n    def legacy(self, peer):\n        k_cl = self._x(peer)\n        return hashlib.sha256(k_cl).digest()\n'),
    'A4 compare_digest matches combiner regex': (False, '\nimport hmac\ndef go(peer, ct):\n    k = X25519PrivateKey.generate()\n    m = mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss = m.decapsulate(ct)\n    if hmac.compare_digest(a, ss):\n        raise ValueError\n    return hashlib.sha256(a).digest()\n'),
    'A5 untyped-parameter KEM fed a non-ML-KEM object': (False, '\nclass RsaKem:\n    def decapsulate(self, ct): return b"x"\ndef finish(peer, kem, ct):\n    k = X25519PrivateKey.generate()\n    mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss = kem.decapsulate(ct)\n    return hashlib.sha256(a + ss).digest()\ndef main(peer, ct):\n    return finish(peer, RsaKem(), ct)\n'),
    'A6 sign: message rebound between, same expr text': (False, '\ndef sign(m):\n    k = ec.generate_private_key(ec.SECP256R1())\n    q = mldsa.MLDSA65PrivateKey.generate()\n    s1 = k.sign(m, ec.ECDSA(hashes.SHA256()))\n    m = b"unrelated"\n    s2 = q.sign(m)\n    return s1 + s2\n'),
    'A7 verify: optional PQ via early return': (False, '\ndef verify(s1, s2, m, raw, strict):\n    k = ec.generate_private_key(ec.SECP256R1()).public_key()\n    q = mldsa.MLDSA65PublicKey.from_public_bytes(raw)\n    k.verify(s1, m, ec.ECDSA(hashes.SHA256()))\n    if not strict:\n        return True\n    q.verify(s2, m)\n    return True\n'),
    'A8 verify: PQ failure swallowed': (False, '\ndef verify(s1, s2, m, raw):\n    k = ec.generate_private_key(ec.SECP256R1()).public_key()\n    q = mldsa.MLDSA65PublicKey.from_public_bytes(raw)\n    try:\n        k.verify(s1, m, ec.ECDSA(hashes.SHA256()))\n        q.verify(s2, m)\n    except Exception:\n        pass\n    return True\n'),
    'A9 combine in dead branch after (while False / if DEBUG)': (False, '\nDEBUG = False\ndef go(peer, ct):\n    k = X25519PrivateKey.generate()\n    m = mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss = m.decapsulate(ct)\n    key = hashlib.sha256(a).digest()\n    if DEBUG:\n        key = hashlib.sha256(a + ss).digest()\n    return key\n'),
    'B1 positive: xwing-style combiner with extra args': (True, '\nclass X:\n    def __init__(self):\n        self.k = X25519PrivateKey.generate()\n        self.m = mlkem.MLKEM768PrivateKey.generate()\n    def dec(self, ct, peer):\n        ss_m = self.m.decapsulate(ct)\n        ss_x = self.k.exchange(peer)\n        return xwing_combiner(ss_m, ss_x, ct, peer)\n'),
    'B2 positive: bytes(a) + ss wrapped': (True, '\ndef go(peer, ct):\n    k = X25519PrivateKey.generate()\n    m = mlkem.MLKEM768PrivateKey.generate()\n    a = k.exchange(peer)\n    ss = m.decapsulate(ct)\n    return hashlib.sha3_256(b"label" + ss + a).digest()\n'),
    'B3 positive: composite sign self attrs': (True, '\nclass S:\n    def __init__(self):\n        self.ec = ec.generate_private_key(ec.SECP256R1())\n        self.pq = mldsa.MLDSA65PrivateKey.generate()\n    def sign(self, m):\n        s1 = self.ec.sign(m, ec.ECDSA(hashes.SHA256()))\n        s2 = self.pq.sign(m)\n        return s1 + s2\n'),
}


@pytest.mark.parametrize("name", sorted(PROBES_R4))
def test_confirmation_probe(name):
    positive, body = PROBES_R4[name]
    res = outcomes(body)
    if positive:
        ops = [r for r in res if r[0] == "operation"]
        assert ops and all(r[2] == "NO_ACTION_HYBRID" for r in ops), (name, res)
    else:
        assert not any(r[2] == "NO_ACTION_HYBRID" for r in res), (name, res)


def test_bare_probes_in_try_are_inventory():
    body = ("def available():\n    try:\n        X25519PrivateKey.generate()\n        ec.generate_private_key(ec.SECP256R1())\n"
            "    except Exception:\n        return False\n    return True\n")
    assert [r[2] for r in outcomes(body)] == ["INVENTORY", "INVENTORY"]


def test_chained_keygen_public_key_verify_roles():
    body = "def v(sig, m):\n    ec.generate_private_key(ec.SECP256R1()).public_key().verify(sig, m, ec.ECDSA(hashes.SHA256()))\n"
    roles = {}
    for ev in analyze_source("p.py", HDR + body):
        if ev.site_kind in ("operation", "key-material"):
            roles[ev.site_kind] = classify(ev).role.value
    assert roles == {"operation": "VERIFY", "key-material": "SIGN"}


def test_if_else_two_families_same_name_no_false_conflict():
    body = ("def mk(use_ec, m, peer):\n    if use_ec:\n        k = ec.generate_private_key(ec.SECP256R1())\n"
            "        return k.sign(m, ec.ECDSA(hashes.SHA256()))\n    else:\n        k = X25519PrivateKey.generate()\n"
            "        return k.exchange(peer)\n")
    got = {}
    for ev in analyze_source("p.py", HDR + body):
        if ev.site_kind == "key-material":
            d = classify(ev)
            got[ev.candidate.api.split(".")[-2]] = (d.role.value, bool(d.conflicts))
    assert got == {"ec": ("SIGN", False), "X25519PrivateKey": ("KEY_ESTABLISHMENT", False)}, got


@pytest.mark.parametrize("text, expected", [
    ("Prefer ML-DSA over ML-KEM for signatures", "SIG"), ("ML-KEM is unnecessary here; use ML-DSA", "SIG"),
    ("ML-KEM should not be delayed: migrate now", "KEM"), ("ML-KEM is not a signature scheme; use ML-DSA", "SIG"),
    ("ML-KEM isn't deprecated; migrate to ML-KEM-768", "KEM"), ("Instead of RSA, use ML-KEM-768", "KEM"),
    ("Use ML-KEM instead of ML-DSA here", "KEM"), ("No ML_KEM; use mldsa65", "SIG"), ("ml kem recommended", "KEM"),
])
def test_confirmation_phrasings(text, expected):
    from pqscan.bench.judge import classify_text
    assert classify_text(text) == expected
