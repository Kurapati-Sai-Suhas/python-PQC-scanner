"""Statistical methods for protocol v1.0.4 revision 4 (PROPOSED, NOT ADOPTED; not production code).

Data structure. For every primary-set eligible test site i in repository r there is a PAIR of binary outcomes:
X_i = 1 if the provenance-aware arm is CORRECT, Y_i = 1 if the comparator arm is CORRECT, both scored with the frozen
scoring policy after coverage matching (R4_03). Site-level discordant counts: b (X=1, Y=0), c (X=0, Y=1).

Estimand (R4_02): delta = mean over the 7 repositories of delta_r, delta_r = P_r(X=1) - P_r(Y=1), where P_r is the
distribution over the repository's primary-set eligible sites (a finite population sampled at random by the seeded
sampler). With equal quotas (30 per repository) the repository-balanced and site-weighted estimates coincide.

Tests implemented
- mcnemar_exact_p_upper(b, c): H0 delta <= 0 vs delta > 0, exact conditional binomial on pooled site-level counts.
- tango_p_upper(b, c, n, d0): H0 delta <= d0 vs delta > d0, Tango (1998)/Nam (1997) score test on pooled site-level
  counts. Applied to SITE-LEVEL paired binary outcomes only (never to repository aggregates).
- repo_t_p_upper(delta_r, d0): one-sample t test on the 7 repository differences (superpopulation-oriented).
- signflip_p_upper(delta_r, d0): exact sign-flip randomization test on repository differences.
- wilcoxon_exact_p_upper(delta_r, d0): exact Wilcoxon signed-rank on repository differences (own enumeration).
- holm_adjust(p): Holm step-down adjusted p-values.
"""
from __future__ import annotations
import itertools, math
import numpy as np
from scipy.stats import binom, norm, t as tdist

# ------------------------------------------------------------------ site-level (pooled) paired tests
def tango_q(b, c, n, d0):
    """Restricted MLE of p21 under p12 = p21 + d0: root of 2n q^2 + B q + C = 0 (closed form)."""
    b, c, n = (np.asarray(x, float) for x in (b, c, n))
    A = 2 * n
    B = -b - c + (2 * n - b + c) * d0
    C = -c * d0 * (1 - d0)
    return (-B + np.sqrt(B * B - 4 * A * C)) / (2 * A)


def tango_z(b, c, n, d0):
    b, c, n = (np.asarray(x, float) for x in (b, c, n))
    v = n * (2 * tango_q(b, c, n, d0) + d0 * (1 - d0))
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (b - c - n * d0) / np.sqrt(v)
    return np.where(v > 0, z, np.where(b - c - n * d0 > 0, np.inf, -np.inf))


def tango_p_upper(b, c, n, d0):
    return norm.sf(tango_z(b, c, n, d0))


def mcnemar_exact_p_upper(b, c):
    b, c = np.asarray(b), np.asarray(c)
    D = b + c
    return np.where(D > 0, binom.sf(b - 1, D, 0.5), 1.0)


# ------------------------------------------------------------------ repository-level tests
def repo_t_p_upper(delta_r, d0):
    d = np.asarray(delta_r, float)
    K = d.shape[-1]
    m, s = d.mean(-1), d.std(-1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        tt = (m - d0) / (s / math.sqrt(K))
    return np.where(s > 0, tdist.sf(tt, K - 1), np.where(m > d0, 0.0, 1.0))


_SIGNS: dict[int, np.ndarray] = {}


def _signs(K):
    if K not in _SIGNS:
        _SIGNS[K] = np.array(list(itertools.product((1.0, -1.0), repeat=K)))
    return _SIGNS[K]


def signflip_p_upper(delta_r, d0):
    d = np.asarray(delta_r, float) - d0
    S = _signs(d.shape[-1])
    obs = d.mean(-1)
    return ((d[..., None, :] * S).mean(-1) >= obs[..., None] - 1e-12).mean(-1)


def wilcoxon_exact_p_upper(delta_r, d0):
    """Exact one-sided Wilcoxon signed-rank (zeros dropped; average ranks for ties) by full sign enumeration."""
    d = np.atleast_2d(np.asarray(delta_r, float) - d0)
    out = np.empty(d.shape[0])
    for i, row in enumerate(d):
        x = row[np.abs(row) > 1e-12]
        if x.size == 0:
            out[i] = 1.0
            continue
        from scipy.stats import rankdata
        rk = rankdata(np.abs(x))
        w_obs = rk[x > 0].sum()
        S = _signs(x.size)
        w_all = ((S > 0) * rk).sum(-1)
        out[i] = (w_all >= w_obs - 1e-12).mean()
    return out if np.ndim(delta_r) > 1 else out[0]


# ------------------------------------------------------------------ multiplicity
def holm_adjust(p):
    p = np.asarray(p, float)
    m = p.size
    order = np.argsort(p, kind="stable")
    adj = np.empty(m)
    running = 0.0
    for k, idx in enumerate(order):
        running = max(running, min(1.0, (m - k) * p[idx]))
        adj[idx] = running
    return adj


# ------------------------------------------------------------------ data generation
def fixed_heterogeneity(delta, tau, pd, kind="normal", K=7):
    """Repository effects held FIXED across replicates (finite-population / conditional estimand).
    'normal': delta + tau * standardized normal quantiles; 'skewed': six equal repositories and one outlier.
    Values are clipped to [-pd, pd]; the returned mean is the actual estimand after clipping."""
    if kind == "normal":
        z = norm.ppf((np.arange(1, K + 1) - 0.5) / K)
    elif kind == "skewed":
        z = np.array([-1.0] * (K - 1) + [K - 1.0])
    else:
        raise ValueError(kind)
    z = (z - z.mean()) / (z.std(ddof=0) if z.std(ddof=0) > 0 else 1)
    dr = np.clip(delta + tau * z, -pd, pd)
    return dr, float(dr.mean())


def draw_pairs(delta_r, pd, n, rng):
    """Site-level paired outcomes per repository. delta_r has shape (reps, K): one row of repository effects per
    replicate. A site is discordant w.p. pd; a discordant site favours the first arm w.p. (pd + delta_r) / (2 pd).
    Returns b, c with shape (reps, K)."""
    delta_r = np.asarray(delta_r, float)
    D = rng.binomial(n, pd, delta_r.shape)
    b = rng.binomial(D, (pd + delta_r) / (2 * pd))
    return b, D - b


def all_tests(b, c, n, d0):
    """One-sided p-values of every candidate test for H0: delta <= d0, per replicate (rows of b, c)."""
    B, C = b.sum(-1), c.sum(-1)
    N = n * b.shape[-1]
    dr = (b - c) / n
    return {
        "site_exact_mcnemar": mcnemar_exact_p_upper(B, C) if d0 == 0 else np.full(B.shape, np.nan),
        "site_tango": tango_p_upper(B, C, N, d0),
        "repo_t": repo_t_p_upper(dr, d0),
        "repo_signflip": signflip_p_upper(dr, d0),
        "repo_wilcoxon": wilcoxon_exact_p_upper(dr, d0),
    }
