"""Pins the policy facts checked against NIST primary sources on 2026-11-17 (docs/final/technical_readiness_report.md,
Phase 2 table). A later policy edit that silently breaks one of them fails here.

Sources (text extracted from the official PDFs):
- NIST IR 8547 (final, October 2026): Sec. 4.1.1 Table 2 (signatures), Table 3 note on ML-DSA-44 and the RBG;
  Sec. 4.1.2 Table 4 (key establishment); Table 5 and the following paragraph (ML-KEM-768 as the default parameter
  set); Sec. 3.2 (hybrids are typically temporary measures).
- FIPS 203 Sec. 3.3, "Approved usage of the shared secret key" (used directly, or via an approved KDF); K-PKE is not
  approved as a stand-alone public-key encryption scheme.
- FIPS 204 Sec. 3.6.1: RBG security strength >= 192 bits for ML-DSA-65; ML-DSA-44 >= 128 bits, and below 192 bits
  the category drops to 1 (IR 8547 Table 3 note).
- SP 800-227 (final, September 2025): Sec. 4.6 (multi-algorithm KEMs and PQ/T hybrids, 4.6.2 approved combiners);
  Sec. 5.2.1 (KEM-DEM public-key encryption).
"""
from pqscan.policy.engine import load_policy

REQUIRED_ROLE_CLASS = {
    "SIGN": "SIG",
    "VERIFY": "SIG",
    "KEY_ESTABLISHMENT": "KEM",
    "PK_ENCRYPT": "KEM_DEM",
    "PK_DECRYPT": "KEM_DEM",
    "KEY_MATERIAL_ONLY": "INVENTORY",
    "PROTOCOL_CONFIG": "PROTOCOL_REVIEW",
    "UNKNOWN": "ABSTAIN",
}


def _data():
    return load_policy().data


def test_role_to_class_mapping_is_the_required_one():
    assert _data()["roles"] == REQUIRED_ROLE_CLASS


def test_signature_class_targets_ml_dsa_with_category_3_default():
    sig = _data()["classes"]["SIG"]
    assert "ML-DSA (FIPS 204)" in sig["target"]
    assert "ML-DSA-65" in sig["parameter_set"]
    # ML-DSA-44 keeps category 2 only with an RBG of >= 192 bits (IR 8547 Table 3 note; FIPS 204 Sec. 3.6.1)
    assert "ML-DSA-44 only with an RBG of >= 192-bit strength" in sig["parameter_set"]
    assert "ML-KEM" not in sig["target"]


def test_kem_classes_use_ml_kem_768_and_kem_dem_is_not_drop_in():
    c = _data()["classes"]
    assert c["KEM"]["parameter_set"].startswith("ML-KEM-768")
    assert c["KEM_DEM"]["parameter_set"].startswith("ML-KEM-768")
    assert "not a drop-in replacement" in c["KEM_DEM"]["target"]
    for cls in ("KEM", "KEM_DEM"):
        assert "ML-DSA" not in c[cls]["target"]


def test_templates_cite_the_verified_ir_8547_tables_and_sections():
    t = _data()["templates"]
    assert "NIST IR 8547 Table 2" in t["SIGN"] and "deprecated after 2030 and disallowed after 2035" in t["SIGN"]
    assert "NIST IR 8547 Table 4" in t["KEY_ESTABLISHMENT"]
    assert "deprecated after 2030 and disallowed after 2035" in t["KEY_ESTABLISHMENT"]
    assert "SP 800-227 Sec. 4.6" in t["KEY_ESTABLISHMENT"]
    for role in ("PK_ENCRYPT", "PK_DECRYPT"):
        assert "FIPS 203 Sec. 3.3" in t[role] and "cannot be preserved" in t[role]
    assert "transitional" in t["HYBRID"]


def test_non_migration_classes_carry_no_target_algorithm():
    c = _data()["classes"]
    for cls in ("INVENTORY", "PROTOCOL_REVIEW", "NO_ACTION_HYBRID", "ABSTAIN"):
        assert c[cls]["family"] == "NONE"
        assert "ML-KEM" not in c[cls]["target"] and "ML-DSA" not in c[cls]["target"]
