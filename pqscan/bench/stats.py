"""Statistics for the evaluation protocol (Sec. 5). Pure functions, no plotting."""
from __future__ import annotations
import math, random
from collections import defaultdict
from typing import Callable, Hashable, Sequence
from scipy import stats as sps


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for k successes of n (95% by default)."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value from the discordant counts b (A right, B wrong) and c."""
    n = b + c
    if n == 0:
        return 1.0
    return float(min(1.0, 2 * sps.binom.cdf(min(b, c), n, 0.5)))


def holm(pvalues: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values (same order as input)."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvalues[i])
        adj[i] = min(1.0, running)
    return adj


def cohen_kappa(a: Sequence[Hashable], b: Sequence[Hashable]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("two equal-length, non-empty label sequences are required")
    n = len(a)
    cats = set(a) | set(b)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((list(a).count(c) / n) * (list(b).count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def cluster_bootstrap(units: Sequence[dict], clusters: Sequence[Hashable], statistic: Callable[[list[dict]], float],
                      n_boot: int = 1000, seed: int = 20261113, alpha: float = 0.05) -> tuple[float, float, float]:
    """Percentile bootstrap CI resampling whole clusters (repository or synthetic base case).
    Returns (point estimate, lower, upper)."""
    groups: dict[Hashable, list[dict]] = defaultdict(list)
    for u, c in zip(units, clusters):
        groups[c].append(u)
    keys = sorted(groups, key=str)
    rng = random.Random(seed)
    point = statistic(list(units))
    vals = []
    for _ in range(n_boot):
        sample = [u for k in (rng.choice(keys) for _ in keys) for u in groups[k]]
        v = statistic(sample)
        if not math.isnan(v):
            vals.append(v)
    if not vals:
        return (point, math.nan, math.nan)
    vals.sort()
    lo = vals[int((alpha / 2) * (len(vals) - 1))]
    hi = vals[int((1 - alpha / 2) * (len(vals) - 1))]
    return (point, lo, hi)


def risk_coverage(scored: Sequence[tuple[int, bool]]) -> list[tuple[float, float]]:
    """`scored` = (evidence rank, harmful?) for every eligible site the method would recommend at
    the most permissive threshold. Sweeping the threshold from strict to permissive gives points
    (coverage, risk), where coverage = recommended / eligible and risk = harmful / recommended."""
    n = len(scored)
    pts = []
    for thr in sorted({r for r, _ in scored}, reverse=True):
        rec = [h for r, h in scored if r >= thr]
        pts.append((len(rec) / n, sum(rec) / len(rec)))
    return pts


def aurc(points: Sequence[tuple[float, float]]) -> float:
    """Area under the risk-coverage curve (trapezoid over coverage, starting at the first point)."""
    pts = sorted(points)
    if len(pts) < 2:
        return pts[0][1] * pts[0][0] if pts else math.nan
    return sum((c2 - c1) * (r1 + r2) / 2 for (c1, r1), (c2, r2) in zip(pts, pts[1:]))
