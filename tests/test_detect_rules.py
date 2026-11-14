"""Module A rule tests: every `# expect:` marker in the fixtures must be matched by exactly the
listed rules, and no finding may appear on a line without a marker (strict precision and recall
at line level)."""
from __future__ import annotations
import re
from collections import defaultdict
from pathlib import Path
import pytest
from pqscan.detect import run_semgrep, RULES_DIR

FIXTURES = Path(__file__).parent / "fixtures" / "semgrep"
EXPECT = re.compile(r"#\s*expect:\s*(.+?)\s*$")


def expected_markers() -> dict[tuple[str, int], set[str]]:
    exp: dict[tuple[str, int], set[str]] = {}
    for f in sorted(FIXTURES.glob("*.py")):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            m = EXPECT.search(line)
            if m:
                exp[(f.name, i)] = {r.strip() for r in m.group(1).split(",")}
    return exp


@pytest.fixture(scope="module")
def findings():
    cands = run_semgrep(FIXTURES, RULES_DIR)
    found: dict[tuple[str, int], set[str]] = defaultdict(set)
    for c in cands:
        found[(c.location.file, c.location.line)].add(c.rule_id)
    return found, cands


def test_rule_files_load():
    assert {p.name for p in RULES_DIR.glob("*.yaml")} == {"pyca.yaml", "pycryptodome.yaml", "common.yaml"}


def test_every_expected_line_is_found(findings):
    found, _ = findings
    missing = {k: v for k, v in expected_markers().items() if not v <= found.get(k, set())}
    assert not missing, f"expected rules not found (recall): {missing}"


def test_no_unexpected_findings(findings):
    found, _ = findings
    exp = expected_markers()
    unexpected = {k: v - exp.get(k, set()) for k, v in found.items() if v - exp.get(k, set())}
    assert not unexpected, f"findings on lines without a marker, or extra rules (precision): {unexpected}"


def test_candidate_metadata_populated(findings):
    _, cands = findings
    assert cands, "no candidates at all"
    for c in cands:
        assert c.rule_id.startswith("pqscan."), c
        assert c.coverage_row, c
        assert c.snippet and "-----BEGIN" not in c.snippet
        assert c.location.line >= 1 and c.location.col >= 1


def test_import_gate_blocks_unrelated_sign(findings):
    found, _ = findings
    assert not any(f == "no_crypto_import.py" for (f, _l) in found), "method candidates leaked into a file with no crypto import"


def test_deterministic_order():
    a = run_semgrep(FIXTURES, RULES_DIR)
    b = run_semgrep(FIXTURES, RULES_DIR)
    assert [(c.location, c.rule_id) for c in a] == [(c.location, c.rule_id) for c in b]


def test_default_targets_are_the_confined_walk_and_include_tests(tmp_path):
    from pqscan.detect import run_semgrep_report
    (tmp_path / "tests").mkdir()
    src = "from cryptography.hazmat.primitives.asymmetric import rsa\nk = rsa.generate_private_key(65537, 2048)\n"
    (tmp_path / "tests" / "test_k.py").write_text(src, encoding="utf-8")
    (tmp_path / "app.py").write_text(src, encoding="utf-8")
    cands, errors = run_semgrep_report(tmp_path)
    assert {c.location.file for c in cands} == {"app.py", "tests/test_k.py"} and errors == []
    cands, _ = run_semgrep_report(tmp_path, include_tests=False)
    assert {c.location.file for c in cands} == {"app.py"}


def test_targets_outside_root_are_ignored(tmp_path):
    from pqscan.detect import run_semgrep_report
    root = tmp_path / "root"; root.mkdir()
    other = tmp_path / "other.py"
    other.write_text("from cryptography.hazmat.primitives.asymmetric import rsa\nk = rsa.generate_private_key(65537, 2048)\n")
    cands, _ = run_semgrep_report(root, targets=[other])
    assert cands == []


def test_semgrep_failure_is_raised_as_semgrep_error(tmp_path):
    from pqscan.detect import run_semgrep_report, SemgrepError
    (tmp_path / "a.py").write_text("x = 1\n")
    bad = tmp_path / "rules"; bad.mkdir()
    (bad / "bad.yaml").write_text("rules:\n  - id: broken\n    languages: [python]\n")
    with pytest.raises(SemgrepError):
        run_semgrep_report(tmp_path, rules_dir=bad)
    with pytest.raises(SemgrepError):
        run_semgrep_report(tmp_path / "missing")


def test_rel_or_redacted():
    from pathlib import Path
    from pqscan.detect.runner import _rel_or_redacted
    root = Path(__file__).resolve().parent
    assert _rel_or_redacted(str(root / "x.py"), root) == "x.py"
    assert _rel_or_redacted(str(root.parent / "y.py"), root) == "<outside scan root>"
    assert _rel_or_redacted("", root) == ""
