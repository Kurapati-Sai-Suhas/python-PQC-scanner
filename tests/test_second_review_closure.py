"""Second isolated AI specification review (protocol v1.0.5), findings G01, G04, G07, G08, G09, G10, G11: the editorial
corrections are present and consistent with the code. G05/G06 are covered by tests/test_g05_g06_forbidden_gate.py.
G02 and G03 are open owner decisions and are deliberately not asserted as closed here."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest

from pqscan.baselines.adapters import ADAPTERS
from pqscan.baselines.simple import ARMS, H2_ARMS
from pqscan.bench import annotate as AN
from pqscan.bench import candidates as C
from pqscan.bench import guard_diagnostics as GD
from pqscan.bench import h2 as H
from pqscan.policy import load_policy

ROOT = Path(__file__).resolve().parents[1]
GUIDE = (ROOT / "docs/benchmark/annotation_guide.md").read_text(encoding="utf-8")
TAX = (ROOT / "docs/specification/role_taxonomy.md").read_text(encoding="utf-8")
PROTO = (ROOT / "docs/specification/evaluation_protocol.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs/specification/phase3_analysis_plan.md").read_text(encoding="utf-8")
SPEC = json.loads((ROOT / "docs/specification/run_specification_pre_f1.json").read_text(encoding="utf-8"))
YAML = (ROOT / "pqscan/policy/policy_v1_1.yaml").read_text(encoding="utf-8")


# ------------------------------------------------------------------ G01
def test_g01_protocol_config_branch_is_defined_and_scored():
    step_c = GUIDE[GUIDE.index("**Step C"):GUIDE.index("**Step D")]
    assert "Protocol configuration (r2, G01)" in step_c and "`PROTOCOL_CONFIG`, `eligible = true`" in step_c
    assert "out-of-scope library (Step A): `eligible = false`" in step_c
    multi = GUIDE[GUIDE.index("**Multi-call candidate statement"):GUIDE.index("**Step B")]
    assert "3. a **protocol-configuration** call" in multi and "4. if several calls qualify" in multi
    assert "configures a protocol object of that supported library" in TAX
    assert load_policy().data["roles"]["PROTOCOL_CONFIG"] == "PROTOCOL_REVIEW"     # scored as protocol review


# ------------------------------------------------------------------ G04, G07
def test_g04_batch_run_versus_manual_use_is_explicit_in_guide_and_protocol():
    assert "The only permitted execution is the prescribed one: the frozen batch run" in GUIDE
    assert "This prescribed run is the only execution of any method on the test split before F2" in PROTO


def test_g07_h3_interpretation_note_next_to_the_hypotheses():
    note = PROTO[PROTO.index("**H3 interpretation note"):PROTO.index("## 2. Datasets")]
    assert "**matched coverage**" in note and "**natural-coverage**" in note and "B3-full-noabst" in note
    assert "H3: at coverage ≥ 70%, the harmful rate of the τ = T2 policy is lower than" in PROTO   # wording kept


# ------------------------------------------------------------------ G08
def test_g08_inventory_matches_the_code_registry():
    inv = SPEC["interpretations"]["H-6 (H4)"]["tool_inventory_G08"]
    assert set(inv["runnable_external_tools"]) == set(ADAPTERS)
    assert set(inv["runnable_pqscan_arms"]) == {f"pqscan:{a}" for a in set(ARMS) | set(H2_ARMS)}
    assert inv["proposed_analyser"] in inv["runnable_pqscan_arms"]
    assert set(inv["not_runnable"]) == {"CBOMkit (sonar-cryptography)", "Mehl ESEM 2026 scanner"}
    # owner decision G08 (19 Nov 2026): the F-A baseline set (was "PENDING OWNER DECISION" in r2)
    assert inv["decision_set_part1"] == SPEC["families"]["F-A"]["baselines"]


# ------------------------------------------------------------------ G09
def test_g09_yaml_comment_says_colocation_is_only_a_candidate_condition():
    assert "only a CANDIDATE condition" in YAML and "co-location alone never yields NO_ACTION_HYBRID" in YAML
    probes = (ROOT / "tests/test_hybrid_review3.py").read_text(encoding="utf-8")
    assert "'N2 same fn, both computed, not combined': (False" in probes          # the behavioural test stays


# ------------------------------------------------------------------ G10
def _res(rf, rm, n):
    return {"R_f": rf, "R_m": rm, "n_common": n}


def test_g10_diagnostics_are_descriptive_and_agree_with_the_signed_gap():
    rs = [_res(20, 10, 30), _res(5, 15, 30), _res(12, 12, 24), _res(0, 0, 0)]
    d = GD.diagnostics(rs)
    assert d["signed_mean"] == H.coverage_gap(rs) and d["K_e"] == 3 and d["descriptive_only"] is True
    assert d["mean_absolute"] == (Fraction(10, 30) + Fraction(10, 30) + 0) / 3
    assert d["minimum"] == Fraction(-10, 30) and d["opposite_direction_repositories"] == 1
    # cancellation lowers the signed gap: the guard can only switch on, never off
    assert H.guard_active(H.coverage_gap(rs)) and not H.guard_active(H.coverage_gap(rs[:1]))
    assert GD.diagnostics([_res(0, 0, 0)])["K_e"] == 0


def test_g10_rationale_and_limitation_recorded_without_changing_the_rule():
    sec = PLAN[PLAN.index("### 7.2 Coverage-gap guard"):PLAN.index("### 7.3")]
    assert "the guard is active iff **g < 1/10**" in sec and "**signed** coverage advantage" in sec
    assert "never change the guard or p" in sec and "The pre-specified signed rule stands." in sec


# ------------------------------------------------------------------ G11
def _repo(tmp: Path) -> tuple[Path, Path]:
    repo = tmp / "repo"
    repo.mkdir()
    (repo / "m.py").write_text("from cryptography.hazmat.primitives.asymmetric import rsa\n"
                               "k = rsa.generate_private_key(public_exponent=65537, key_size=2048)\n", encoding="utf-8")
    run = tmp / "run"
    run.mkdir()
    return repo, run


def test_g11_build_writes_attribution_outside_the_order_folder(tmp_path):
    repo, run = _repo(tmp_path)
    out = tmp_path / "benchmark" / "candidates" / "development"
    assert C.main(["build", "--repo", str(repo), "--name", "demo", "--commit", "abc", "--run-dir", str(run),
                   "--out", str(out)]) == 0
    assert not list(out.glob("pool_sources_*"))
    assert (tmp_path / "benchmark" / "restricted" / "pool_sources" / "development" / "pool_sources_demo.json").exists()
    with pytest.raises(C.SamplerError, match="G11"):
        C.main(["build", "--repo", str(repo), "--name", "demo", "--commit", "abc", "--run-dir", str(run),
                "--out", str(out), "--sources-out", str(out / "sub")])


def test_g11_issue_refuses_while_attribution_sits_in_a_candidate_or_annotation_folder(tmp_path):
    root = tmp_path
    cand = root / "benchmark" / "candidates" / "development"
    cand.mkdir(parents=True)
    (cand / "pool_sources_x.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="tool-attribution"):
        AN._attribution_isolated(root, root / "benchmark" / "annotation" / "DV" / "x")
    (cand / "pool_sources_x.json").unlink()
    AN._attribution_isolated(root, root / "benchmark" / "annotation" / "DV" / "x")      # clean: no error
    with pytest.raises(SystemExit, match="tool-attribution"):
        AN.main(["issue", "--phase", "pilot", "--repo", "paramiko"], root=_with_stray(root))


def _with_stray(root: Path) -> Path:
    w = root / "benchmark" / "annotation" / "pilot" / "paramiko"
    w.mkdir(parents=True, exist_ok=True)
    (w / "pool_sources_paramiko.json").write_text("{}", encoding="utf-8")
    return root


def test_g11_real_repository_keeps_attribution_out_of_tracked_and_packet_paths():
    assert not list((ROOT / "benchmark" / "candidates").rglob("pool_sources_*.json"))
    import subprocess
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
    assert "pool_sources_" not in tracked and "benchmark/restricted" not in tracked
    attest = (ROOT / "docs/audit/source_attribution_access_attestation_TEMPLATE.md").read_text(encoding="utf-8")
    assert "self-attested" in attest and "not technically enforced" in attest
