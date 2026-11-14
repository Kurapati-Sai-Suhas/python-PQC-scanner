"""Modules F and G: judging rules, statistics (cross-checked against scipy/statsmodels), adapters
(regression: the packaged code reproduces the published pilot table) and simple baselines."""
from __future__ import annotations
import collections, csv, math
from pathlib import Path
import pytest
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.proportion import proportion_confint
from pqscan.bench.judge import judge, classify_text, combine_texts, expected_class, our_action
from pqscan.bench.run import judge_external, judge_ours, summarise
from pqscan.bench.stats import wilson, mcnemar_exact, holm, cohen_kappa, cluster_bootstrap, risk_coverage, aurc

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "docs" / "pilot"


def site(role="SIGN", assess="DETERMINATE", eligible="yes", hybrid="no"):
    return {"gt_role": role, "assessability": assess, "eligible": eligible, "hybrid_component": hybrid}


# ---------------------------------------------------------------- judging
@pytest.mark.parametrize("s, action, cls, expected", [
    (site("SIGN"), "RECOMMEND", "SIG", ("CORRECT", "")),
    (site("SIGN"), "RECOMMEND", "KEM", ("INCORRECT", "ROLE_INCOMPATIBLE")),
    (site("KEY_ESTABLISHMENT"), "RECOMMEND", "SIG", ("INCORRECT", "ROLE_INCOMPATIBLE")),
    (site("PK_ENCRYPT"), "RECOMMEND", "KEM", ("CORRECT", "")),
    (site("SIGN"), "RECOMMEND", "DUAL", ("UNDECIDED", "")),
    (site("SIGN"), "RECOMMEND", "PQC_ALREADY", ("INCORRECT", "FALSE_ASSURANCE")),
    (site("SIGN"), "NO_FINDING", "NONE", ("MISSED", "")),
    (site("SIGN"), "FLAG_NO_TARGET", "NONE", ("DETECTED_ONLY", "")),
    (site("SIGN"), "ABSTAIN", "NONE", ("UNASSESSABLE", "")),
    (site("UNKNOWN", "INDETERMINATE"), "ABSTAIN", "NONE", ("CORRECT", "")),
    (site("UNKNOWN", "INDETERMINATE"), "RECOMMEND", "SIG", ("UNJUSTIFIED", "")),
    (site("UNKNOWN", "INDETERMINATE"), "RECOMMEND", "DUAL", ("UNDECIDED", "")),
    (site("KEY_MATERIAL_ONLY"), "FLAG_NO_TARGET", "NONE", ("CORRECT", "")),
    (site("KEY_MATERIAL_ONLY"), "RECOMMEND", "KEM", ("INCORRECT", "OVER_RECOMMENDATION")),
    (site("KEY_ESTABLISHMENT", hybrid="yes"), "RECOMMEND", "PQC_ALREADY", ("CORRECT", "")),
    (site("KEY_ESTABLISHMENT", hybrid="yes"), "RECOMMEND", "KEM", ("INCORRECT", "OVER_RECOMMENDATION")),
    (site("NONE", eligible="no"), "RECOMMEND", "KEM", ("FALSE_POSITIVE_SITE", "")),
    (site("NONE", eligible="no"), "NO_FINDING", "NONE", ("N/A", "")),
    (site("SIGN"), "EXECUTION_FAILURE", "NONE", ("EXECUTION_FAILURE", "")),
])
def test_judgment_table(s, action, cls, expected):
    j = judge(s, action, cls)
    assert (j.judgment, j.harm) == expected


def test_text_classification_and_combination():
    assert classify_text("Shor — migrate to ML-KEM-768") == "KEM"
    assert classify_text("ML-KEM (key establishment) / ML-DSA (signatures)") == "DUAL"
    assert classify_text("Already using PQC — verify algorithm is NIST-approved (ML-KEM, ML-DSA, SLH-DSA)") == "PQC_ALREADY"
    assert combine_texts([]) == ("NO_FINDING", "NONE")
    assert combine_texts(["X25519 (key-agreement)"]) == ("FLAG_NO_TARGET", "NONE")
    assert combine_texts(["migrate to ML-KEM-768", "migrate to ML-DSA-65"]) == ("RECOMMEND", "DUAL")
    assert combine_texts(["Already using PQC", "Migrate to ML-DSA"]) == ("RECOMMEND", "SIG")
    assert our_action("KEM_DEM", "RECOMMEND") == ("RECOMMEND", "KEM")
    assert our_action("ABSTAIN", "ABSTAIN") == ("ABSTAIN", "NONE")


