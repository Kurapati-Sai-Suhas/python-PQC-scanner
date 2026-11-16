"""Statistical methods proposed in protocol v1.0.4 revision 3 (PROPOSED; not production code).

Paired binary outcome per eligible site: X = 1 if the provenance-aware ("full") arm is correct, Y = 1 if the
method+argument arm is correct. Discordant counts: b = #(X=1, Y=0), c = #(X=0, Y=1).
Site-weighted estimand: delta = P(X=1) - P(Y=1) = p12 - p21, estimated by (b - c) / n.

Functions
---------
tango_score_z / tango_p_upper : score test of H0: delta <= d0 vs H1: delta > d0 for paired proportions
    (Tango 1998, Stat Med 17:891-908; Nam 1997, Biometrics 53:1422-1430). The restricted MLE of p21 under
    p12 = p21 + d0 solves 2n q^2 + B q + C = 0 with B = -b - c + (2n - b + c) d0, C = -c d0 (1 - d0)
    (derived from the multinomial likelihood b log(q + d0) + c log q + m log(1 - 2q - d0)).
    For d0 = 0 the statistic equals the McNemar z = (b - c) / sqrt(b + c).
mcnemar_exact_p_upper : exact conditional one-sided McNemar p for H0: delta <= 0.
cluster_t_p_upper     : repository-level one-sample t test of mean(delta_r) <= d0 (df = K - 1).
signflip_p_upper      : exact sign-flip randomization test on repository-level (delta_r - d0).
"""
from __future__ import annotations
import itertools, math
import numpy as np
from scipy.stats import binom, norm, t as tdist


def tango_restricted_q(b, c, n, d0):
    b, c, n = np.asarray(b, float), np.asarray(c, float), np.asarray(n, float)
    A = 2 * n
    B = -b - c + (2 * n - b + c) * d0
    C = -c * d0 * (1 - d0)
    return (-B + np.sqrt(B * B - 4 * A * C)) / (2 * A)


def tango_score_z(b, c, n, d0):
    b, c, n = np.asarray(b, float), np.asarray(c, float), np.asarray(n, float)
    q = tango_restricted_q(b, c, n, d0)
    var = n * (2 * q + d0 * (1 - d0))
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (b - c - n * d0) / np.sqrt(var)
    return np.where(var > 0, z, 0.0)


def tango_p_upper(b, c, n, d0):
    return norm.sf(tango_score_z(b, c, n, d0))


def mcnemar_exact_p_upper(b, c):
    b, c = np.asarray(b), np.asarray(c)
    D = b + c
    return np.where(D > 0, binom.sf(b - 1, D, 0.5), 1.0)


def cluster_t_p_upper(delta_r, d0):
    """delta_r: array (..., K) of repository-level differences."""
    d = np.asarray(delta_r, float)
    K = d.shape[-1]
    m, s = d.mean(-1), d.std(-1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        tt = (m - d0) / (s / math.sqrt(K))
    p = tdist.sf(tt, K - 1)
    return np.where(s > 0, p, np.where(m > d0, 0.0, 1.0))


_SIGNS: dict[int, np.ndarray] = {}


def signflip_p_upper(delta_r, d0):
    """Exact one-sided sign-flip test of mean(delta_r - d0) <= 0 over all 2^K sign patterns."""
    d = np.asarray(delta_r, float) - d0
    K = d.shape[-1]
    if K not in _SIGNS:
        _SIGNS[K] = np.array(list(itertools.product((1, -1), repeat=K)), float)
    S = _SIGNS[K]                                  # (2^K, K)
    obs = d.mean(-1)
    flipped = (d[..., None, :] * S).mean(-1)       # (..., 2^K)
    return (flipped >= obs[..., None] - 1e-12).mean(-1)


def simulate(delta, pd, tau, K=7, n=30, reps=4000, seed=20261113):
    """Repository-clustered paired outcomes. Repository r has true difference delta_r = delta + u_r,
    u_r ~ N(0, tau^2), clipped to [-pd, pd]; each site is discordant with probability pd; a discordant site
    favours the full arm with probability (pd + delta_r) / (2 pd). Returns b, c arrays of shape (reps, K)."""
    rng = np.random.default_rng(seed)
    dr = np.clip(delta + rng.normal(0, tau, (reps, K)) if tau > 0 else np.full((reps, K), delta), -pd, pd)
    D = rng.binomial(n, pd, (reps, K))
    b = rng.binomial(D, (pd + dr) / (2 * pd))
    return b, D - b


def decisions(b, c, n_r, alpha, d0=0.10):
    """Rejection indicators per replicate for every analysis option (one-sided level alpha)."""
    B, C = b.sum(-1), c.sum(-1)
    N = n_r * b.shape[-1]
    delta_r = (b - c) / n_r
    obs = (B - C) / N
    return {
        # Option A: positive difference, plus an observed >= 10 pp criterion
        "A_site_mcnemar_pos": mcnemar_exact_p_upper(B, C) <= alpha,
        "A_site_mcnemar_pos_and_obs10": (mcnemar_exact_p_upper(B, C) <= alpha) & (obs >= d0),
        "A_cluster_t_pos_and_obs10": (cluster_t_p_upper(delta_r, 0.0) <= alpha) & (obs >= d0),
        # fixed-sequence step 1 on its own: repository-level positive difference
        "S1_cluster_t_pos": cluster_t_p_upper(delta_r, 0.0) <= alpha,
        # Option B: literal margin delta > 0.10
        "B_site_tango_margin": tango_p_upper(B, C, N, d0) <= alpha,
        "B_cluster_t_margin": cluster_t_p_upper(delta_r, d0) <= alpha,
        "B_cluster_signflip_margin": signflip_p_upper(delta_r, d0) <= alpha,
    }
