"""Tests for the revision 3 statistical functions. Run: .venv/Scripts/python -m pytest docs/proposals/v1.0.4/rev3/scripts -q"""
import math
import numpy as np
import pytest
from scipy.stats import binom, ttest_1samp
from stats_rev3 import (tango_restricted_q, tango_score_z, tango_p_upper, mcnemar_exact_p_upper,
                        cluster_t_p_upper, signflip_p_upper, simulate, decisions)


@pytest.mark.parametrize("b,c,n", [(30, 12, 210), (5, 5, 50), (20, 0, 100), (1, 9, 40)])
def test_tango_reduces_to_mcnemar_at_zero_margin(b, c, n):
    assert math.isclose(float(tango_score_z(b, c, n, 0.0)), (b - c) / math.sqrt(b + c), rel_tol=1e-12)


@pytest.mark.parametrize("b,c,n,d0", [(40, 10, 210, 0.10), (25, 20, 210, 0.05), (60, 2, 210, 0.15), (0, 0, 210, 0.10)])
def test_restricted_mle_solves_score_equation_and_is_valid(b, c, n, d0):
    q = float(tango_restricted_q(b, c, n, d0))
    assert 0 <= q and q + d0 <= 1 and 2 * q + d0 <= 1
    m = n - b - c
    if b and c and m:
        score = b / (q + d0) + c / q - 2 * m / (1 - 2 * q - d0)
        assert abs(score) < 1e-6


def test_tango_size_near_nominal_at_margin_boundary_without_clustering():
    for pd in (0.2, 0.3, 0.4):
        b, c = simulate(0.10, pd, 0.0, K=1, n=210, reps=40000, seed=7)
        rej = (tango_p_upper(b[:, 0], c[:, 0], 210, 0.10) <= 0.025).mean()
        assert rej < 0.035, (pd, rej)                 # nominal 0.025; Monte Carlo SE about 0.0008


def test_exact_mcnemar_matches_binomial_tail():
    assert math.isclose(float(mcnemar_exact_p_upper(30, 12)), binom.sf(29, 42, 0.5))
    assert float(mcnemar_exact_p_upper(0, 0)) == 1.0


def test_cluster_t_matches_scipy():
    d = np.array([0.20, 0.10, 0.15, 0.05, 0.25, 0.12, 0.18])
    ref = ttest_1samp(d, 0.10, alternative="greater").pvalue
    assert math.isclose(float(cluster_t_p_upper(d, 0.10)), ref, rel_tol=1e-10)


def test_signflip_is_exact_and_has_floor_1_over_128():
    d = np.full(7, 0.30)
    assert float(signflip_p_upper(d, 0.10)) == pytest.approx(1 / 128)
    d2 = np.array([0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.0])     # one repository below the margin
    assert float(signflip_p_upper(d2, 0.10)) > 1 / 128


def test_simulation_is_reproducible_and_shapes():
    a = simulate(0.15, 0.3, 0.05, reps=50, seed=1)
    b = simulate(0.15, 0.3, 0.05, reps=50, seed=1)
    assert (a[0] == b[0]).all() and a[0].shape == (50, 7)
    dec = decisions(*a, 30, 0.025)
    assert set(dec) >= {"B_site_tango_margin", "B_cluster_t_margin", "B_cluster_signflip_margin"}