# ---------------------------------------------------------------- statistics
@pytest.mark.parametrize("k,n", [(16, 30), (0, 30), (30, 30), (6, 29)])
def test_wilson_matches_statsmodels(k, n):
    lo, hi = wilson(k, n)
    elo, ehi = proportion_confint(k, n, method="wilson")
    assert math.isclose(lo, elo, abs_tol=1e-9) and math.isclose(hi, ehi, abs_tol=1e-9)


@pytest.mark.parametrize("b,c", [(10, 2), (5, 5), (0, 7), (12, 30)])
def test_mcnemar_matches_statsmodels(b, c):
    expected = mcnemar([[20, b], [c, 20]], exact=True).pvalue
    assert math.isclose(mcnemar_exact(b, c), expected, rel_tol=1e-9)


def test_holm_matches_statsmodels():
    p = [0.01, 0.04, 0.03, 0.2, 0.005]
    assert all(math.isclose(a, b) for a, b in zip(holm(p), multipletests(p, method="holm")[1]))


def test_cohen_kappa_known_value():
    a = ["S"] * 20 + ["V"] * 10 + ["K"] * 10
    b = ["S"] * 18 + ["V"] * 2 + ["V"] * 8 + ["S"] * 2 + ["K"] * 10
    # po = 36/40; pe = (20*20 + 10*10 + 10*10)/1600 = 0.375 -> kappa = (0.9-0.375)/(0.625) = 0.84
    assert math.isclose(cohen_kappa(a, b), 0.84, abs_tol=1e-9)


