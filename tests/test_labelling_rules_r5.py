"""Owner decisions TA06, TA07, TA11, TA19 (revision v1.0.5-r5, 19 Nov 2026; before any annotation).

TA06 PROTOCOL_CONFIG reserved, limited to supported-library protocol objects. TA07 escaped single-purpose keys: role from
algorithm + resolved key type; a signature-family key of unknown public/private status is UNKNOWN (never SIGN), in all
four arms. TA11 PyCryptodome split idiom: the operation is the site, the constructor is not. TA19 hybrid_component only
for KEY_ESTABLISHMENT, SIGN, VERIFY (schema). Existing pilot and Dataset A labels are unchanged."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from pqscan.pipeline import scan
from pqscan.roles.classifier import ARMS

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "docs/benchmark/benchmark_schema.json").read_text(encoding="utf-8"))
TAX = (ROOT / "docs/specification/role_taxonomy.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "docs/benchmark/annotation_guide.md").read_text(encoding="utf-8")
POLICY_MD = (ROOT / "docs/specification/recommendation_policy.md").read_text(encoding="utf-8")

ESCAPES = '''from Crypto.PublicKey import DSA
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519


def load_dsa(data):
    return DSA.import_key(data)                                   # line 6: status unknown -> UNKNOWN


def new_signing_key():
    return ed25519.Ed25519PrivateKey.generate()                   # line 10: private -> SIGN


def peer_verify_key(raw):
    return ed25519.Ed25519PublicKey.from_public_bytes(raw)        # line 14: public -> VERIFY


def new_kex_key():
    return x25519.X25519PrivateKey.generate()                     # line 18: -> KEY_ESTABLISHMENT
'''

SPLIT = '''from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def seal(pub_pem, message):
    key = RSA.import_key(pub_pem)
    cipher = PKCS1_OAEP.new(key)                                  # line 7: constructor, not a site
    return cipher.encrypt(message)                                # line 8: the operation site
'''


def _sites(tmp_path: Path, name: str, src: str, arm: str) -> dict[int, object]:
    d = tmp_path / arm.replace("+", "_")
    d.mkdir(exist_ok=True)
    (d / name).write_text(src, encoding="utf-8")
    res = scan(d, arm=arm, run_semgrep_rules=False)
    return {f.evidence.candidate.location.line: f for f in res.findings}


# ------------------------------------------------------------------ TA07
@pytest.mark.parametrize("arm", ARMS)
def test_ta07_unknown_direction_never_sign_in_any_arm(tmp_path, arm):
    s = _sites(tmp_path, "escapes.py", ESCAPES, arm)
    d = s[6].decision
    assert d.role.value == "UNKNOWN"
    assert [r.value for r in d.possible_roles] == ["SIGN", "VERIFY", "KEY_MATERIAL_ONLY"]
    assert s[6].recommendation.action == "ABSTAIN"


def test_ta07_established_key_type_gives_the_family_role(tmp_path):
    s = _sites(tmp_path, "escapes.py", ESCAPES, "full")
    assert s[10].decision.role.value == "SIGN"
    assert s[14].decision.role.value == "VERIFY"
    assert s[18].decision.role.value == "KEY_ESTABLISHMENT"


def test_ta07_documents_consistent():
    assert "10. **Escaped keys of single-purpose algorithms (v1.1-r5, owner decision TA07)" in TAX
    assert "**Exception (v1.1-r5, owner decision TA07):**" in TAX
    assert "Never label `SIGN` merely because the status is unknown." in GUIDE
    assert "`possible_roles = [SIGN, VERIFY, KEY_MATERIAL_ONLY]`" in GUIDE


# ------------------------------------------------------------------ TA11
def test_ta11_split_idiom_operation_is_the_site_constructor_is_not(tmp_path):
    s = _sites(tmp_path, "split.py", SPLIT, "full")
    assert 7 not in s
    assert s[8].decision.role.value == "PK_ENCRYPT"
    assert "constructor** on its own" in GUIDE and "the site is `ct = c.encrypt(m)`" in GUIDE


# ------------------------------------------------------------------ TA19
def _rec(**kw):
    base = json.loads((ROOT / "benchmark/synthetic/sites.jsonl").read_text(encoding="utf-8").splitlines()[0])
    base.update(kw)
    return base


@pytest.mark.parametrize("role", ["PK_ENCRYPT", "PK_DECRYPT", "KEY_MATERIAL_ONLY", "UNKNOWN"])
def test_ta19_schema_rejects_hybrid_for_other_roles(role):
    v = Draft202012Validator(SCHEMA)
    assert any("gt_role" in "".join(map(str, e.absolute_path)) or "enum" in e.message or "is not one of" in e.message
               for e in v.iter_errors(_rec(gt_role=role, hybrid_component=True)))


@pytest.mark.parametrize("role", ["KEY_ESTABLISHMENT", "SIGN", "VERIFY"])
def test_ta19_schema_accepts_hybrid_for_matching_roles(role):
    v = Draft202012Validator(SCHEMA)
    errs = [e for e in v.iter_errors(_rec(gt_role=role, hybrid_component=True)) if "hybrid" in e.message or
            ("gt_role" in "".join(map(str, e.absolute_path)) and "is not one of" in e.message)]
    assert not errs
    assert SCHEMA["title"].endswith("(v1.2)")
    assert "`KEY_ESTABLISHMENT`, `SIGN` or `VERIFY` with `hybrid_component = yes`" in POLICY_MD


# ------------------------------------------------------------------ TA06
def test_ta06_protocol_config_reserved_and_out_of_scope_examples_removed():
    row = next(line for line in TAX.splitlines() if line.startswith("| `PROTOCOL_CONFIG`"))
    assert "Reserved (v1.1-r5, owner decision TA06)" in row and "**Not** `ssl.SSLContext` methods" in row
    assert "`ssl.SSLContext.set_ciphers`, `ssl.SSLContext.set_ecdh_curve`, transport KEX" not in row
    g4 = next(line for line in GUIDE.splitlines() if line.startswith("| **PROTOCOL_CONFIG**"))
    assert "of a supported library" in g4 and "out of scope, `eligible = false`" in g4


# ------------------------------------------------------------------ existing labels unchanged
@pytest.mark.parametrize("path", ["benchmark/synthetic/sites.jsonl", "docs/pilot/h1_pilot_sites.csv"])
def test_existing_labels_unchanged_by_r5(path):
    committed = subprocess.run(["git", "show", f"1cdc2d7:{path}"], cwd=ROOT, capture_output=True).stdout
    assert committed.replace(b"\r\n", b"\n") == (ROOT / path).read_bytes().replace(b"\r\n", b"\n")
    synth = [json.loads(x) for x in (ROOT / "benchmark/synthetic/sites.jsonl").read_text(encoding="utf-8").splitlines() if x]
    assert all(not list(Draft202012Validator(SCHEMA).iter_errors(r)) for r in synth)
