"""Experiment E infrastructure (revision v1.0.5-r6): H1 (TA08), H3 (TA03, TA28), H4 (TA04, TA05), the E driver (TA17,
TA22) and its freeze gates. Fixture, synthetic-dev and development data only: no test repository, no synthetic
holdout instance and no label is created or read for evaluation."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest

from pqscan.bench import experiment_e as E
from pqscan.bench import h1, h3, h4_analysis
from pqscan.bench.h4 import PART1_BASELINES, PROPOSED_ANALYSER

ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------------------------------------------------------ H1 (TA08)
def _lab(i, obvious, elig=True, assess="DETERMINATE", ev="none"):
    return {"site_id": f"s{i}", "eligible": elig, "obvious_from_name": obvious if elig else None,
            "assessability": assess, "evidence_needed": ev}


def test_h1a_numerator_is_obvious_false_including_indeterminate():
    labs = [_lab(1, False, assess="INDETERMINATE", ev="key-provenance"), _lab(2, True), _lab(3, True), _lab(4, True),
            _lab(5, None, elig=False)]
    r = h1.h1a(labs)
    assert r["primary"]["k"] == 1 and r["primary"]["n"] == 4      # the ineligible site is ignored
    assert r["status"] == "MET"                                     # exactly 0.25 meets ">= 0.25"
    assert r["sensitivity_excluding_indeterminate"]["k"] == 0 and r["sensitivity_excluding_indeterminate"]["n"] == 3
    assert r["evidence_needed_in_numerator"] == {"key-provenance": 1}
    assert len(r["primary"]["wilson95"]) == 2


def test_h1a_below_threshold_and_validation():
    assert h1.h1a([_lab(1, False)] + [_lab(i, True) for i in range(2, 6)])["status"] == "NOT MET"  # 1/5 < 1/4
    assert h1.h1a([])["status"] == "NOT ESTIMABLE"
    with pytest.raises(ValueError):
        h1.h1a([{"site_id": "x", "eligible": True, "obvious_from_name": None, "assessability": "DETERMINATE"}])


def _row(tool, sid, judgment, harm="", elig=True):
    return {"method": tool, "site_id": sid, "eligible": elig, "judgment": judgment, "harm_category": harm}


def test_h1b_rate_failures_and_assessability():
    rows = []
    for t in h1.H1B_SET:
        rows += [_row(t, "a", "INCORRECT", "FALSE_ASSURANCE"), _row(t, "b", "CORRECT"), _row(t, "c", "UNDECIDED"),
                 _row(t, "d", "EXECUTION_FAILURE"), _row(t, "e", "INCORRECT", "", elig=True),
                 _row(t, "f", "UNJUSTIFIED", elig=False)]
    r = h1.h1b(rows)
    one = r["tools"]["pqcheck"]
    assert (one["k"], one["n"], one["execution_failures"]) == (2, 4, 1)   # harmful + UNDECIDED; ineligible ignored
    assert r["status"] == "MET"
    assert h1.h1b([x for x in rows if x["method"] != "qsafe"])["status"] == "NOT ASSESSABLE"


# ----------------------------------------------------------------------------------------------------- H3 (TA03, TA28)
def _sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def _h3_repo(repo, n, harm_t2=(), harm_ar=(), t3=()):
    return [{"site_id": f"{repo}-{i}", "t2_rec": True, "t2_tier": "T3" if i in t3 else "T2",
             "t2_harm": i in harm_t2, "ar_rec": True, "ar_harm": i in harm_ar} for i in range(n)]


def test_h3_t2_withdrawal_follows_frozen_order():
    sites = {"r1": _h3_repo("r1", 10, harm_t2=range(10), t3=(0,))}
    rep = h3._Repo("r1", sites["r1"])
    res = rep.at(Fraction(7, 10))
    assert res["K"] == 7 and res["H_T2"] == 7            # every T2 recommendation harmful: kept count = K
    # the withdrawn three are the T2-tier sites with the smallest SHA-256 keys; the T3 site is never withdrawn first
    order = sorted(range(10), key=lambda i: _sha(f"20261113|H3-T2|r1|r1-{i}"))     # all ten are T2-tier here
    s2 = {"r1": _h3_repo("r1", 10, harm_t2=set(order[:3]))}
    assert h3._Repo("r1", s2["r1"]).at(Fraction(7, 10))["H_T2"] == 0                 # the harmful three are withdrawn
    s3 = {"r1": _h3_repo("r1", 10, harm_t2={order[3]})}
    assert h3._Repo("r1", s3["r1"]).at(Fraction(7, 10))["H_T2"] == 1                 # the fourth is kept
    # tier first: a T3 site with the smallest key is kept while T2 sites are withdrawn
    s4 = {"r1": _h3_repo("r1", 10, harm_t2={order[0]}, t3={order[0]})}
    assert h3._Repo("r1", s4["r1"]).at(Fraction(7, 10))["H_T2"] == 1


def test_h3_random_withholding_uses_the_seed_strings():
    sites = _h3_repo("r1", 10, harm_ar=(3,))
    rep = h3._Repo("r1", sites)
    res = rep.at(Fraction(7, 10))
    exp = [int(3 in sorted(range(10), key=lambda i: _sha(f"{s}|H3-withhold|r1|r1-{i}"))[:7]) for s in h3.WITHHOLD_SEEDS]
    assert res["H_rand"].tolist() == exp


def test_h3_decision_estimability_and_reporting():
    good = {r: _h3_repo(r, 20, harm_ar=range(0, 20, 4)) for r in ("r1", "r2")}
    out = h3.analyse(good, B=30)
    assert out["status"] == "MET"                           # T2 never harmful, AR harmful on 5/20
    pt = out["points"]["7/10"]
    t = pt["always_recommend_reporting_TA03"]
    assert t["coverage_AR_natural"] == 1.0 and t["coverage_T2_at_c"] == pytest.approx(0.7)
    assert t["per_recommendation_risk_AR"] == pytest.approx(0.25)
    assert pt["bootstrap_TA28"]["B"] == 30 and pt["bootstrap_TA28"]["seed"] == 20261113
    assert h3.analyse(good, B=30)["points"]["7/10"]["bootstrap_TA28"] == pt["bootstrap_TA28"]   # deterministic
    # C1: a repository with n_r = 0 makes every point NOT ESTIMABLE (never dropped)
    assert h3.analyse(dict(good, r3=[]), B=5)["status"] == "NOT ASSESSABLE"
    # C1: R_T2 < K in one repository
    short = dict(good, r3=[dict(s, t2_rec=(i < 5)) for i, s in enumerate(_h3_repo("r3", 10))])
    o = h3.analyse(short, B=5)
    assert o["status"] == "NOT ASSESSABLE" and not o["points"]["7/10"]["estimable"]


# -------------------------------------------------------------------------------------------------- H4 (TA04, TA05)
def _h4_sites(bases):
    out = []
    for b in bases:
        out.append({"base_case": b, "transformation": "identity", "site_id": f"{b}.identity", "eligible": True})
        for o in h4_analysis.OPERATORS:
            out.append({"base_case": b, "transformation": o, "site_id": f"{b}.{o}", "eligible": True})
    return out


def _outcomes(sites, flip_ops=(), fail=()):
    res = {}
    for s in sites:
        o = s["transformation"]
        rec = ("EXECUTION_FAILURE", "NONE") if s["site_id"] in fail else \
            (("ABSTAIN", "NONE") if o in flip_ops else ("RECOMMEND", "SIG"))
        res[s["site_id"]] = {"cls": "SIGN", "rec": rec}
    return res


def test_h4_part1_per_tool_and_one_operator_descriptive():
    bases = [f"b{i}" for i in range(10)]
    sites = _h4_sites(bases)
    split = {b: ("synthetic-dev" if i < 5 else "synthetic-holdout") for i, b in enumerate(bases)}
    tools = {j: _outcomes(sites, flip_ops=("loaded-key",) if k % 2 else ("cross-function",))
             for k, j in enumerate(PART1_BASELINES)}
    tools[PROPOSED_ANALYSER] = _outcomes(sites)
    r = h4_analysis.analyse(sites, tools, split)
    assert r["part1"]["status"] == "MET"                             # per tool: each has some operator
    one = r["part1"]["one_operator_for_all_eight_TA04_descriptive"]
    assert one["loaded-key"] is False and one["cross-function"] is False   # no single operator for all eight
    assert r["part2"]["primary_holdout_TA05"]["status"] == "MET"
    assert r["part2"]["primary_holdout_TA05"]["by_operator"]["alias-import"]["invariant_share"]["n"] == 5
    assert r["part2"]["all_pairs"]["by_operator"]["alias-import"]["invariant_share"]["n"] == 10


def test_h4_failures_excluded_and_missing_tool():
    bases = ["b0", "b1"]
    sites = _h4_sites(bases)
    t = _outcomes(sites, fail=("b0.alias-import",))
    f = h4_analysis.flips(h4_analysis.pairs(sites), t, "alias-import")
    assert f["execution_failure_pairs"] == 1 and f["FR_cls"]["n"] == 1
    r = h4_analysis.analyse(sites, {PROPOSED_ANALYSER: t}, {b: "synthetic-dev" for b in bases})
    assert r["part1"]["status"] == "NOT ASSESSABLE"
    assert r["part2"]["primary_holdout_TA05"]["status"] == "NOT ESTIMABLE"     # no holdout pairs supplied


# ----------------------------------------------------------------------------------------------- driver (TA17, gates)
def test_gate_refuses_test_split_without_f1_f2():
    assert not (ROOT / E.F1_RECORD).exists()
    with pytest.raises(E.GateError):
        E.check_gate("test")
    with pytest.raises(E.GateError):
        E.check_gate("holdout")
    E.check_gate("development")


def test_ta17_exactly_seven_test_repositories():
    repos = E.test_repositories()
    assert len(repos) == 7
    E.assert_seven(repos)
    with pytest.raises(E.GateError):
        E.assert_seven(repos[:6])
    with pytest.raises(E.GateError):
        E.assert_seven(repos[:6] + ["paramiko/paramiko"])


def test_h4_refuses_synthetic_holdout_before_f1():
    with pytest.raises(E.GateError):
        E.analyse_h4(sites=[], outcomes_by_tool={}, use_holdout=True)


def test_fa_baselines_are_the_registered_eight():
    assert tuple(E.fa_baselines()) == PART1_BASELINES


@pytest.fixture(scope="module")
def dev_run():
    """Development smoke run on synthetic-dev instances only (holdout base cases filtered out before any read of
    their files). Pseudo-repositories = library. Not evidence of anything; it exercises the pipeline."""
    from pqscan.baselines.simple import ARMS, H2_ARMS
    from pqscan.bench.run import judge_ours
    split = json.loads((ROOT / "benchmark/synthetic/manifest.json").read_text(encoding="utf-8"))["split"]
    dev = [s for s in map(json.loads, (ROOT / "benchmark/synthetic/sites.jsonl").read_text(encoding="utf-8").splitlines())
           if split.get(s["base_case"]) == "synthetic-dev" and s["library"] in ("pyca", "pycryptodome")]
    rows = judge_ours(dev, ROOT / "benchmark", arms=tuple(dict.fromkeys(ARMS + H2_ARMS)))
    for r in rows:
        r["repo"] = "dev-" + next(s["library"] for s in dev if s["site_id"] == r["site_id"])
    finals = [{"site": dict(s, repo="dev-" + s["library"]), "meta": {"unresolved": ["gt_role"] if i % 9 == 0 else []}}
              for i, s in enumerate(dev)]
    return dev, E.analyse(split="synthetic-dev", rows=rows, finals=finals, B=200, h3_B=20, mc_rule=False)


def test_dev_run_uses_no_holdout_and_produces_every_section(dev_run):
    dev, res = dev_run
    split = json.loads((ROOT / "benchmark/synthetic/manifest.json").read_text(encoding="utf-8"))["split"]
    assert {split[s["base_case"]] for s in dev} == {"synthetic-dev"}
    assert res["K"] == 2 and res["repositories"] == ["dev-pyca", "dev-pycryptodome"]
    p = res["primary"]
    assert set(p) == {"F-A", "F-B", "H1a", "H1b", "H3"}
    assert {c: p["F-B"][c]["K"] for c in ("H2-1", "H2-3", "H2-4")} == {"H2-1": 2, "H2-3": 2, "H2-4": 2}
    # F-A: the six external tools have no development results here; the two pqscan baselines are compared
    assert set(p["F-A"]["comparisons"]) == {"pqscan:B1-algorithm", "pqscan:B2-method-args"}
    assert p["H1b"]["status"] == "NOT ASSESSABLE"
    assert set(res["sensitivities_TA22"]) == set(E.SENSITIVITY_VARIANTS)
    # consensus without AI records is empty: repositories stay (K unchanged), nothing is estimable
    cons = res["sensitivities_TA22"]["consensus"]
    assert cons["F-B"]["H2-1"]["K"] == 2 and cons["F-B"]["H2-1"]["K_e"] == 0
    assert cons["H3"]["status"] == "NOT ASSESSABLE"


def test_cli_refuses_test_split(tmp_path):
    import subprocess
    import sys
    (tmp_path / "e.jsonl").write_text("", encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "scripts/run_experiment_e.py"), "--split", "test", "--rows",
                        str(tmp_path / "e.jsonl"), "--finals", str(tmp_path / "e.jsonl")], capture_output=True, text=True)
    assert r.returncode == 2 and "REFUSED" in r.stderr