def test_cluster_bootstrap_is_deterministic_and_brackets_point():
    units = [{"y": int(i % 3 == 0)} for i in range(60)]
    clusters = [i // 10 for i in range(60)]
    stat = lambda u: sum(x["y"] for x in u) / len(u)  # noqa: E731
    a = cluster_bootstrap(units, clusters, stat, n_boot=300)
    assert a == cluster_bootstrap(units, clusters, stat, n_boot=300)
    assert a[1] <= a[0] <= a[2]


def test_risk_coverage_and_aurc():
    scored = [(3, False), (3, False), (2, True), (2, False), (1, True)]
    pts = risk_coverage(scored)
    assert pts == [(0.4, 0.0), (0.8, 0.25), (1.0, 0.4)]
    assert math.isclose(aurc(pts), 0.4 * 0.125 + 0.2 * 0.325)


# ---------------------------------------------------------------- adapters: regression against the pilot
def test_packaged_adapters_reproduce_published_pilot_table():
    sites = list(csv.DictReader(open(PILOT / "h1_pilot_sites.csv", encoding="utf-8")))
    published = {}
    for r in csv.DictReader(open(PILOT / "h1_pilot_joined.csv", encoding="utf-8")):
        published[(r["tool"], r["site_id"])] = (r["judgment"], r["harm_category"])
    for tool in ("pqcheck", "pqc-audit", "PostQuant", "qsafe", "QSA-regex"):
        rows = judge_external(sites, PILOT / "raw_tool_outputs", tool)
        got = {(tool, r["site_id"]): (r["judgment"], r["harm_category"]) for r in rows}
        diff = {k: (published[k], v) for k, v in got.items() if published[k] != v}
        assert not diff, f"{tool}: packaged judging differs from the pilot table: {diff}"


# ---------------------------------------------------------------- simple baselines and pqscan arms on the fixture project
def test_simple_baselines_on_fixture_sites(tmp_path):
    proj = ROOT / "tests" / "fixtures"
    lines = (proj / "project/app/keys.py").read_text(encoding="utf-8").splitlines()
    ln = lambda needle: next(i for i, l in enumerate(lines, 1) if needle in l)  # noqa: E731
    rows = [
        {"site_id": "F1", "repo": "project", "file": "app/keys.py", "line_start": ln("self.key.sign("), "line_end": ln("self.key.sign("),
         "gt_role": "SIGN", "assessability": "DETERMINATE", "eligible": "yes", "hybrid_component": "no"},
        {"site_id": "F2", "repo": "project", "file": "app/keys.py", "line_start": ln("ec.generate_private_key("), "line_end": ln("ec.generate_private_key("),
         "gt_role": "KEY_ESTABLISHMENT", "assessability": "DETERMINATE", "eligible": "yes", "hybrid_component": "no"},
    ]
    rows = [{k: str(v) for k, v in r.items()} for r in rows]
    out = {(r["method"], r["site_id"]): r for r in judge_ours(rows, proj)}
    # algorithm mapping: RSA -> KEM is role-incompatible for a signing site; EC -> SIG is wrong for ECDH
    assert out[("pqscan:B1-algorithm", "F1")]["judgment"] == "INCORRECT"
    assert out[("pqscan:B1-algorithm", "F2")]["judgment"] == "INCORRECT"
    assert out[("pqscan:B1-dual", "F1")]["judgment"] == "UNDECIDED"
    assert out[("pqscan:B3-full-noabst", "F2")]["judgment"] == "CORRECT"
    assert out[("pqscan:B4-full-T2", "F1")]["judgment"] == "CORRECT"
    assert "pqscan:B4-full-T2" in summarise(list(out.values()))


# ---------------------------------------------------------------- review findings 6, 7, 8, 13
def test_reported_abstention_on_ineligible_site_is_a_false_positive():
    assert judge(site("NONE", eligible="no"), "ABSTAIN", "NONE").judgment == "FALSE_POSITIVE_SITE"
    assert judge(site("NONE", eligible="no"), "NO_FINDING", "NONE").judgment == "N/A"


def test_dropin_wording_ignores_negations_and_applies_to_pqscan_text():
    from pqscan.bench.judge import dropin_wording
    from pqscan.policy import load_policy
    from pqscan.roles.classifier import RoleDecision
    from pqscan.models import Role, Tier
    assert dropin_wording("Replace RSA with ML-KEM-768") and dropin_wording("ML-KEM is a drop-in replacement")
    assert not dropin_wording("RSA-OAEP has no drop-in replacement; redesign as KEM + AEAD")
    assert not dropin_wording("ML-KEM is not a drop-in replacement for encrypt()")
    r = load_policy().apply(RoleDecision("operation", Role.PK_ENCRYPT, Tier.T3, "RSA", "t"))
    assert not dropin_wording(f"{r.target} {r.rationale}")


def test_negated_target_mentions_are_not_counted():
    assert classify_text("Do not use ML-KEM for signatures; migrate to ML-DSA") == "SIG"


def test_parse_failure_is_execution_failure_in_the_benchmark(tmp_path):
    (tmp_path / "r").mkdir()
    (tmp_path / "r" / "bad.py").write_text("from cryptography.hazmat.primitives.asymmetric import rsa\ndef f(:\n", encoding="utf-8")
    s = {"site_id": "X", "repo": "r", "file": "bad.py", "line_start": "1", "line_end": "3", "gt_role": "SIGN",
         "assessability": "DETERMINATE", "eligible": "yes", "hybrid_component": "no"}
    rows = judge_ours([s], tmp_path, arms=("B4-full-T2",))
    assert rows[0]["judgment"] == "EXECUTION_FAILURE"


def test_best_hit_follows_the_labelled_method(tmp_path):
    (tmp_path / "r").mkdir()
    (tmp_path / "r" / "m.py").write_text(
        "from cryptography.hazmat.primitives.asymmetric import ec\nfrom cryptography.hazmat.primitives import hashes\n"
        "def f(m, peer):\n    k = ec.generate_private_key(ec.SECP256R1()); s = k.sign(m, ec.ECDSA(hashes.SHA256()))\n    return s\n",
        encoding="utf-8")
    s = {"site_id": "Y", "repo": "r", "file": "m.py", "line_start": "4", "line_end": "4", "gt_role": "SIGN", "method": "sign",
         "assessability": "DETERMINATE", "eligible": "yes", "hybrid_component": "no"}
    rows = judge_ours([s], tmp_path, arms=("B3-full-noabst",))
    assert rows[0]["judgment"] == "CORRECT" and rows[0]["rec_class"] == "SIG"



def test_negation_removes_only_the_negated_token():
    assert classify_text("No ML-KEM equivalent exists for signatures, migrate to ML-DSA") == "SIG"
    assert classify_text("Use not ML-KEM but ML-DSA for signing") == "SIG"
    assert classify_text("migrate to ML-KEM-768") == "KEM"



# ---------------------------------------------------------------- baseline execution failures (before Experiment A)
ERRFIX = Path(__file__).parent / "fixtures" / "baseline_errors"


def _err_sites():
    from pqscan.bench.fileprobe import file_condition
    rows = []
    for name in ("good.py", "syntax_error.py", "latin1.py", "nullbyte.py"):
        rows.append({"site_id": name, "repo": "errrepo", "file": name, "line_start": "4", "line_end": "4", "method": "generate_private_key",
                     "gt_role": "SIGN", "assessability": "DETERMINATE", "eligible": "yes", "hybrid_component": "no"})
    assert [file_condition(ERRFIX / "repos/errrepo" / r["file"]) for r in rows] == ["ok", "syntax-error", "non-utf8", "null-byte"]
    return rows


@pytest.mark.parametrize("tool, failed", [
    ("pqcheck", {"syntax_error.py", "nullbyte.py"}),
    ("pqc-audit", {"syntax_error.py", "nullbyte.py"}),
    ("PostQuant", set()),
    ("qsafe", set()),
    ("QSA-regex", {"nullbyte.py"}),
    ("pqblocks-scan", {"good.py", "syntax_error.py", "latin1.py", "nullbyte.py"}),   # whole run aborted, no report
])
def test_external_tool_failures_are_execution_failures_not_misses(tool, failed):
    rows = {r["site_id"]: r for r in judge_external(_err_sites(), ERRFIX / "outputs", tool, ERRFIX / "repos")}
    got = {k for k, r in rows.items() if r["judgment"] == "EXECUTION_FAILURE"}
    assert got == failed, (tool, got)
    assert not any(r["judgment"] == "MISSED" for r in rows.values()), "a failed file was counted as a miss"


def test_pqblocks_error_log_is_parsed():
    from pqscan.bench.run import logged_failures
    got = logged_failures(ERRFIX / "outputs", "pqblocks-scan", "errrepo")
    assert {g.split("/")[-1] for g in got} == {"nullbyte.py", "syntax_error.py"}


def test_execution_failures_do_not_change_rates_of_executed_sites():
    """Adding failed sites must leave correctness/harm rates over executed sites unchanged."""
    s = _err_sites()
    base = judge_external(s[:1], ERRFIX / "outputs", "pqcheck", ERRFIX / "repos")
    more = judge_external(s, ERRFIX / "outputs", "pqcheck", ERRFIX / "repos")
    def rates(rows):
        ex = [r for r in rows if r["judgment"] != "EXECUTION_FAILURE"]
        return len(ex), sum(r["judgment"] == "CORRECT" for r in ex) / len(ex), sum(r["judgment"] == "INCORRECT" for r in ex) / len(ex)
    assert rates(base)[1:] == rates([r for r in more if r["site_id"] in ("good.py", "latin1.py")])[1:]
    table = summarise(more)
    assert "| pqcheck | 4 | 2 | 2 |" in table   # n=4, two execution failures, n_exec=2



def test_strict_scoring_only_changes_family_correct_dropin_rows():
    from pqscan.bench.judge import strict_judgment, Judgment
    assert strict_judgment(Judgment("CORRECT"), True) == Judgment("INCORRECT", "UNSUPPORTED_DROP_IN")
    assert strict_judgment(Judgment("CORRECT"), False) == Judgment("CORRECT")
    assert strict_judgment(Judgment("INCORRECT", "ROLE_INCOMPATIBLE"), True) == Judgment("INCORRECT", "ROLE_INCOMPATIBLE")
    from pqscan.bench.run import _row
    r = _row({"site_id": "Z", "repo": "r", "gt_role": "PK_ENCRYPT", "assessability": "DETERMINATE", "eligible": "yes",
              "hybrid_component": "no"}, "tool", "RECOMMEND", "KEM", "", "Replace RSA with ML-KEM", dropin=True)
    assert (r["judgment"], r["judgment_strict"], r["harm_category_strict"]) == ("CORRECT", "INCORRECT", "UNSUPPORTED_DROP_IN")
