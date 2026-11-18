"""F05: the F-A Type I error simulation tests the unchanged procedure (one-sided exact McNemar + Holm), places every
configuration on the null boundary, and is reproducible from its seeds."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

from pqscan.bench import stats as ST

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("fa_type1", ROOT / "scripts" / "fa_type1_simulation.py")
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)


def test_vectorised_p_value_equals_the_production_function():
    rng = np.random.default_rng(1)
    b, c = rng.integers(0, 40, 500), rng.integers(0, 40, 500)
    b[:5] = c[:5] = 0
    got = FA.p_one_sided(b, c)
    want = np.array([ST.mcnemar_exact_one_sided(int(x), int(y)) for x, y in zip(b, c)])
    assert np.allclose(got, want, rtol=0, atol=1e-12)


def test_vectorised_holm_equals_the_production_function():
    rng = np.random.default_rng(2)
    p = rng.random((300, 8)) ** 3
    rej = FA.holm_reject(p)
    for row, r in zip(p, rej):
        adj = ST.holm(list(row))
        assert list(r) == [a <= FA.ALPHA for a in adj]


def test_every_single_configuration_is_on_the_null_boundary():
    for spec in FA.SINGLE.values():
        frames, m, fail = FA.build(spec)
        e = FA.design_expectation(frames, m, fail)
        smin = min(mh * (1 - fh) / sum(f) for f, mh, fh in zip(frames, m, fail))
        assert -smin < e <= 1e-12
        assert all(mh <= sum(f) for f, mh in zip(frames, m))               # sampling without replacement is valid


def test_family_null_baselines_are_exactly_balanced():
    rng = np.random.default_rng(FA.seed_int("t"))
    mask = [False] * 4 + [True] * 4
    for X, Y, _ in FA.family_frames(rng, mask, 0.2, 0.6, 0.75):
        for j, is_null in enumerate(mask):
            B, C = int(np.sum(X & ~Y[j])), int(np.sum(~X & Y[j]))
            assert (B == C) if is_null else (B > C)


def test_runs_are_reproducible_from_the_seed_rule():
    spec = FA.SINGLE["S3-stratum-heterogeneous"]
    assert FA.simulate_single(spec, 300, "x") == FA.simulate_single(spec, 300, "x")
    assert FA.seed_int("S1-homogeneous") == int.from_bytes(
        __import__("hashlib").sha256(b"20261113:fa-type1:S1-homogeneous").digest()[:8], "big")
    a = FA.simulate_family([True] * 8, 50, "y")
    assert a == FA.simulate_family([True] * 8, 50, "y")
