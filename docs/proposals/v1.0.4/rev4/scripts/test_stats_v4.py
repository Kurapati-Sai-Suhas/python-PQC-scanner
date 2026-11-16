"""Unit tests, independent cross-checks and simulation tests for stats_v4 (PROPOSED rev4).
Run from the project root: .venv/Scripts/python -m pytest -q -o addopts="" docs/proposals/v1.0.4/rev4/scripts"""
import itertools, math
import numpy as np
import pytest
from scipy.optimize import minimize_scalar
from scipy.stats import binomtest, ttest_1samp, wilcoxon
from statsmodels.stats.multitest import multipletests
import stats_v4 as S


# ---------------------------------------------------------------- independent cross-checks
@pytest.mark.parametrize("b,c,n,d0", [(40, 10, 210, 0.10), (25, 20, 210, 0.05), (60, 3, 210, 0.15), (12, 30, 210, 0.10), (5, 1, 60, 0.10)])
def test_restricted_mle_matches_numerical_optimiser(b, c, n, d0):
    m = n - b - c
    nll = lambda q: -(b * math.log(q + d0) + c * math.log(q) + m * math.log(1 - 2 * q - d0))  # noqa: E731
    hi = (1 - d0) / 2 - 1e-12
    res = minimize_scalar(nll, bounds=(1e-12, hi), method="bounded", options={"xatol": 1e-12})
    assert float(S.tango_q(b, c, n, d0)) == pytest.approx(res.x, abs=1e-7)


@pytest.mark.parametrize("b,c,n", [(30, 12, 210), (5, 5, 50), (20, 1, 100)])
def test_tango_at_zero_margin_equals_mcnemar_z(b, c, n):
    assert float(S.tango_z(b, c, n, 0.0)) == pytest.approx((b - c) / math.sqrt(b + c), rel=1e-12)


@pytest.mark.parametrize("b,c", [(30, 12), (7, 7), (0, 5), (9, 0)])
def test_exact_mcnemar_matches_scipy_binomtest(b, c):
    ref = binomtest(b, b + c, 0.5, alternative="greater").pvalue
    assert float(S.mcnemar_exact_p_upper(b, c)) == pytest.approx(ref, rel=1e-12)


def test_repo_t_matches_scipy():
    d = np.array([0.20, 0.10, 0.15, 0.05, 0.25, 0.12, 0.18])
    for d0 in (0.0, 0.10):
        assert float(S.repo_t_p_upper(d, d0)) == pytest.approx(ttest_1samp(d, d0, alternative="greater").pvalue, rel=1e-10)


def test_wilcoxon_matches_scipy_exact():
    d = np.array([0.20, 0.10, 0.15, 0.05, 0.25, 0.12, -0.18])
    ref = wilcoxon(d, alternative="greater", method="exact").pvalue
    assert float(S.wilcoxon_exact_p_upper(d, 0.0)) == pytest.approx(ref, rel=1e-10)


def test_signflip_matches_bruteforce_loop():
    d = np.array([0.30, -0.10, 0.20, 0.05, 0.12, 0.00, 0.40])
    obs = (d - 0.10).mean()
    cnt = sum((np.array(s) * (d - 0.10)).mean() >= obs - 1e-12 for s in itertools.product((1, -1), repeat=7))
    assert float(S.signflip_p_upper(d, 0.10)) == pytest.approx(cnt / 128)
    assert float(S.signflip_p_upper(np.full(7, 0.5), 0.10)) == pytest.approx(1 / 128)


def test_holm_matches_statsmodels():
    p = np.array([0.004, 0.030, 0.012, 0.0009])
    assert np.allclose(S.holm_adjust(p), multipletests(p, method="holm")[1])


def test_margin_pvalue_never_below_zero_margin_pvalue():
    """Holm's step-down therefore never rejects H2-margin before H2-pos (same data)."""
    rng = np.random.default_rng(3)
    for _ in range(500):
        b, c = rng.integers(0, 60, 2)
        n = 210
        if b + c == 0:
            continue
        assert float(S.tango_p_upper(b, c, n, 0.10)) >= float(S.tango_p_upper(b, c, n, 0.0)) - 1e-12
        d = rng.normal(0.1, 0.1, 7)
        assert float(S.repo_t_p_upper(d, 0.10)) >= float(S.repo_t_p_upper(d, 0.0)) - 1e-12


# ---------------------------------------------------------------- simulation tests (size and power)
@pytest.mark.parametrize("pd", [0.2, 0.3, 0.4])
@pytest.mark.parametrize("kind,tau", [("normal", 0.0), ("normal", 0.10), ("skewed", 0.10)])
def test_site_tests_hold_size_for_fixed_repositories(pd, kind, tau):
    """Conditional (fixed-repository) estimand: pooled exact McNemar at delta=0 and pooled Tango at delta=0.10
    must not exceed nominal 0.025 by more than Monte Carlo error."""
    rng = np.random.default_rng(11)
    for d0 in (0.0, 0.10):
        dr, mean = S.fixed_heterogeneity(d0, tau, pd, kind)
        if abs(mean - d0) > 1e-9:
            continue                                    # clipping moved the estimand; covered in the full grid
        b, c = S.draw_pairs(np.tile(dr, (8000, 1)), pd, 30, rng)
        p = S.mcnemar_exact_p_upper(b.sum(1), c.sum(1)) if d0 == 0 else S.tango_p_upper(b.sum(1), c.sum(1), 210, d0)
        assert (p <= 0.025).mean() <= 0.025 + 3 * math.sqrt(0.025 * 0.975 / 8000)


def test_power_increases_with_effect():
    rng = np.random.default_rng(5)
    pw = []
    for delta in (0.10, 0.15, 0.20, 0.25):
        dr, _ = S.fixed_heterogeneity(delta, 0.0, 0.3)
        b, c = S.draw_pairs(np.tile(dr, (3000, 1)), 0.3, 30, rng)
        pw.append((S.tango_p_upper(b.sum(1), c.sum(1), 210, 0.10) <= 0.025).mean())
    assert pw == sorted(pw) and pw[0] < 0.05 and pw[-1] > 0.7
